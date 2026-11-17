"""Content fixes from Dallas's review notes of Nov 16, 2026 (World 2). One-time; guarded so it is safe to run again.
The main idea: a lesson should not make anyone type a long formula on a phone. Long answers become "tap the pieces into the rule".
   python3 tools/fix/notes3.py"""
import json, os, itertools
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def load(dk):
    return json.load(open(os.path.join(ROOT, 'decks', dk + '.json')))


def save(d):
    with open(os.path.join(ROOT, 'decks', d['id'] + '.json'), 'w') as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
        f.write('\n')


def S(d, i):
    return next(s for s in (d.get('lesson') or d['lessons'][0])['slides'] if s['id'] == i)


def product_bank(qid, lead, g, kp, gp, k, work, hint, text='Tap the pieces into the rule, $gk\' + g\'k$.'):
    a, b = [g, kp], [gp, k]
    alts = [list(p1) + list(p2) for t1, t2 in ((a, b), (b, a)) for p1 in itertools.permutations(t1) for p2 in itertools.permutations(t2)]
    return {'id': qid, 'type': 'bank', 'text': text + '\n' + lead + ' = ___ · ___ + ___ · ___', 'blanks': alts[0], 'alts': alts[1:], 'hint': hint, 'work': work}


def quotient_bank(qid, lead, g, gp, k, kp, low2, work, hint, text='Tap the pieces into the rule: low d-high minus high d-low, over low squared.'):
    alts = [list(p1) + list(p2) for p1 in itertools.permutations([k, gp]) for p2 in itertools.permutations([g, kp])]
    return {'id': qid, 'type': 'bank', 'text': text + '\n' + lead + ' = frac{___ · ___ − ___ · ___}{' + low2 + '}', 'blanks': alts[0], 'alts': alts[1:], 'hint': hint, 'work': work}


# ---------------------------------------------------------------- Definition of the derivative
d = load('d-defn')
sl = d['lesson']['slides']
if not any(s['id'] == 'L0' for s in sl):
    d.setdefault('graphs', {})['sec'] = {'window': [-0.6, 3.4, -1, 9.6], 'pieces': [{'expr': 'x^2', 'from': -0.6, 'to': 3.2}], 'dots': [[2, 4], [3, 9], [2.5, 6.25]], 'labels': [[2, 4, 'x = 2']]}
    sl.insert(0, {'id': 'L0', 'type': 'multi', 'title': 'From secant to tangent', 'graph': 'sec',
                  'text': 'The slope of a **secant line** through two points on a curve is\n$$m = frac{f(b) - f(a)}{b - a}$$\nOn $f(x) = x^2$, find the slope from $x = 2$ to each point below. Watch the slopes as the second point closes in. (The **Calc** button is at the top.)',
                  'parts': [{'label': 'to $x = 3$:', 'answer': 5, 'tol': 0.0005}, {'label': 'to $x = 2.5$:', 'answer': 4.5, 'tol': 0.0005}, {'label': 'to $x = 2.1$:', 'answer': 4.1, 'tol': 0.0005}, {'label': 'to $x = 2.01$:', 'answer': 4.01, 'tol': 0.0005}],
                  'picture': False, 'hint': 'For $x = 3$: $frac{9 - 4}{3 - 2}$. For $x = 2.5$: $frac{6.25 - 4}{0.5}$.', 'explain': '5, 4.5, 4.1, 4.01: the secant slopes are settling on **4**.'})
    s1 = S(d, 'L1')
    s1['title'] = 'Watch it happen'
    s1['text'] = 'Slide the teal point toward the black point at $x = 2$ and watch the secant line turn into the tangent line.'
S(d, 'L3')['text'] = "$$f'(a) = lim[h->0] frac{f(a+h) - f(a)}{h}$$\nUse the definition to find $f'(1)$ for $f(x) = x^2 + x$, one line at a time."
th = d['drills']['theory']['questions']
th[:] = [q for q in th if q['id'] != 'T6']
for q in th:
    if q['id'] == 'T4':
        q['pairs'] = [['Secant line', 'a line through two points of the curve'], ['Tangent line', 'a line that touches the curve at one point and has the curve’s slope there'],
                      ['Difference quotient', 'the slope of a secant line'], ["Derivative $f'(a)$", 'the slope of the tangent line at $x = a$']]
save(d)

