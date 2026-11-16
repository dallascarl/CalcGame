"""Lays out the Limits, Derivatives and Integration maps by class day, the way the Toolkit and Applications maps are.
Edit DAYS below (which stops belong to which day, row by row, with the x position of each) and run:
   python3 tools/maps.py && python3 tools/stops.py
Stops keep their ids, titles, decks and blurbs; only positions, roads and the dashed day boxes change."""
import json, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
L, C, R = 26, 50, 74
DAYS = {
    'limits': ([
        ('Day 8', [[('limits', L), ('infinite', R)], [('evaluate', L), ('vasym', R)]]),
        ('Day 9', [[('laws', L), ('factor', R)], [('sqrtlim', L), ('complex', R)], [('sqroots', L), ('fractions', R)]]),
        ('Day 10', [[('infinity', C)], [('squeeze', L), ('trig', R)]]),
        ('Day 11', [[('continuity', L), ('combo', R)]]),
    ], [('precise', L), ('review', R)]),
    'derivatives': ([
        ('Day 13', [[('defn', C)]]),
        ('Day 14', [[('dfunc', C)]]),
        ('Day 15', [[('rules', C)]]),
        ('Day 16', [[('trigrev', L), ('trig', R)]]),
        ('Day 17', [[('compose', L), ('chain', R)]]),
        ('Day 18', [[('exp', L), ('dlog', R)], [('logdiff', L), ('hyper', R)]]),
        ('Day 19', [[('implicit', L), ('invtrig', R)], [('solvey', 16), ('invfun', C), ('invtrigrev', 84)]]),
    ], [('review', C)]),
    'integration': ([
        ('Day 33', [[('anti', L), ('indef', R)]]),
        ('Day 34', [[('sumnot', L), ('areas', R)]]),
        ('Day 35', [[('definite', C)]]),
        ('Day 36', [[('ftc', L), ('proof', R)]]),
        ('Day 37', [[('ftc2', C)]]),
        ('Days 38 and 39', [[('subst', C)]]),
    ], [('review', C)]),
}
ROW, PAD, GAP = 36, 20, 6
for mid, (days, tail) in DAYS.items():
    path = os.path.join(ROOT, 'maps', mid + '.json')
    m = json.load(open(path))
    old = {n['id']: n for n in m['nodes']}
    placed = [nid for _, rows in days for row in rows for nid, _ in row] + [nid for nid, _ in tail]
    assert sorted(placed + ['start']) == sorted(old), (mid, set(old) ^ set(placed + ['start']))
    nodes = [dict(old['start'], x=50, y=10, requires=[])]
    nodes[0].pop('from', None)
    regions, y, prev = [], 24, 'start'
    for label, rows in days:
        h = PAD + ROW * (len(rows) - 1) + 19
        regions.append({'label': label, 'x': 3, 'y': y, 'w': 94, 'h': h})
        mains = [nid for row in rows for nid, _ in row if old[nid]['kind'] == 'main']
        pos = {nid: (px, ri) for ri, row in enumerate(rows) for nid, px in row}
        for ri, row in enumerate(rows):
            for nid, px in row:
                n = dict(old[nid], x=px, y=y + PAD + ROW * ri)
                n.pop('from', None)
                if n['kind'] == 'main':                 # the road runs through the main stops in order
                    n['requires'] = [prev]
                    prev = nid
                else:                                   # a side stop hangs off the nearest main stop of its day
                    n['requires'] = [min(mains, key=lambda k: (abs(pos[k][0] - px) + 40 * abs(pos[k][1] - ri), mains.index(k)))]
                nodes.append(n)
        y += h + GAP
    for nid, px in tail:
        n = dict(old[nid], x=px, y=y + 16, requires=[prev])
        n.pop('from', None)
        nodes.append(n)
    m['regions'], m['nodes'], m['height'] = regions, nodes, y + 38
    with open(path, 'w') as f:
        json.dump(m, f, indent=1, ensure_ascii=False)
        f.write('\n')
    print(mid, 'height', m['height'], len(nodes), 'stops')
