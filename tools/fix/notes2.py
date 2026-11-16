"""Content fixes from Dallas's review notes of Nov 15-16, 2026 (Worlds 0 and 1). One-time; guarded so it is safe to run again.
   python3 tools/fix/notes2.py"""
import json, os, re, copy
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
TR = standard_transformations + (implicit_multiplication_application, convert_xor)
x = sp.Symbol('x')


def load(dk):
    return json.load(open(os.path.join(ROOT, 'decks', dk + '.json')))


def save(d):
    with open(os.path.join(ROOT, 'decks', d['id'] + '.json'), 'w') as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
        f.write('\n')


def slides(d):
    return (d.get('lesson') or d['lessons'][0])['slides']


def S(d, i):
    return next(s for s in slides(d) if s['id'] == i)


def allq(d):
    for dr in d['drills'].values():
        for q in dr['questions']:
            yield q


def msym(m):
    """app math markup -> sympy"""
    def fr(s):
        while 'frac{' in s:
            i = s.index('frac{'); d = 0; j = i + 4
            for j in range(i + 4, len(s)):
                d += s[j] == '{'; d -= s[j] == '}'
                if d == 0: break
            k = j + 1; d = 0
            for e in range(k, len(s)):
                d += s[e] == '{'; d -= s[e] == '}'
                if d == 0: break
            s = s[:i] + '((' + fr(s[i + 5:j]) + ')/(' + fr(s[k + 1:e]) + '))' + s[e + 1:]
        return s
    return parse_expr(fr(m).replace('−', '-').replace('·', '*'), transformations=TR, local_dict={'x': x})


def bottom(m):
    """the denominator of a top-level frac{..}{..}, as markup"""
    d = 0
    for j in range(4, len(m)):
        d += m[j] == '{'; d -= m[j] == '}'
        if d == 0: break
    return m[j + 2:-1]


def excluded(orig, simp):
    """x-values where the original (markup) is undefined but the simplified form is fine"""
    d0 = msym(bottom(orig)); _, d1 = sp.fraction(sp.together(simp))
    bad = [r for r in sp.solve(d0, x) if r.is_real and sp.simplify(d1.subs(x, r)) != 0]
    return sorted(set(bad))


def ne(vals):
    v = ['$x ≠ %s$' % str(a).replace('-', '−') for a in vals]
    return ' and '.join(v)


# ============================================================ World 0
d = load('t-domain')
S(d, 'L2').update(text='So the domain is every number except 4. Interval notation says “every number except 1” like this: $(-∞, 1) ∪ (1, ∞)$.\nWrite the domain of\n$$f(x) = frac{1}{x - 4}$$',
                  hint='Everything below 4, joined to everything above 4.')
save(d)

d = load('t-rational')
sl = slides(d)
if not any(s['id'] == 'L2b' for s in sl):
    k = next(i for i, s in enumerate(sl) if s['id'] == 'L2')
    sl.insert(k + 1, {'id': 'L2b', 'type': 'mc', 'text': 'One catch, even when cancelling is legal.\n$$frac{x(x + 3)}{x} ;; x + 3$$\nAre these the same function?',
                      'options': ['Equal for every $x$ except 0, where the fraction is undefined', 'Yes, exactly the same', 'No, they never agree'], 'answer': 0, 'fixed': True,
                      'hint': 'Try $x = 0$ in each one.',
                      'explain': 'Cancelling the $x$ divides top and bottom by $x$, which is only allowed when $x ≠ 0$. So we write $frac{x(x + 3)}{x} = x + 3$ **for $x ≠ 0$**. The two are equal on their common domain, and the domain changed when we cancelled.'})
st = S(d, 'L5')['steps'][1]
st.update(text='Dividing by $x - 3$ is multiplying by $frac{1}{x - 3}$, and $3 - x = -(x - 3)$:\n$$frac{3 - x}{3x} · frac{1}{x - 3} = frac{-(x - 3)}{3x(x - 3)}$$\nCancel the $x - 3$ (allowed for $x ≠ 3$). What is left?',
          work='$= -frac{1}{3x}$, for $x ≠ 3$')
