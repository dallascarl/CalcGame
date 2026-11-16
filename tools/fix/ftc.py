"""One-time: gives each part of the Fundamental Theorem its own stop (class days 36 and 37), from Dallas's note of Nov 16, 2026.
   w-ftc   -> Part 1 (area functions and their derivatives), with a new lesson opening and generated practice
   w-ftc2  -> Part 2 and the Net Change Theorem (net change moves here from w-indef, where it came before definite integrals)
   w-indef -> Indefinite Integrals only
   python3 tools/fix/ftc.py && python3 tools/maps.py && python3 tools/stops.py && node tools/gen/verify.js"""
import json, os, copy, random
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TR = standard_transformations + (implicit_multiplication_application, convert_xor)
x, t = sp.symbols('x t')
KEYS = ['sin(', 'cos(', 'tan(', 'sqrt(', 'e^(', 'ln(']
MAN = []


def load(dk):
    return json.load(open(os.path.join(ROOT, 'decks', dk + '.json')))


def save(d):
    with open(os.path.join(ROOT, 'decks', d['id'] + '.json'), 'w') as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
        f.write('\n')


def app(s):
    return parse_expr(s, transformations=TR, local_dict={'x': x, 'e': sp.E})


def E(deck, qid, text, answer, truth, label, show, upToC=False, **kw):
    """a typed-formula question; the answer string is checked against sympy here and against the app's parser by verify.js"""
    diff = sp.simplify(app(answer) - truth)
    assert (sp.diff(diff, x) == 0) if upToC else diff == 0, (qid, answer, truth)
    pts = [0.37, 0.71, 1.13]
    MAN.append({'deck': deck, 'id': qid, 'answer': answer, 'vars': ['x'], 'upToC': upToC, 'samples': [[{'x': p}, float(truth.subs(x, p))] for p in pts]})
    q = {'id': qid, 'type': 'expr', 'text': text, 'answer': answer, 'vars': ['x'], 'keys': KEYS, 'label': label, 'show': '$' + show + '$', 'ranges': {'x': [0.3, 1.2]}}
    if upToC:
        q.update(post='$+ C$', upToC=True)
    q.update(kw)
    return q


if os.path.exists(os.path.join(ROOT, 'decks', 'w-ftc2.json')):
    raise SystemExit('already split')
F, I = load('w-ftc'), load('w-indef')
fl = {s['id']: s for s in F['lesson']['slides']}
il = {s['id']: s for s in I['lesson']['slides']}
ft = {q['id']: q for q in F['drills']['theory']['questions']}
it = {q['id']: q for q in I['drills']['theory']['questions']}
fp, ip = F['drills']['practice']['questions'], I['drills']['practice']['questions']
grp = lambda qs, letters: [q for q in qs if q['id'].rstrip('0123456789') in letters]
re_id = lambda q, i: dict(copy.deepcopy(q), id=i)

# ------------------------------------------------------------------ Part 1 (day 36)
P1 = {k: F[k] for k in ('id', 'course', 'unit')}
P1.update(title='The Fundamental Theorem, Part 1', subtitle='The derivative of an area function is the function you started with.', version=3,
          graphs={'flat': {'window': [-0.5, 4.5, -0.5, 3.5], 'pieces': [{'expr': '2', 'from': -0.5, 'to': 4.5}], 'rects': [[0, 3, 2]]},
                  'tri': {'window': [-0.5, 4.5, -0.5, 4.5], 'pieces': [{'expr': 'x', 'from': -0.5, 'to': 4.5}], 'vlines': [3], 'labels': [[3, 3, 'x']]}})
