"""point map stops at their decks: python3 tools/gen/hookmap.py maps/derivatives.json defn=d-defn ..."""
import json, sys
p = sys.argv[1]
m = json.load(open(p))
want = dict(a.split('=') for a in sys.argv[2:])
for n in m['nodes']:
    if n['id'] in want:
        n['deck'] = want[n['id']]
json.dump(m, open(p, 'w'), indent=2, ensure_ascii=False)
open(p, 'a').write('\n')
print([(n['id'], n.get('deck')) for n in m['nodes']])