# ---------------------------------------------------------------- Derivative rules
d = load('d-rules')
s = S(d, 'L3')
s['text'] = "**Product rule:** if $f = gk$, then\n$$f' = gk' + g'k$$\nTake\n$$f(x) = (x^2 + 2)(3x + 1)$$"
s['steps'][0]['label'] = "$g = x^2 + 2$, so $g'$ ="
s['steps'][1]['label'] = "$k = 3x + 1$, so $k'$ ="
s['steps'][2] = product_bank('L3.3', 'f′(x)', '$x^2 + 2$', '$3$', '$2x$', '$3x + 1$', "$f'(x) = 3(x^2 + 2) + 2x(3x + 1)$", "$g$ times $k'$, plus $g'$ times $k$.")
s = S(d, 'L4')
s['text'] = "**Quotient rule**\n$$(frac{g}{k})' = frac{kg' - gk'}{k^2}$$\n“Low d-high minus high d-low, over low squared.” Take\n$$f(x) = frac{4x^2}{2x + 1}$$"
s['steps'][0]['label'] = "top $g = 4x^2$, so $g'$ ="
s['steps'][1]['label'] = "bottom $k = 2x + 1$, so $k'$ ="
s['steps'][2] = quotient_bank('L4.3', 'f′(x)', '$4x^2$', '$8x$', '$2x + 1$', '$2$', '(2x + 1)²', "$f'(x) = frac{(2x + 1)(8x) - 8x^2}{(2x + 1)^2}$", 'Low is the bottom, $2x + 1$. High is the top, $4x^2$.')
save(d)

# ---------------------------------------------------------------- Trig
d = load('d-trig')
s = S(d, 'L2'); s.clear()
s.update({'id': 'L2', 'type': 'dtrace', 'title': 'The slopes of cosine', 'text': 'Now $f(x) = cos(x)$. Slide again. At $x = 0$ the curve is at its peak, so the slope is 0. Then it goes **downhill**.',
          'fn': 'cos(x)', 'window': [-6.4, 6.4, -1.6, 1.6], 'dwindow': [-1.6, 1.6], 'xstep': 2, 'ystep': 1, 'dstep': 1,
          'after': 'The slopes of $cos(x)$ trace out an upside-down sine. So $frac{d}{dx} cos(x) = -sin(x)$. Mind the minus sign.'})
s = S(d, 'L3')
s['text'] = 'Trig functions follow all the same rules. Use the product rule on\n$$y = x^2 sin(x)$$'
s['steps'][0].update(text='', label="$g = x^2$, so $g'$ =")
s['steps'][1].update(text='', label="$k = sin(x)$, so $k'$ =")
s['steps'][2] = product_bank('L3.3', 'y′', '$x^2$', '$cos(x)$', '$2x$', '$sin(x)$', "$y' = x^2 cos(x) + 2x sin(x)$", "$g$ times $k'$, plus $g'$ times $k$.")
d['drills']['theory']['questions'] = [q for q in d['drills']['theory']['questions'] if q['id'] != 'T4']
save(d)

# ---------------------------------------------------------------- Exponentials
d = load('d-exp')
s = S(d, 'L5')
s['steps'] = [
    {'id': 'L5.1', 'type': 'mc', 'text': 'The top is $g = e^(x^2)$. It needs the chain rule.', 'options': ['$2x e^(x^2)$', '$e^(x^2)$', '$x^2 e^(x^2 - 1)$', '$e^(2x)$'], 'answer': 0,
     'hint': '$e^(x^2)$ times the derivative of $x^2$.', 'work': "$g' = 2x e^(x^2)$"},
    {'id': 'L5.2', 'type': 'num', 'text': 'The bottom is $k = x$.', 'answer': 1, 'label': "$k'$ =", 'hint': 'The slope of $x$.', 'work': "$k' = 1$"},
    quotient_bank('L5.3', 'f′(x)', '$e^(x^2)$', '$2x e^(x^2)$', '$x$', '$1$', 'x²', "$f'(x) = frac{2x^2 e^(x^2) - e^(x^2)}{x^2}$", 'Low is the bottom, $x$. High is the top, $e^(x^2)$.')]
save(d)

# ---------------------------------------------------------------- Logs
d = load('d-log')
S(d, 'L1').update(text="Where does the derivative of $ln(x)$ come from? Start with what $ln$ means:\n$$y = ln(x) ;; e^y = x$$\nDifferentiate both sides of $e^y = x$. The left side needs the chain rule:\n$$e^y · y' = 1$$\nSolve for $y'$, then swap $e^y$ for $x$. What is $y'$?",
                  hint="$y' = frac{1}{e^y}$, and $e^y$ is $x$.")
s = S(d, 'L2'); keep = {k: s[k] for k in ('id',)}; s.clear()
s.update({'id': 'L2', 'type': 'bank', 'text': 'With the chain rule, the derivative of the inside goes over the inside:\n$$frac{d}{dx} ln(f(x)) = frac{f\'(x)}{f(x)}$$\nTry $y = ln(x^3 + 2x + 1)$.\ny′ = frac{___}{___}',
          'blanks': ['$3x^2 + 2$', '$x^3 + 2x + 1$'], 'distractors': ['$3x^2$', '$1$'], 'hint': 'Top: the derivative of $x^3 + 2x + 1$. Bottom: $x^3 + 2x + 1$ itself.', 'explain': '$frac{3x^2 + 2}{x^3 + 2x + 1}$'})
save(d)

