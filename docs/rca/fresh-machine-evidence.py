"""Offline causal checks. No evaluator calls, publication, or artifact modification."""
import copy
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path.cwd()))
from jsonschema import Draft202012Validator
import jot_agent as a
from jot_html import parse_transcript_document
from jot_evaluator import _decode_codex

root = Path('/Users/kebaux/Downloads/jot-transcripts')
stem = 'Stanford CS146S How always-on agents work'
request = json.loads((root / f'{stem}.request.json').read_text())
response = json.loads((root / f'{stem}.request.response.json').read_text())
second = json.loads((root / f'{stem} (1).request.json').read_text())
_, meta, transcript = parse_transcript_document(request['source_document'])
_, _, transcript2 = parse_transcript_document(second['source_document'])
segments = a._segments(transcript, a._duration(meta['Duration']))
assert transcript == transcript2
for packet, source in [(request, stem), (second, stem+' (1)')]:
    assert packet['source_document'] == (root / f'{source}.md').read_text()
    assert packet['request_id'] == a._digest({k:v for k,v in packet.items() if k != 'request_id'})
    assert packet['response_schema'] == json.loads(a.read_asset('evaluation-response.schema.json'))
    assert packet['rubric'] == a.read_asset('evaluation-rubric.md')
assert not list(Draft202012Validator(request['response_schema']).iter_errors(response))

citations = []
def walk(value, path='response'):
    if isinstance(value, dict):
        if set(value) == {'timestamp', 'quote'}:
            citations.append((path,value))
        else:
            for key, child in value.items(): walk(child, f'{path}.{key}')
    elif isinstance(value,list):
        for i, child in enumerate(value): walk(child, f'{path}[{i}]')
walk(response)
invalid=[]
for location, citation in citations:
    if not any(citation['quote'] in span for span in segments.get(citation['timestamp'], [])):
        matches=[t for t,spans in segments.items() if any(citation['quote'] in s for s in spans)]
        invalid.append({'location': location, **citation, 'matching_timestamps': matches})
assert len(citations)==43 and len(invalid)==1
assert invalid[0]['matching_timestamps']==[1907]
try:
    a._validate(request,response)
except ValueError as e:
    original_error=str(e)
    assert 'takeaways[5]' in original_error and 'timestamp 1909' in original_error
else: raise AssertionError('Original must fail')
# H1: only change the offending timestamp, in memory, leaving saved evidence untouched.
corrected=copy.deepcopy(response)
corrected['takeaways'][5]['evidence'][2]['timestamp']=1907
assert a._validate(request,corrected)[0] == 'Stanford CS146S: How always-on agents work'

# H2: vary only the non-fatal warning item, using the sequence quoted in message.txt.
warning='Skill descriptions were shortened to fit the skills context budget. Codex can still see every skill, but some descriptions are shorter. Disable unused skills or plugins to leave more room for the rest.'
success=[{'type':'thread.started','thread_id':'replay'}, {'type':'turn.started'}, {'type':'item.completed','item':{'id':'item_1','type':'agent_message','text':'{"ok":true}'}}, {'type':'turn.completed','usage':{'input_tokens':13386}}]
def decode(events): return _decode_codex(('\n'.join(json.dumps(e) for e in events)+'\n').encode())
assert decode(success)=={'ok':True}
with_warning=[*success[:2],{'type':'item.completed','item':{'id':'item_0','type':'error','message':warning}},*success[2:]]
try: decode(with_warning)
except ValueError as e: codex_error=str(e)
else: raise AssertionError('Warning replay must reproduce rejection')
assert 'Check `codex login`' in codex_error
# H3: terminal failure is different from a warning; actual failures remain rejected.
for fatal in [{'type':'turn.failed','error':{'message':'synthetic failure'}},{'type':'error','message':'synthetic failure'}]:
    try: decode([*success[:2], fatal, *success[2:]])
    except ValueError: pass
    else: raise AssertionError('Fatal events must fail')
print(json.dumps({
 'repository_head':__import__('subprocess').check_output(['git','rev-parse','HEAD'], text=True).strip(),
 'mode':'offline; no paid model calls; original artifacts unchanged',
 'artifact_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.iterdir()) if p.is_file()},
 'requests_match_saved_sources':True,'request_digests_and_packaged_protocol_match':True,
 'transcripts_identical_except_capture_metadata':True,'caption_lines':sum(len(s) for s in segments.values()),
 'distinct_timestamps':len(segments),'duration_seconds':a._duration(meta['Duration']),
 'response_schema_valid':True,'citations_total':len(citations),'invalid_citations':invalid,
 'claude_original_validation_error':original_error,
 'claude_single_timestamp_counterfactual_passes_full_validation':True,
 'codex_replay_provenance':'synthetic event reconstruction from message.txt; not the original stdout',
 'codex_without_warning':{'ok':True},'codex_with_warning_error':codex_error,
 'codex_fatal_event_controls_rejected':True
},indent=2))