lesson = [
    {'id': 'L1', 'type': 'num', 'graph': 'flat', 'text': 'An **area function** adds up area from a fixed start to a moving end.\n$$A(x) = int[0,x] 2 dt$$\nThe graph of $f(t) = 2$ is a flat line, so the area is a rectangle.',
     'answer': 6, 'label': '$A(3)$ =', 'hint': 'The rectangle is 3 wide and 2 tall.', 'explain': 'Width 3 times height 2.'},
    E('w-ftc', 'L2', '$$A(x) = int[0,x] 2 dt$$\nNow let the right edge be $x$ instead of 3. The rectangle is $x$ wide and 2 tall.', '2x', 2 * x, '$A(x)$ =', '2x', hint='Width times height.', explain='$A(x) = 2x$.'),
    {'id': 'L3', 'type': 'mc', 'text': '$A(x) = 2x$, so $A\'(x) = 2$. Where have you seen that 2 before?', 'options': ['It is the height of the function being integrated, $f(t) = 2$', 'It is the left endpoint', 'Nowhere. It is a coincidence'], 'answer': 0,
     'hint': 'Look inside the integral.', 'explain': 'The area grows at a rate equal to the height at the moving edge. That is the whole theorem.'},
    E('w-ftc', 'L4', 'Try a slanted one. Under $f(t) = t$, the area from 0 to $x$ is a triangle, $x$ wide and $x$ tall.\n$$A(x) = int[0,x] t dt$$', 'x^2/2', x ** 2 / 2, '$A(x)$ =', 'frac{x^2}{2}', graph='tri',
      hint='Half of base times height.', explain='$A(x) = frac{x^2}{2}$, and its derivative is $x$: again the height of $f$ at the moving edge.'),
    re_id(fl['L3'], 'L5'), re_id(fl['L4'], 'L6')]
lesson[4]['text'] = lesson[4]['text'].replace('**FTC, part 1:**', '**The Fundamental Theorem, Part 1.** It works for every continuous $f$:')
theory = [
    {'id': 'T1', 'type': 'mc', 'text': '$$A(x) = int[2,x] f(t) dt$$\nWhat is $A(2)$?', 'options': ['0', '$f(2)$', '2', 'It depends on $f$'], 'answer': 0, 'hint': 'How wide is the region from 2 to 2?', 'explain': 'No width, so no area.'},
    {'id': 'T2', 'type': 'mc', 'text': '$$frac{d}{dx} int[1,x] cos(t^2) dt =$$', 'options': ['$cos(x^2)$', '$-2x sin(x^2)$', '$cos(x^2) - cos(1)$', '$sin(x^2)$'], 'answer': 0,
     'hint': 'You do not need an antiderivative of $cos(t^2)$. (Nobody has a formula for one.)', 'explain': 'Part 1: the derivative of the area function is the integrand, with $x$ in place of $t$.'},
    {'id': 'T3', 'type': 'tf', 'text': 'Changing the lower limit from 1 to 5 changes the value of $frac{d}{dx} int[1,x] f(t) dt$.', 'answer': False,
     'hint': 'What does moving the starting point do to the area function?', 'explain': 'A different start shifts the area by a constant, and the derivative of a constant is 0. The answer is $f(x)$ either way.'},
    re_id(ft['T3'], 'T4'),
    {'id': 'T5', 'type': 'mc', 'text': '$$frac{d}{dx} int[x,3] f(t) dt =$$', 'options': ['$-f(x)$', '$f(x)$', '$f(3)$', '0'], 'answer': 0, 'hint': 'Part 1 needs $x$ on top. What does swapping the limits do?',
     'explain': 'Swap the limits first: $int[x,3] f(t) dt = -int[3,x] f(t) dt$.'},
    {'id': 'T6', 'type': 'tf', 'text': 'Part 1 says that every continuous function has an antiderivative.', 'answer': True, 'hint': 'What is the derivative of $A(x) = int[a,x] f(t) dt$?',
     'explain': 'The area function $A(x) = int[a,x] f(t) dt$ is one: its derivative is $f(x)$.'}]