NOTE = ' The result equals the original only where the crossed-out factor is not 0: cancelling changes the domain.'
for dk in ('t-rational', 't-ready', 't-exponents'):
    dd = d if dk == 't-rational' else load(dk)
    for q in allq(dd):
        t = q.get('text', '')
        if q['type'] == 'cancel' and 'changes the domain' not in q.get('explain', ''):
            q['explain'] = (q.get('explain') or '').rstrip() + NOTE
        m = re.search(r'\$\$(frac\{.*\})\$\$', t)
        if q['type'] == 'expr' and m and re.search(r'Factor, then cancel|splits up', t) and 'changes the domain' not in q.get('explain', ''):
            try:
                ans = q['answer'] if isinstance(q['answer'], str) else q['answer'][0]
                bad = excluded(m.group(1), msym(ans))
            except Exception as e:
                bad = None
            if bad:
                q['explain'] = (q.get('explain') or '').rstrip() + ' This holds for %s, where the original is undefined: cancelling changes the domain.' % ne(bad)
                q['text'] = t.rstrip('\n') + '\n' if t.endswith('\n') else t
    if dk != 't-rational':
        save(dd)
save(d)

d = load('t-radicals')
S(d, 'L5').update(text='Here is the payoff: a conjugate clears a square root out of a denominator. Multiply the top and the bottom by the conjugate of the bottom.$$frac{6}{sqrt(7) - 1}$$\n', steps=[
    {'id': 'L5.1', 'type': 'num', 'text': 'The new bottom is\n$$(sqrt(7) - 1)(sqrt(7) + 1)$$\nMultiply it out.', 'answer': 6, 'label': 'bottom =', 'hint': '$a^2 - b^2$, with $a = sqrt(7)$ and $b = 1$.', 'work': 'bottom $= 7 - 1 = 6$'},
    {'id': 'L5.2', 'type': 'mc', 'text': 'The top was multiplied by the same conjugate, so the fraction is now\n$$frac{6(sqrt(7) + 1)}{6}$$', 'options': ['$sqrt(7) + 1$', '$6sqrt(7) + 1$', '$sqrt(7) - 1$', '$frac{sqrt(7) + 1}{6}$'], 'answer': 0,
     'hint': '6 is a factor of the top and of the bottom.', 'work': '$= sqrt(7) + 1$'}])
for q in list(slides(d)) + list(allq(d)):
    for k in ('text', 'explain', 'hint'):
        if isinstance(q.get(k), str):
            q[k] = q[k].replace('You just found the derivative of $sqrt(x)$: it is $frac{1}{2sqrt(x)}$.', '').replace('  ', ' ').strip() if 'You just found the derivative' in q[k] else q[k]
save(d)

d = load('t-compose')
S(d, 'L4')['text'] = 'Now run it backwards.$$h(x) = sqrt(x^2 + 1)$$\nIf you plugged in a number, what would you compute **first**? That part is the inside function.'
S(d, 'L5').update(text='$$h(x) = sqrt(x^2 + 1)$$\nThe outside function is what you do **last**. Call the inside $u = x^2 + 1$. Write the outside as a function of $u$.',
                  explain='$h(x) = f(g(x))$ with inside $g(x) = x^2 + 1$ and outside $f(u) = sqrt(u)$.')
save(d)

d = load('t-inverse')
S(d, 'L1')['text'] = 'An inverse function **undoes** $f$: it takes each output back to the input it came from.\n$$f(2) = 7$$'
S(d, 'L2').update(items=['Subtract 3', 'Divide by 2'])
s5 = S(d, 'L5'); s5.clear()
s5.update({'id': 'L5', 'type': 'pick', 'text': 'One warning about the notation. Select every statement that is **false**.',
           'options': ['$f^(-1)(x)$ always equals $frac{1}{f(x)}$', '$f^(-1)(x)$ equals $-f(x)$', '$f^(-1)(x)$ equals $f(-x)$'], 'answers': [0, 1, 2],
           'hint': 'For $f(x) = 2x + 3$ you just found $f^(-1)(x) = frac{x - 3}{2}$. Compare it with each one.',
           'explain': 'All three are false. The $-1$ is not an exponent here and has nothing to do with a minus sign: it means “inverse”. The reciprocal is written $(f(x))^(-1)$ or $frac{1}{f(x)}$.'})
