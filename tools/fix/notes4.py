"""Content fixes from Dallas's last review notes (Nov 17-20, 2026: Worlds 3 and 4, chapter reviews). One-time; safe to run again.
   python3 tools/fix/notes4.py"""
import json, os, re
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def load(dk):
    return json.load(open(os.path.join(ROOT, 'decks', dk + '.json')))


def save(d):
    with open(os.path.join(ROOT, 'decks', d['id'] + '.json'), 'w') as f:
        json.dump(d, f, indent=1, ensure_ascii=False); f.write('\n')


def sl(d):
    return [s for L in [d.get('lesson')] + list(d.get('lessons', [])) if L for s in L['slides']]


def S(d, i):
    return next(s for s in sl(d) if s.get('id') == i)


def Q(d, i):
    return next(q for dr in d['drills'].values() for q in dr['questions'] if q['id'] == i)


# ---------------------------------------------------------------- Integration
d = load('w-areas')
st = S(d, 'L3')['steps'][2]
st['text'] = 'The heights are $f(x) = x^2$ at each right endpoint:\n{{table: x | 0.5 | 1 | 1.5 | 2 ;; f(x) | 0.25 | 1 | 2.25 | 4}}\nAdd them up.'
st['hint'] = '0.25 + 1 + 2.25 + 4'
save(d)

d = load('w-anti')
S(d, 'L5')['text'] = '**Initial value problem:** a little extra information pins down $C$.\nSolve\n$$frac{dy}{dx} = 6x^2 ;; y(1) = 5$$'
Q(d, 'T3')['text'] = 'How can you check this answer?\n$$int x cos(x) dx ;; = x sin(x) + cos(x) + C$$'
Q(d, 'T4')['text'] = "Say $F' = f$ and $G' = g$. Then\n$$int (f(x) + g(x)) dx =$$"
Q(d, 'T5')['text'] = "Say $F' = f$, and $k$ is a constant. Then\n$$int kf(x) dx =$$"
save(d)

d = load('w-indef')
S(d, 'L4')['label'] = 'answer ='
S(d, 'L2')['label'] = 'answer ='
save(d)

d = load('w-definite')
q = Q(d, 'T3')
q['options'] = ['$-int[a,b] f(x) dx$', '$int[a,b] f(x) dx$', '0', '$2int[a,b] f(x) dx$']
q = Q(d, 'T5')
d['graphs']['lin2x'] = {'window': [-3.6, 3.6, -7, 7], 'pieces': [{'expr': '2*x', 'from': -3, 'to': 3}], 'vlines': [-3, 3], 'ystep': 2,
                        'labels': [[2.1, 1.4, 'area 9'], [-2.1, -1.6, 'area 9']]}
q.update(graph='lin2x', text='$f(x) = 2x$ on $[-3, 3]$. The region is two triangles, one above the axis and one below. Which is true?')
save(d)

d = load('w-subst')
s = S(d, 'L3'); s.clear()
s.update({'id': 'L3', 'type': 'steps', 'text': 'Your turn:\n$$int 3x^2(x^3 - 3)^2 dx$$', 'steps': [
    {'id': 'L3.1', 'type': 'mc', 'text': 'Let $u = x^3 - 3$. Then $du$ =', 'options': ['$3x^2 dx$', '$x^3 dx$', '$3x dx$', '$(x^3 - 3) dx$'], 'answer': 0,
     'hint': 'Differentiate $x^3 - 3$, then tack on $dx$.', 'work': '$du = 3x^2 dx$'},
    {'id': 'L3.2', 'type': 'mc', 'text': 'Swap in $u$ and $du$. The integral becomes', 'options': ['$int u^2 du$', '$int 3x^2 u^2 du$', '$int u du$', '$int u^3 du$'], 'answer': 0,
     'hint': '$(x^3 - 3)^2$ is $u^2$, and $3x^2 dx$ is $du$.', 'work': '$int u^2 du$'},
    {'id': 'L3.3', 'type': 'mc', 'text': 'Integrate, then put $x$ back in for $u$.', 'options': ['$frac{(x^3 - 3)^3}{3} + C$', '$frac{u^3}{3} + C$', '$(x^3 - 3)^3 + C$', '$frac{(x^3 - 3)^3}{9x^2} + C$'], 'answer': 0,
     'hint': '$int u^2 du = frac{u^3}{3} + C$. The answer should be in terms of $x$.', 'work': '$frac{(x^3 - 3)^3}{3} + C$'}]})
save(d)

d = load('w-ftc2')
s = S(d, 'L4')
s['text'] = 'A particle moves with velocity $v(t) = t^2 - 4t$ (m/s) for $0 <= t <= 6$. It moves backward while $v < 0$, which is for $0 < t < 4$. The two pieces are\n$$int[0,4] v dt = -frac{32}{3} ;; int[4,6] v dt = frac{32}{3}$$'
s['steps'][0].update(text='**Displacement** is the net change: add the two pieces as they are.', hint='$-frac{32}{3} + frac{32}{3}$')
s['steps'][1].update(text='**Total distance** counts both pieces as positive: add their sizes.', hint='$frac{32}{3} + frac{32}{3}$', tol=0.01)
s['steps'][1].pop('text2', None)
save(d)

# ---------------------------------------------------------------- Applications
d = load('opt')
PEN = 'The pen: 1200 ft of fence, width $x$, length $y$, with the river as the fourth side, so $2x + y = 1200$.\n'
s = S(d, 'L6')
if not s['text'].startswith('The pen'):
    s['text'] = PEN + 'What values of $x$ make sense?'
save(d)