prac = grp(fp, ('P',)) + grp(fp, ('C',))
rng = random.Random(36)
fs = [('2t + 1', 2 * t + 1), ('t^2 - 3', t ** 2 - 3), ('3t^2 + t', 3 * t ** 2 + t), ('5 - t', 5 - t), ('t^3', t ** 3), ('4t - t^2', 4 * t - t ** 2), ('t^2 + 2t', t ** 2 + 2 * t), ('6 - 2t', 6 - 2 * t)]
for n, (shown, f) in enumerate(fs, 1):
    k = rng.choice([1, 2, 3]); a = rng.choice([0, 1, 2]); v = f.subs(t, k)
    prac.append({'id': 'G%d' % n, 'type': 'num', 'level': 1, 'text': '$$A(x) = int[%d,x] (%s) dt$$' % (a, shown), 'answer': int(v), 'label': "$A'(%d)$ =" % k,
                 'hint': "$A'(x)$ is the integrand with $x$ in place of $t$.", 'explain': "$A'(x) = %s$, so $A'(%d) = %s$." % (shown.replace('t', 'x'), k, str(v).replace('-', '−'))})
rs = [('t^2 + 1', '-(x^2 + 1)', -(x ** 2 + 1), '-(x^2 + 1)', 5), ('sin(t)', '-sin(x)', -sp.sin(x), '-sin(x)', 2), ('e^t', '-e^(x)', -sp.exp(x), '-e^x', 0), ('sqrt(t)', '-sqrt(x)', -sp.sqrt(x), '-sqrt(x)', 4),
      ('cos(t)', '-cos(x)', -sp.cos(x), '-cos(x)', 1), ('t^3', '-x^3', -x ** 3, '-x^3', 3)]
for n, (shown, ans, tr, show, b) in enumerate(rs, 1):
    prac.append(E('w-ftc', 'R%d' % n, 'Find\n$$frac{d}{dx} int[x,%d] %s dt$$' % (b, shown if '+' not in shown else '(' + shown + ')'), ans, tr, 'derivative =', show, level=2,
                  hint='Swap the limits so that $x$ is on top. That costs a minus sign.', explain='$int[x,%d] = -int[%d,x]$, so the derivative is $%s$.' % (b, b, show)))
cs = [('x^3', '3x^2', 3 * x ** 2, 'cos(t)', 'cos(x^3)', sp.cos(x ** 3), 0), ('2x', '2', sp.Integer(2), 't^2 + 1', '4x^2 + 1', 4 * x ** 2 + 1, 1), ('x^2', '2x', 2 * x, 'e^t', 'e^(x^2)', sp.exp(x ** 2), 0),
      ('sin(x)', 'cos(x)', sp.cos(x), 't^2', 'sin(x)^2', sp.sin(x) ** 2, 0), ('3x', '3', sp.Integer(3), 'sqrt(t)', 'sqrt(3x)', sp.sqrt(3 * x), 1), ('x^2', '2x', 2 * x, 't^3', 'x^6', x ** 6, 2)]
for n, (g, dg, dgt, fshown, fg, fgt, a) in enumerate(cs, 1):
    qid = 'S%d' % n
    full = '%s(%s)' % (fg if fg.endswith(')') or fg.isalnum() or fg == 'x^6' else '(' + fg + ')', dg) if dg not in ('2', '3') else '%s(%s)' % (dg, fg)
    fshow = lambda s: s.replace('e^(x^2)', 'e^(x^2)').replace('sin(x)^2', 'sin^2(x)')
    prac.append({'id': qid, 'type': 'steps', 'level': 3, 'title': 'Part 1 with the chain rule', 'text': 'Find\n$$frac{d}{dx} int[%d,%s] %s dt$$' % (a, g, fshown if '+' not in fshown else '(' + fshown + ')'), 'steps': [
        E('w-ftc', qid + '.1', 'The upper limit is the inside function, $g(x) = %s$. Find its derivative.' % g, dg, dgt, "$g'(x)$ =", dg, hint='An ordinary derivative.', work="$g'(x) = %s$" % dg),
        E('w-ftc', qid + '.2', 'Put the upper limit into the integrand: replace $t$ with $%s$.' % g, fg, fgt, '$f(g(x))$ =', fshow(fg), hint='The integrand is $%s$.' % fshown, work='$f(g(x)) = %s$' % fshow(fg)),
        E('w-ftc', qid + '.3', 'Multiply the two.', full, fgt * dgt, 'derivative =', fshow(full), hint="$f(g(x))·g'(x)$", work='$= %s$' % fshow(full))]})