save(d)

d = load('t-circle')
sl = slides(d)
if not any(s['id'] == 'L4b' for s in sl):
    k = next(i for i, s in enumerate(sl) if s['id'] == 'L4')
    sl.insert(k + 1, {'id': 'L4b', 'type': 'match', 'text': 'A way to remember the signs: **A**ll **S**tudents **T**ake **C**alculus, going around quadrants I, II, III, IV. Match each quadrant with what is **positive** there.',
                      'pairs': [['Quadrant I', '**A**ll of them'], ['Quadrant II', '**S**ine only'], ['Quadrant III', '**T**angent only'], ['Quadrant IV', '**C**osine only']],
                      'hint': 'Sine is the height and cosine is the left-right position. Tangent is positive when those two have the same sign.',
                      'explain': 'A, S, T, C: all, sine, tangent, cosine. Everything else in that quadrant is negative.'})
save(d)

for dk, old in (('t-exponents', ' In February every derivative of a root starts with this rewrite.'), ('t-notation', None)):
    d = load(dk)
    for q in list(slides(d)) + list(allq(d)):
        for k in ('text', 'explain', 'hint', 'after'):
            if isinstance(q.get(k), str):
                if old:
                    q[k] = q[k].replace(old, '')
                q[k] = re.sub(r' ?This is the first move of every derivative you will compute in this course\.?', '', q[k])
    save(d)

# ============================================================ World 1
d = load('limits-intro')
s = S(d, 's02'); s.clear()
s.update({'id': 's02', 'type': 'multi', 'title': 'Now walk toward it', 'graph': 'L1',
          'text': 'Forget the point at $x = 2$ for a moment. This is the graph of $f(x) = x + 1$. Fill in the heights as $x$ closes in on 2 from each side.',
          'parts': [{'label': '$f(1.9)$ =', 'answer': 2.9, 'tol': 0.0005}, {'label': '$f(1.99)$ =', 'answer': 2.99, 'tol': 0.0005}, {'label': '$f(2.01)$ =', 'answer': 3.01, 'tol': 0.0005}, {'label': '$f(2.1)$ =', 'answer': 3.1, 'tol': 0.0005}],
          'picture': False, 'hint': 'Add 1 to each $x$.', 'explain': 'From both sides, the heights close in on 3.'})
s = S(d, 's06'); s.clear()
s.update({'id': 's06', 'type': 'multi', 'graph': 'L2',
          'text': 'The point is gone: now $f(2)$ is undefined. Everywhere else, $f(x) = x + 1$ as before. Walk toward $x = 2$ anyway.',
          'parts': [{'label': '$f(1.99)$ =', 'answer': 2.99, 'tol': 0.0005}, {'label': '$f(1.999)$ =', 'answer': 2.999, 'tol': 0.00005}, {'label': '$f(2.001)$ =', 'answer': 3.001, 'tol': 0.00005}],
          'picture': False, 'hint': 'Add 1 to each $x$.', 'explain': 'Still closing in on 3, even though the graph never gets there.'})
S(d, 's03')['hint'] = 'Think back to the heights you filled in. What number were they closing in on?'
save(d)

d = load('l-laws')
giv = '$$lim[x->5] f(x) = 1 ;; lim[x->5] g(x) = 3$$\n'
s = S(d, 'L3')
if s['text'].startswith('Same'):
    s['text'] = giv + 'Find\n$$lim[x->5] frac{f(x)}{g(x)}$$'
save(d)