d = load('opt2')
AREA = '$$A(x) = x(1200 - 2x)$$\n'
S(d, 'L8')['text'] = AREA + "$A'(x) = 1200 - 4x$. Set it equal to 0. The critical point is:"
S(d, 'L9')['text'] = AREA + 'How do we know $x$ = 300 is the maximum?'
S(d, 'L10')['text'] = AREA + 'Answer the question: what is the largest area?'
S(d, 'L11')['items'] = ['Draw a diagram and name the variables', 'Decide what to optimize (max or min)', 'Write an equation for what you are trying to optimize',
                        'Write the constraint, and use it to get down to one variable', 'Find the critical points', 'Check it is really a max or min, then answer the question']
save(d)

d = load('newton')
S(d, 'L9')['text'] = 'Same function. Do it by hand this time:\n1. Drag to pick a first guess $x_0$.\n2. Tap where the dashed tangent line crosses the $x$-axis. That is $x_1$.\n3. Repeat from the new point until the digits in the table stop changing.\nUse **Zoom +** to look closely.'
save(d)

d = load('linear')
S(d, 'N17')['text'] = 'Start at the dot. Move right by $dx$, then go up two ways: to the tangent line ($dy$) and to the curve ($Δy$).\nDrag the slider **left, toward 0**, until $dy$ and $Δy$ are within 0.01 of each other.'
save(d)

d = load('mvt')
s = S(d, 'M12'); s.clear()
s.update({'id': 'M12', 'type': 'steps', 'title': 'Find the $c$', 'text': '$$f(x) = sqrt(x) ;; [0, 9]$$', 'steps': [
    {'id': 'M12.1', 'type': 'num', 'text': 'Find the secant slope.', 'answer': 0.333333, 'tol': 0.002, 'label': 'slope =', 'hint': '$frac{sqrt(9) - sqrt(0)}{9 - 0}$', 'work': 'secant slope $= frac{1}{3}$'},
    {'id': 'M12.2', 'type': 'mc', 'text': "$f'(x) = frac{1}{2sqrt(x)}$. The MVT promises a $c$ where $f'(c) = frac{1}{3}$. Which one?", 'options': ['$c = 2.25$', '$c = 1.5$', '$c = 3$', '$c = 4.5$'], 'answer': 0,
     'hint': 'Try each: which makes $2sqrt(c) = 3$?', 'explain': '$sqrt(2.25) = 1.5$, so $frac{1}{2(1.5)} = frac{1}{3}$.'}]})
save(d)

d = load('incdec')
s = S(d, 'L6')
s.update(text="$$f'(x) = frac{x + 2}{x - 3}$$\nand $f$ is undefined at 3. Which $x$-values split the number line for the sign chart of $f'$?",
         options=['−2', '2', '3', '−3', '0'], answers=[0, 2],
         explain='The top is 0 at −2; the bottom is 0 at 3. A point where $f$ is undefined is not a critical number, but it still splits the sign chart.')
s = S(d, 'L7')
s.update(text="$$f'(x) = frac{x + 2}{x - 3}$$\nThat makes three pieces. Here is one test point in each:\n{{table: test x | −3 | 0 | 4 ;; f′(x) | 1/6 | −2/3 | 6}}\nWhere is $f$ increasing? (Use open intervals.)",
         answer='(-inf,-2)U(3,inf)', hint="Increasing where $f'$ is positive.",
         explain='Positive on $(-∞, -2)$ and $(3, ∞)$, negative on $(-2, 3)$.')
save(d)

d = load('concavity')
s = S(d, 'L15')
s['text'] = "Use the second derivative test on\n$$f(x) = x^3 - frac{3}{2}x^2 - 18x ;; f'(x) = 3x^2 - 3x - 18$$\nThe critical numbers are $c$ = 3 and $c$ = −2."
s['steps'][0]['text'] = "Differentiate $f'$ once more."
s['steps'][0]['hint'] = "The derivative of $3x^2 - 3x - 18$."
save(d)

d = load('curve')
d['lesson']['slides'] = [x for x in d['lesson']['slides'] if x.get('id') != 'L16']
S(d, 'L17')['text'] = 'Put it all together for\n$$f(x) = x^3 - 6x^2 + 9x + 1$$'
save(d)

d = load('lhop')
def boxlim(q):
    m = re.fullmatch(r'What form does \$(.+)\$ have\?', q.get('text', ''))
    if m:
        q['text'] = 'What form does this limit have?\n$$' + m.group(1) + '$$'
for q in [x for dr in d['drills'].values() for x in dr['questions']] + sl(d):
    boxlim(q)
for s in sl(d):
    if s.get('id') == 'O1':
        s['pairs'] = [['$0·∞$', 'Move one factor to the bottom: $fg = frac{f}{1/g}$'], ['$∞ - ∞$', 'Combine into one fraction (common denominator or conjugate)'],
                      ['$1^(∞)$, $0^0$ and $∞^0$', 'Take $ln$: the exponent comes down']]
        s['explain'] = 'Products become quotients, differences become one fraction, and all three powers get a logarithm.'
        s['hint'] = 'The three power forms all use the same move.'
save(d)

d = load('review3')
for q in [x for dr in d['drills'].values() for x in dr['questions']] + sl(d):
    boxlim(q)
s = S(d, 'L8')
s['steps'][1] = {'type': 'expr', 'text': 'Plug in $r = 10$ and $r\' = 3$.', 'answer': '60*pi', 'vars': [], 'keys': ['pi'], 'label': "$A'$ =", 'show': '$60pi$',
                 'explain': '$2pi(10)(3) = 60pi ≈ 188.5$ cm²/s.', 'hint': '$2pi(10)(3)$'}
s = S(d, 'L9')
s['steps'][2].update(text="$P'(x) = 20 - 2x$. Set it equal to 0. Best $x$:", hint='$20 - 2x = 0$')
save(d)
print('done')