P1['lesson'] = {'slides': lesson}
P1['drills'] = {'theory': {'title': 'Theory', 'mode': 'all', 'questions': theory}, 'practice': {'title': 'Practice', 'mode': 'pool', 'questions': prac}}

# ------------------------------------------------------------------ Part 2 and net change (day 37)
P2 = {'id': 'w-ftc2', 'course': F['course'], 'unit': F['unit'], 'title': 'The Fundamental Theorem, Part 2, and Net Change', 'subtitle': 'Exact areas from antiderivatives, and total change from a rate.', 'version': 1, 'graphs': {}}
l2 = [re_id(fl['L1'], 'L1'), re_id(fl['L2'], 'L2'), re_id(il['L3'], 'L3'), re_id(il['L4'], 'L4'), re_id(il['L5'], 'L5'), re_id(fl['L5'], 'L6')]
l2[0]['text'] = l2[0]['text'].replace('**FTC, part 2:**', '**The Fundamental Theorem, Part 2:**')
for i, st in enumerate(l2[3].get('steps', []), 1):
    st['id'] = 'L4.%d' % i
t2 = [re_id(q, 'T%d' % (i + 1)) for i, q in enumerate([ft['T1'], ft['T2'], ft['T5'], it['T1'], it['T2'], it['T3'], ft['T4']])]
p2 = grp(fp, ('F', 'D', 'W', 'A')) + [dict(copy.deepcopy(q), id='N' + q['id']) for q in grp(ip, ('N', 'T'))]
for q in p2:
    for i, st in enumerate(q.get('steps', []), 1):
        st['id'] = '%s.%d' % (q['id'], i)
P2['lesson'] = {'slides': l2}
P2['drills'] = {'theory': {'title': 'Theory', 'mode': 'all', 'questions': t2}, 'practice': {'title': 'Practice', 'mode': 'pool', 'questions': p2}}

# ------------------------------------------------------------------ Indefinite integrals (day 33)
I.update(title='Indefinite Integrals', subtitle='Antiderivatives with + C.')
il['L2']['text'] = il['L2']['text'].replace('Game time from class! ', '')
I['lesson']['slides'] = [il['L1'], il['L2'],
    {'id': 'L3', 'type': 'mc', 'text': 'Why the $+ C$?\n$$frac{d}{dx}(x^2 + 7) = 2x ;; frac{d}{dx}(x^2 - 3) = 2x$$\nSo $int 2x dx$ is', 'options': ['$x^2 + C$: every one of them at once', '$x^2$ only', '$x^2 + 7$', '2'], 'answer': 0,
     'hint': 'How many functions have derivative $2x$?', 'explain': 'A constant disappears when you differentiate, so the indefinite integral has to allow any constant.'},
    E('w-indef', 'L4', 'Constants and sums come along for the ride, just as with derivatives. Find\n$$int (6x^2 - 4sin(x)) dx$$', '2x^3 + 4cos(x)', 2 * x ** 3 + 4 * sp.cos(x), '$int (6x^2 - 4sin(x)) dx$ =', '2x^3 + 4cos(x)', upToC=True,
      hint='Term by term. An antiderivative of $sin(x)$ is $-cos(x)$.', explain='$2x^3 + 4cos(x) + C$'),
    {'id': 'L5', 'type': 'mc', 'text': 'You can always check an integral by differentiating the answer. A student writes\n$$int x cos(x) dx = frac{x^2}{2} sin(x) + C$$\nDifferentiate the right side. Is the student correct?',
     'options': ['No. The product rule gives $x sin(x) + frac{x^2}{2} cos(x)$, not $x cos(x)$', 'Yes'], 'answer': 0, 'fixed': True, 'hint': 'The right side is a product.',
     'explain': 'There is no product rule for integrals: you cannot integrate each factor separately. When in doubt, differentiate your answer.'}]
