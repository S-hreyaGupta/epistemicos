import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import cycle_projection as cp
import loop_state as ls
import run_pins
import test_validate_cycle as tv
import test_ledger as tl


def put(path, obj):
    tv.write_lf(path, json.dumps(obj, indent=2) + '\n')


def bind(cycle, target):
    put(cycle / 'target.json', target)
    digest = tv.sha256_file(cycle / 'target.json')
    tv.write_lf(cycle / 'target.sha256', digest + '\n')
    tv.write_lf(cycle / 'codex-input.md', 'Review target ' + digest + '\n')


def fixture():
    root, commit, tree = tv.make_repo()
    cycle = tv.build(root, commit, tree)
    runpath = cycle.parent.parent / 'run.json'
    run = json.loads(runpath.read_text())
    for entry in [run['protocol'], *run['spec_files']]:
        tv.write_lf(root / entry['path'], '# Governing document\n')
        entry['sha256'] = tv.sha256_file(root / entry['path'])
    put(runpath, run)
    target = json.loads((cycle / 'target.json').read_text())
    target['governing_pins'] = run_pins.initial_pin_set(run)
    target['governing_pin_hashes'] = run_pins.pin_hashes_for_cycle(run, [], 1)
    target['protocol_sha256'] = run['protocol']['sha256']
    target['spec_sha256'] = run_pins.spec_digest(run['spec_files'])
    bind(cycle, target)
    code, out = tv.run(root, cycle)
    assert code == 0, out
    return root, cycle, run, target


h = [{'cycle': c, 'event': e} for c, e in [
    (1, 'RAISED'), (1, 'ACCEPT'), (2, 'DEMONSTRATED'),
    (3, 'REOPENED'), (2, 'ACCEPT'), (4, 'DEMONSTRATED')]]
p = cp.Projection([1, 2, 3, 4], {})
print('REPLAY', cp.replay(h, p), 'ACCEPT', cp.last_authorized(h, 'ACCEPT', p),
      'CONTROLLER', ls.state_after({'history': h}, {1, 2, 3, 4}),
      'SKIPPED', cp.skipped_events(h, p), flush=True)

root, cycle, run, target = fixture()
(root / run['protocol']['path']).unlink()
(root / run['spec_files'][0]['path']).unlink()
code, out = tv.run(root, cycle)
print('MISSING GOVERNING FILES', code, tv.marks(out), flush=True)

root, cycle, run, target = fixture()
items = [{'reason': 'test invalid protocol removal from governing set',
          'affected_artifacts': [run['protocol']['path']],
          'prior_pin_set': target['governing_pins'],
          'new_pin_set': [run['spec_files'][0]['path']],
          'effective_cycle': 1, 'authorized_by': 'review fixture', 'at': '2026-09-25'}]
put(cycle.parent.parent / 'pin-amendments.json', {'schema': run_pins.SCHEMA, 'amendments': items})
try:
    run_pins.validate_chain(run, items)
except run_pins.PinError as e:
    print('CHAIN REJECTED', str(e).splitlines()[0], flush=True)
# A malformed amendment preserving paths but lying about its prior set is not checked.
items[0]['new_pin_set'] = target['governing_pins']
items[0]['prior_pin_set'] = ['never-pinned.md']
put(cycle.parent.parent / 'pin-amendments.json', {'schema': run_pins.SCHEMA, 'amendments': items})
try:
    run_pins.validate_chain(run, items)
except run_pins.PinError as e:
    print('SECOND CHAIN REJECTED', str(e).splitlines()[0], flush=True)
code, out = tv.run(root, cycle)
print('INVALID CHAIN MC2', code, tv.marks(out), flush=True)

root, cycle, run, target = fixture()
target['cycle'] = 2
target['run_id'] = 'ANOTHER-RUN'
bind(cycle, target)
code, out = tv.run(root, cycle)
print('WRONG CYCLE AND RUN', code, tv.marks(out), 'directory', cycle.name, flush=True)

root, commit = tl.make_repo()
review = root / 'runs/T-001/plan-review'
tl.make_cycle(root, review, 1, commit)
runpath = review.parent / 'run.json'
run = json.loads(runpath.read_text())
run['bootstrap_review'] = 'EXEMPT - NOT_A_PROTOCOL_CYCLE'
put(runpath, run)
print('EXEMPT BASELINE', tl.loop(root, review).returncode, flush=True)
del run['bootstrap_review']
put(runpath, run)
r = tl.loop(root, review)
print('MISSING CLASSIFICATION', r.returncode, tl.status_of(r.stdout), flush=True)

