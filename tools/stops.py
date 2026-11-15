"""Keep stops.json in step with the maps.  python3 tools/stops.py
Every stop with a deck needs a place in stops.json: its position is its bit in every app code.
This script only ever APPENDS new stops at the end. It never reorders or removes one, because that would
change what every code already handed in means. A stop taken off the maps simply keeps its place."""
import json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
reg = json.load(open(os.path.join(ROOT, 'stops.json')))
have = list(reg['v1'])
onmaps = []
for p in json.load(open(os.path.join(ROOT, 'worlds.json')))['worlds']:
    m = json.load(open(os.path.join(ROOT, p)))
    onmaps += [m['id'] + ':' + n['id'] for n in m['nodes'] if n.get('deck')]
new = [k for k in onmaps if k not in have]
gone = [k for k in have if k not in onmaps]
if len(have) + len(new) > 88:
    sys.exit('Version 1 codes hold 88 stops; this would make %d. Codes need a version 2 first.' % (len(have) + len(new)))
if new:
    reg['v1'] = have + new
    with open(os.path.join(ROOT, 'stops.json'), 'w') as f:
        json.dump(reg, f, indent=1)
        f.write('\n')
print('%d stops registered, %d added%s, %d of 88 places used' % (len(reg['v1']), len(new), (': ' + ', '.join(new)) if new else '', len(reg['v1'])))
if gone:
    print('Not on any map now (they keep their places):', ', '.join(gone))