I['drills']['theory']['questions'] = [it['T4'], it['T5'],
    {'id': 'T6', 'type': 'tf', 'text': 'Two antiderivatives of the same function can differ only by a constant.', 'answer': True, 'hint': 'That is what the $+ C$ is for.', 'explain': 'If $F\' = G\'$ on an interval, then $F - G$ is constant there.'},
    {'id': 'T7', 'type': 'mc', 'text': 'For $n ≠ -1$,\n$$int x^n dx =$$', 'options': ['$frac{x^(n+1)}{n+1} + C$', '$n x^(n-1) + C$', '$frac{x^n}{n} + C$', '$x^(n+1) + C$'], 'answer': 0, 'hint': 'Run the power rule backwards.', 'explain': 'Raise the power by one, then divide by the new power.'},
    {'id': 'T8', 'type': 'mc', 'text': '$$int frac{1}{x} dx =$$', 'options': ['$ln|x| + C$', '$-frac{1}{x^2} + C$', '$frac{x^0}{0} + C$', '$x + C$'], 'answer': 0, 'hint': 'This is the one power the power rule cannot handle.', 'explain': 'The derivative of $ln|x|$ is $frac{1}{x}$.'},
    {'id': 'T9', 'type': 'tf', 'text': '$int f(x)g(x) dx = int f(x) dx · int g(x) dx$', 'answer': False, 'hint': 'Try $f(x) = g(x) = x$.', 'explain': 'With $f = g = x$ the left side is $frac{x^3}{3} + C$ and the right side is about $frac{x^4}{4}$. Integrals split over sums, not products.'},
    {'id': 'T10', 'type': 'mc', 'text': '$$int e^x dx =$$', 'options': ['$e^x + C$', '$frac{e^(x+1)}{x+1} + C$', '$x e^(x-1) + C$', '$ln(x) + C$'], 'answer': 0, 'hint': 'Which function is its own derivative?', 'explain': '$e^x$ is its own derivative, so it is its own antiderivative.'}]
keep = grp(ip, ('I',))
for q in keep:
    a = q['answer'] if isinstance(q['answer'], str) else q['answer'][0]
    q['level'] = 2 if len(a.replace(' ', '')) > 9 else 1
I['drills']['practice']['questions'] = keep
for d in (P1, P2, I):
    save(d)
    pr = d['drills']['practice']['questions']
    print(d['id'], 'lesson', len(d['lesson']['slides']), 'theory', len(d['drills']['theory']['questions']), 'practice', len(pr), [sum(1 for q in pr if q['level'] == k) for k in (1, 2, 3)])
json.dump(MAN, open(os.path.join(ROOT, 'tools', 'gen', 'out', 'ftc.manifest.json'), 'w'))

# ------------------------------------------------------------------ the map
mp = os.path.join(ROOT, 'maps', 'integration.json')
m = json.load(open(mp))
for n in m['nodes']:
    if n['id'] == 'ftc':
        n.update(title='The Fundamental Theorem, Part 1', label='FTC Part 1', blurb='The derivative of an area function is the function you started with.')
    if n['id'] == 'indef':
        n.update(title='Indefinite Integrals', blurb='Antiderivatives with + C.')
        n.pop('label', None)
m['nodes'].append({'id': 'ftc2', 'kind': 'main', 'title': 'The Fundamental Theorem, Part 2, and Net Change', 'label': 'FTC Part 2', 'x': 50, 'y': 0, 'deck': 'w-ftc2', 'requires': ['ftc'],
                   'blurb': 'Exact areas from antiderivatives, and total change from a rate.'})
json.dump(m, open(mp, 'w'), indent=1, ensure_ascii=False)