# A structured reviewer finding exists, but its ledger entry was raised in an absent cycle.
c = review / 'cycle-01'
tv.write_lf(c / 'codex-output-raw.md', 'Finding ID: C01-F01\nClass: UNTESTED RULE\n')
put(c / 'findings.json', {'schema': 'cycle-findings/1', 'cycle': 1, 'count': 1,
    'findings': [{'id': 'C01-F01', 'class': 'UNTESTED RULE'}]})
put(review / 'ledger.json', {'findings': {'C01-F01': {
    'history': [{'cycle': 2, 'event': 'RAISED', 'state': 'OPEN'}], 'state': 'OPEN'}}})
r = tl.loop(root, review)
print('UNACCOUNTED RAISE', r.returncode, tl.status_of(r.stdout), flush=True)

root, commit = tl.make_repo()
review = root / 'runs/T-001/plan-review'
for n in range(1, 6):
    tl.make_cycle(root, review, n, commit)
put(review / 'ledger.json', {'findings': {'C01-F01': {'history': [
    {'cycle': 1, 'event': 'RAISED', 'state': 'OPEN'},
    {'cycle': 1, 'event': 'ACCEPT', 'state': 'OPEN'},
    {'cycle': 5, 'event': 'DEMONSTRATED', 'state': 'RESOLVED'}]}}})
put(review / 'loop-authorizations.json', {'schema': 'loop-authorization/1',
    'authorizations': [{'after_valid_cycle': n, 'outcome': 'STALLED',
                        'authorized_by': 'review fixture',
                        'reason': 'Continue within the allowed cycle budget'}
                       for n in (2, 3, 4)]})
r = tl.loop(root, review)
print('HISTORICAL FOURTH BOUNDARY', r.returncode, r.stdout, r.stderr, flush=True)

root, commit = tl.make_repo()
review = root / 'runs/T-001/plan-review'
tl.make_cycle(root, review, 1, commit)
tl.make_cycle(root, review, 2, commit)
put(review / 'ledger.json', {'findings': {'C01-F01': {'history': [
    {'cycle': 1, 'event': 'RAISED', 'state': 'OPEN'}]}}})
for n in (1, 2):
    cycle = review / f'cycle-{n:02d}'
    suffix = 'Class: UNTESTED RULE' if n == 1 else 'Status: REPAIR NOT DEMONSTRATED'
    tv.write_lf(cycle / 'codex-output-raw.md', 'Finding ID: C01-F01\n' + suffix + '\n')
    put(cycle / 'findings.json', {'schema': 'cycle-findings/1', 'cycle': n, 'count': 1,
        'findings': [{'id': 'C01-F01', 'class': 'UNTESTED RULE'}]})
r = tl.loop(root, review)
print('RECURRENCE BASELINE', r.returncode, tl.status_of(r.stdout), flush=True)
tv.write_lf(review / 'cycle-01/target.sha256', '0' * 64 + '\n')
r = tl.loop(root, review)
print('VALID RECURRENCE AFTER INVALID ORIGIN', r.returncode, r.stdout, r.stderr, flush=True)

import test_run_review as tr
import subprocess
root = tr.make_repo()
approval = tr.approve_bootstrap(root)
assert approval.returncode == 0, approval.stderr
protocol = root / 'specs/protocol.md'
tr.write_lf(protocol, '# Changed protocol, not committed\n')
r = tr.runner(root, 'init', '--run', 'T-001', '--protocol', 'specs/protocol.md',
              '--spec', 'specs/spec.md')
print('DIRTY PROTOCOL INIT', r.returncode, r.stdout, r.stderr, flush=True)
run = json.loads((root / 'runs/T-001/run.json').read_text())
committed = subprocess.check_output(['git', '-C', str(root), 'show',
                                    run['protocol_commit'] + ':specs/protocol.md'])
print('PROTOCOL COMMIT HASH AGREES', hashlib.sha256(committed).hexdigest() ==
      run['protocol']['sha256'], flush=True)

for key, val in [('cycle', 2), ('run_id', 'ANOTHER-RUN')]:
    root, cycle, run, target = fixture()
    target[key] = val
    bind(cycle, target)
    code, out = tv.run(root, cycle)
    print('ISOLATED IDENTITY', key, val, code, tv.marks(out), flush=True)