d = load('l-squeeze')
sl = slides(d)
if not any(s['id'] == 'L0' for s in sl):
    sl.insert(0, {'id': 'L0', 'type': 'mc', 'text': '$$lim[x->0] x^2 sin(frac{1}{x})$$\nWhy can we not just plug in $x = 0$?',
                  'options': ['$sin(frac{1}{x})$ is undefined at 0, and it wiggles forever near 0', 'We can: plugging in gives 0', 'The answer would be too big to write'], 'answer': 0,
                  'hint': 'What is $frac{1}{0}$?', 'explain': 'There is no value to plug in, and no algebra will tame the wiggle. We need another idea: trap it.'})
    S(d, 'L1')['text'] = 'Sine always stays between −1 and 1:\n$$-1 <= sin(frac{1}{x}) <= 1$$\nMultiply all three parts by $x^2$ (which is never negative).'
for q in d['drills']['theory']['questions']:
    if q['id'] == 'T4':
        q.clear()
        q.update({'id': 'T4', 'type': 'mc', 'text': 'Near 0 it can be shown that\n$$cos(x) <= frac{sin(x)}{x} <= 1$$\nAs $x -> 0$, $cos(x) -> 1$. So the Squeeze Theorem says $lim[x->0] frac{sin(x)}{x}$ is',
                  'options': ['1', '0', '$infty$', 'impossible to tell'], 'answer': 0, 'hint': 'Where do the two outside functions head?',
                  'explain': 'Both outside functions head to 1, so the one trapped between them must too. This is how the famous sine limit is proved.'})
save(d)

d = load('l-trig')
s = S(d, 'L1'); s.clear()
s.update({'id': 'L1', 'type': 'linear', 'title': 'The famous one', 'fn': 'sin(x)', 'a': 0, 'window': [-3.2, 3.2, -2.2, 2.2], 'goal': 'zoom', 'zoomGoal': 16,
          'text': 'Plugging $x = 0$ into $frac{sin(x)}{x}$ gives $frac{0}{0}$. Here is the top, $y = sin(x)$, drawn with the bottom, the line $y = x$. Zoom in on the origin until you cannot tell them apart.',
          'after': 'Near 0, $sin(x)$ and $x$ are almost the same number, so their ratio heads to **1**:\n$$lim[x->0] frac{sin(x)}{x} = 1$$'})
save(d)

d = load('l-cont')
s = S(d, 'L1'); s.clear()
s.update({'id': 'L1', 'type': 'pick', 'text': 'A function is **continuous** at $x = a$ when three things are all true. Select all three.',
          'options': ['$f(a)$ is defined', '$lim[x->a] f(x)$ exists', '$lim[x->a] f(x) = f(a)$'], 'answers': [0, 1, 2],
          'hint': 'The point, the limit, and whether they match.', 'explain': 'All three. Informally: you can draw the graph through $x = a$ without lifting your pencil.'})
save(d)

d = load('l-atinf')
S(d, 'L1')['text'] = '$$f(x) = 2 + frac{1}{x}$$\n{{table: x | 10 | 100 | 1000 ;; f(x) | 2.1 | 2.01 | 2.001}}'
save(d)

d = load('l-combo')
d['drills']['theory']['questions'] = [q for q in d['drills']['theory']['questions'] if q['id'] != 'T6']
save(d)

# "From class:" anywhere, and a specific label on the last part of a multi-part limit
import glob
for f in sorted(glob.glob(os.path.join(ROOT, 'decks', '*.json'))):
    d = json.load(open(f)); before = json.dumps(d)
    items = [s for L in [d.get('lesson')] + list(d.get('lessons', [])) if L for s in L['slides']] + list(allq(d))
    for q in items:
        if isinstance(q.get('text'), str):
            q['text'] = re.sub(r'^From class:\s*', '', q['text'])
        if q.get('type') == 'steps':
            m = re.findall(r'\$\$(lim\[[^$]+)\$\$', q.get('text', ''))
            last = q['steps'][-1]
            if len(m) == 1 and len(m[0]) <= 48 and last.get('label', '').strip() in ('limit =', 'Limit ='):
                last['label'] = '$' + m[0] + '$ ='
    if json.dumps(d) != before:
        save(d)
print('done')
