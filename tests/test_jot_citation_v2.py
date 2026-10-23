"""Version-two provenance regressions; no live evaluator calls."""

import copy
import json
import unittest
from unittest.mock import patch

import jot_agent
import test_jot_agent as legacy
from test_jot_agent import _response, _resign


def id_response(request_id, source_id=0):
    response = _response(request_id)
    response['takeaways'][0]['evidence'] = [{'source_id': source_id}]
    response['worth_watching'][0]['evidence'] = [{'source_id': source_id}]
    return response


class CitationV2Tests(unittest.TestCase):
    write_packet = legacy.AgentWorkflowTests.write_packet
    publish = legacy.AgentWorkflowTests.publish
    rejected = legacy.AgentWorkflowTests.rejected
    change_source = legacy.AgentWorkflowTests.change_source

    def setUp(self):
        legacy.AgentWorkflowTests.setUp(self)
        self.packet = json.loads(self.request_path.read_text(encoding='utf-8'))
        self.response = id_response(self.packet['request_id'])

    def test_preparation_declares_id_only_protocol(self):
        self.assertEqual(self.packet['version'], 2)
        citation = self.packet['response_schema']['$defs']['Citation']
        self.assertEqual(citation['required'], ['source_id'])
        self.assertEqual(set(citation['properties']), {'source_id'})

    def test_render_resolves_source_without_mutating_raw_response(self):
        original = copy.deepcopy(self.response)
        markdown, html = self.publish()
        self.assertIn('&t=4)', markdown.read_text())
        self.assertIn('data-start="4"', html.read_text())
        self.assertEqual(self.response, original)
        self.assertEqual(json.loads(self.response_path.read_text()), original)
        jot_agent._validate(self.packet, self.response)
        self.assertEqual(self.response, original)

    def test_adjacent_incident_timestamps_and_duplicate_quotes_remain_distinct(self):
        self.change_source('[31:47] repeated quote\n[31:49] repeated quote\n[31:49] distinct quote', duration=2000)
        for source_id, seconds in ((0, 1907), (1, 1909), (2, 1909)):
            with self.subTest(source_id=source_id):
                self.response = id_response(self.packet['request_id'], source_id)
                self.response['worth_watching'] = []
                markdown, _ = self.publish()
                self.assertIn(f'&t={seconds})', markdown.read_text())

    def test_unknown_negative_boolean_and_noninteger_ids_fail_without_outputs(self):
        for source_id, reason in (
            (999, r'^Evidence validation:.*unknown_or_invalid_source_id'),
            (-1, r'^Response schema:.*source_id: constraint=minimum;'),
            (True, r'^Response schema:.*source_id: constraint=type;'),
            (False, r'^Response schema:.*source_id: constraint=type;'),
            # JSON Schema accepts integral floats; the strict identity guard does not.
            (0.0, r'^Evidence validation:.*unknown_or_invalid_source_id'),
            (0.5, r'^Response schema:.*source_id: constraint=type;'),
            ('0', r'^Response schema:.*source_id: constraint=type;'),
            (None, r'^Response schema:.*source_id: constraint=type;'),
        ):
            with self.subTest(source_id=source_id):
                self.response = id_response(self.packet['request_id'], source_id)
                self.rejected(reason)

    def test_old_pairs_and_extra_citation_fields_fail(self):
        for citation in ({'timestamp': 4, 'quote': 'Cache invalidation'},
                         {'source_id': 0, 'timestamp': 12}, {'source_id': 0, 'quote': 'private'}):
            with self.subTest(citation=citation):
                self.response['takeaways'][0]['evidence'] = [citation]
                self.rejected('Response')

    def test_derived_range_membership_is_start_inclusive_end_exclusive(self):
        self.response['worth_watching'][0]['evidence'] = [{'source_id': 1}]
        self.rejected('Evidence.*range')
        self.response['worth_watching'][0].update(start=12, end=20)
        self.publish()

    def test_untimed_prelude_is_not_assigned_next_timestamp(self):
        self.change_source('Genuinely untimed prelude.\n[00:04] Timed speech.')
        self.response = id_response(self.packet['request_id'])
        self.response['worth_watching'] = []
        markdown, html = self.publish()
        report = markdown.read_text().split('## What you can learn')[1].split('## Novelty')[0]
        self.assertNotIn('&t=', report)
        self.response['worth_watching'] = [{'start': 0, 'end': 8, 'reason': 'test', 'evidence': [{'source_id': 0}]}]
        self.output = self.directory / 'rejected-prelude'
        self.rejected('Evidence.*range')

    def test_empty_sections_and_unobserved_evidence_remain_valid(self):
        self.response['takeaways'] = []
        self.response['worth_watching'] = []
        self.publish()

    def test_evidence_errors_aggregate_without_private_text(self):
        self.response['takeaways'][0]['evidence'] = [{'source_id': 999}]
        self.response['signal']['substance'].update(rating='high', evidence=[{'source_id': 998}])
        self.response['worth_watching'][0]['evidence'] = [{'source_id': 1}]
        with self.assertRaises(ValueError) as raised:
            self.publish()
        diagnostic = str(raised.exception)
        self.assertIn('Evidence', diagnostic)
        self.assertIn('failures=3', diagnostic)
        self.assertIn('takeaways[0]', diagnostic)
        self.assertIn('signal.substance', diagnostic)
        self.assertNotIn('Cache invalidation', diagnostic)
        self.assertFalse(self.output.exists())

    def test_forged_lookup_and_wrong_version_schema_are_rejected(self):
        original = copy.deepcopy(self.packet)
        self.packet['citation_lookup'] = [{'source_id': 0, 'timestamp': 12, 'quote': 'forged'}]
        _resign(self.packet)
        self.rejected('exactly')
        self.packet = original
        self.packet['version'] = 1
        _resign(self.packet)
        self.rejected('packaged trusted schema')

    def test_catalog_preserves_physical_lines_whitespace_and_duplicate_entries(self):
        transcript = '  préface  \r\n[00:04]  repeated  \rcontinued\n\n[00:04]  repeated  '
        self.assertEqual(jot_agent._source_catalog(transcript, 20), [
            {'source_id': 0, 'timestamp': None, 'quote': '  préface  '},
            {'source_id': 1, 'timestamp': 4, 'quote': '  repeated  '},
            {'source_id': 2, 'timestamp': 4, 'quote': 'continued'},
            {'source_id': 3, 'timestamp': 4, 'quote': '  repeated  '},
        ])

    def test_untimed_source_supports_ids_but_no_ranges(self):
        self.change_source('Untimed first line.\nUntimed second line.', duration=None)
        self.response = id_response(self.packet['request_id'], 1)
        self.response['worth_watching'] = []
        markdown, html = self.publish()
        self.assertNotIn('&t=', html.read_text())
        self.response['worth_watching'] = [{'start': 0, 'end': 8, 'reason': 'test', 'evidence': [{'source_id': 1}]}]
        self.output = self.directory / 'rejected-untimed'
        self.rejected('cannot invent timestamp ranges')

    def test_v2_trust_and_digest_cannot_be_bypassed(self):
        original = copy.deepcopy(self.packet)
        for field, value in (('rubric', 'private malicious rubric'),
                             ('response_schema', {}), ('version', True), ('version', 2.0)):
            with self.subTest(field=field):
                self.packet = copy.deepcopy(original)
                self.packet[field] = value
                _resign(self.packet)
                self.response['request_id'] = self.packet['request_id']
                self.rejected('packaged trusted|version must')
        self.packet = original
        self.response['request_id'] = original['request_id']
        self.packet['viewer_background'] = 'modified'
        self.rejected('digest mismatch')

    def test_schema_numeric_boolean_equality_does_not_bypass_trust(self):
        self.packet['response_schema']['$defs']['Citation']['properties']['source_id']['minimum'] = False
        _resign(self.packet)
        self.response['request_id'] = self.packet['request_id']
        self.rejected('packaged trusted schema')

    def test_required_evidence_is_not_replaced_by_a_report_wide_quota(self):
        self.response['takeaways'][0]['evidence'] = []
        self.rejected('Response schema')
        self.response = id_response(self.packet['request_id'])
        self.response['signal']['substance']['rating'] = 'high'
        self.rejected('signal.substance.evidence')

    def test_schema_diagnostics_do_not_echo_attacker_values_or_keys(self):
        private = 'private source, skill path, authentication diagnostic'
        self.response['verdict']['decision'] = private
        self.response['takeaways'][0]['evidence'][0][private] = private
        with self.assertRaises(ValueError) as raised:
            self.publish()
        self.assertIn('Response schema', str(raised.exception))
        self.assertNotIn(private, str(raised.exception))
        self.assertFalse(self.output.exists())

    def test_evaluation_sends_derived_lookup_and_preserves_raw_ids(self):
        captured = {}
        def evaluate(packet, instructions, **kwargs):
            captured.update(packet)
            return id_response(packet['request_id'])
        with patch('jot_evaluator.invoke_evaluator', side_effect=evaluate) as invoke:
            jot_agent.evaluate_transcript(self.source, output_dir=self.output, evaluator='codex')
        invoke.assert_called_once()
        self.assertEqual(captured['citation_lookup'], [
            {'source_id': 0, 'timestamp': 4, 'quote': ' Cache invalidation needs explicit ownership.'},
            {'source_id': 1, 'timestamp': 12, 'quote': ' A second distinct source segment.'},
        ])
        responses = list(self.output.glob('*.response.json'))
        self.assertEqual(len(responses), 1)
        raw = json.loads(responses[0].read_text())
        self.assertEqual(raw['takeaways'][0]['evidence'], [{'source_id': 0}])