d = load('d-logdiff')
S(d, 'L1')['text'] = '$$y = x^x$$\nThe power rule needs a constant power. The rule for $b^x$ needs a constant base. Neither fits.\nThe trick: take $ln$ of both sides, and use $ln(a^r) = r ln(a)$. What is $ln(y)$?'
save(d)

# ---------------------------------------------------------------- Implicit
d = load('d-implicit')
s = S(d, 'L4')
s['text'] = 'Find $frac{dy}{dx}$ for\n$$x^3 sin(y) + y = 4x + 3$$'
s['steps'][0] = {'id': 'L4.1', 'type': 'mc', 'text': 'Differentiate the left side: the product rule on $x^3 sin(y)$, plus the derivative of $y$.',
                 'options': ["$3x^2 sin(y) + x^3 cos(y) y' + y'$", "$3x^2 cos(y) y' + y'$", '$3x^2 sin(y) + x^3 cos(y) + 1$', "$3x^2 sin(y) + x^3 cos(y) y'$"], 'answer': 0,
                 'hint': "Every time you differentiate something with $y$ in it, a $y'$ appears.", 'work': "$3x^2 sin(y) + x^3 cos(y)y' + y' = 4$"}
s['steps'][2] = {'id': 'L4.3', 'type': 'bank', 'text': 'Divide.\ny′ = frac{___}{___}', 'blanks': ['$4 - 3x^2 sin(y)$', '$x^3 cos(y) + 1$'], 'distractors': ['$4$', '$x^3 cos(y)$'],
                 'hint': "Divide both sides by what multiplies $y'$.", 'work': "$y' = frac{4 - 3x^2 sin(y)}{x^3 cos(y) + 1}$"}
s = S(d, 'L5'); s.clear()
s.update({'id': 'L5', 'type': 'mc', 'text': "Back to the circle $x^2 + y^2 = 25$, where $y' = -frac{x}{y}$. At which point is the tangent line **vertical**?",
          'options': ['$(5, 0)$', '$(0, 5)$', '$(3, 4)$', '$(4, 3)$'], 'answer': 0, 'hint': 'A vertical line has no slope. Where is $-frac{x}{y}$ undefined?',
          'explain': "At $(5, 0)$ the bottom is 0, so the slope is undefined and the tangent is vertical. Notice that $y'$ needed both coordinates of the point."})
save(d)

# ---------------------------------------------------------------- Inverse trig
d = load('d-invtrig')
s = S(d, 'L1'); s.clear()
s.update({'id': 'L1', 'type': 'num', 'text': '$arcsin(x)$, also written $sin^(-1)(x)$, is the angle whose sine is $x$. Its derivative is one to memorize:\n$$frac{d}{dx} arcsin(x) = frac{1}{sqrt(1 - x^2)}$$\nUse it: what is the slope of $y = arcsin(x)$ at $x = 0$?',
          'answer': 1, 'label': 'slope =', 'hint': 'Put 0 in for $x$.', 'explain': '$frac{1}{sqrt(1 - 0)} = 1$. (The formula comes from implicit differentiation of $sin(y) = x$.)'})
S(d, 'L2')['text'] = 'Match each function to its derivative.'
S(d, 'L4').update(text='A triangle simplifies things like $sin(arccos(x))$. Let $theta = arccos(x)$, so $cos(theta) = x$: the adjacent side is $x$ and the hypotenuse is 1.\n{{triangle: 1 | ? | x | theta}}\nFind the missing side. Then $sin(arccos(x)) =$',
                  hint='Pythagoras: $x^2 + ?^2 = 1$. Sine is opposite over hypotenuse.', explain='The missing side is $sqrt(1 - x^2)$, and sine is that over 1.')
s = S(d, 'L5'); s.clear()
s.update(product_bank('L5', 'f′(x)', '$x$', '$frac{1}{1 + x^2}$', '$1$', '$arctan(x)$', '', "With $g = x$ and $k = arctan(x)$: $g' = 1$ and $k' = frac{1}{1 + x^2}$.",
                      text='Old rules still apply. Use the product rule, $gk\' + g\'k$, on\n$$f(x) = x arctan(x)$$'))
s.pop('work'); s['explain'] = '$f\'(x) = frac{x}{1 + x^2} + arctan(x)$'
save(d)

# ---------------------------------------------------------------- two more run-on lesson steps, in other worlds
d = load('l-cont')
S(d, 'L5')['text'] = '**Intermediate Value Theorem:** if $f$ is continuous on $[a, b]$, it hits every height between $f(a)$ and $f(b)$.\n$$f(x) = x^3 - x^2 - 3x + 1 ;; f(0) = 1 ;; f(1) = -2$$\nSo on $[0, 1]$ it…'
save(d)
d = load('w-ftc2')
S(d, 'L1')['text'] = '**The Fundamental Theorem, Part 2:** if $F$ is any antiderivative of $f$, then\n$$int[a,b] f(x) dx = F(b) - F(a)$$\nNo more rectangles! For $int[0,2] x^2 dx$, which $F$ can you use?'
save(d)
print('done')
