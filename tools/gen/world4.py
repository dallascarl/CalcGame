"""World 4 (Integration): short lesson, theory set (all required) and a practice pool for each stop.
See lib.py before re-running: it overwrites decks."""
import random, re
import sympy as sp
from lib import *

R = random.Random(4044)


def F(name, s):
    return f'${name} = {D(s)}$'


def I(s, var='x'):
    """the indefinite integral sign around s"""
    return f'$int {D(s, False)} d{var}$'


def Idef(s, lo, hi, var='x'):
    return f'$int[{lo},{hi}] {D(s, False)} d{var}$'


def tsub(s, new):
    return re.sub(r'(?<![a-z])t(?![a-z])', new, s)


def anti(s, var='x'):
    v = sp.Symbol(var)
    return sp.integrate(S(s), v)


# ====================================================================== 1. Areas and distance
def deck_areas():
    d = Deck('w-areas', 'Areas and Distance', 'Rectangles that fill in the area under a curve.', 'Integration')
    L = []
    L.append({'id': 'L1', 'type': 'riemann', 'title': 'Fill it with rectangles',
              'text': 'How much area is under $f(x) = x^2$ from $x = 0$ to $x = 2$? Fill it with rectangles. Slide $n$ up, and try both left and right endpoints.',
              'fn': 'x^2', 'a': 0, 'b': 2, 'window': [-0.3, 2.3, -0.4, 4.4], 'exact': 8 / 3, 'rules': ['left', 'right'], 'n': 2, 'goal': 32,
              'after': 'Left rectangles sit under the curve and right ones stick out above it ($x^2$ is increasing). Both close in on the exact area, $frac{8}{3} ≈ 2.667$.'})
    L.append(MC('L2', 'Cut $[a, b]$ into $n$ rectangles of equal width. The width of each one is', ['$Delta x = frac{b - a}{n}$', '$Delta x = frac{n}{b - a}$', '$Delta x = b - a$', '$Delta x = frac{a + b}{2}$'],
                hint='Split the length of the interval into $n$ equal pieces.', explain='$Delta x = frac{b - a}{n}$'))
    L.append(STEPS('L3', 'Estimate the area under $f(x) = x^2$ on $[0, 2]$ with $R_4$ (4 rectangles, right endpoints).', [
        N('L3.1', '', 0.5, label='$Delta x$ =', hint='$frac{2 - 0}{4}$', work='$Delta x = 0.5$'),
        MC('L3.2', 'The right endpoints are', ['0.5, 1, 1.5, 2', '0, 0.5, 1, 1.5', '0.25, 0.75, 1.25, 1.75', '1, 2, 3, 4'], hint='Start one step in from 0 and end at 2.',
           work='right endpoints: 0.5, 1, 1.5, 2'),
        N('L3.3', 'Add up the heights: $f(0.5) + f(1) + f(1.5) + f(2)$.', 7.5, label='sum of heights =', hint='0.25 + 1 + 2.25 + 4', work='heights add to 7.5'),
        N('L3.4', 'Multiply by the width.', 3.75, label='$R_4$ =', hint='$0.5 × 7.5$', work='$R_4 = 3.75$'),
    ]))
    L.append(MC('L4', '$f(x) = x^2$ is **increasing** on $[0, 2]$. The left endpoint sum $L_4$ is', ['an underestimate', 'an overestimate', 'exactly right', 'impossible to tell'],
                hint='Each left rectangle uses the lowest height on its piece.', explain='For an increasing function, left sums are too small and right sums are too big.'))
    L.append(MC('L5', 'The same idea gives **distance**. A car drives 30 mph for 2 hours, then 60 mph for 1 hour. The distance is the area under the velocity graph:', ['120 miles', '90 miles', '45 miles', '180 miles'],
                hint='Two rectangles: $30 × 2$ and $60 × 1$.', explain='Distance = speed × time for each piece: 60 + 60 = 120 miles.'))
    d.lesson(L)

    T = [
        MC('T1', 'Cut $[1, 5]$ into $n = 8$ equal pieces. Each has width', ['$frac{1}{2}$', '$frac{1}{8}$', '4', '$frac{5}{8}$'], explain='$frac{5 - 1}{8} = frac{1}{2}$'),
        MC('T2', 'A **left** endpoint sum uses the heights at', ['$x_0, x_1, …, x_(n-1)$', '$x_1, x_2, …, x_n$', 'the midpoints', 'the highest point of each piece'], explain='Left: start at $x_0 = a$, stop one short of $b$.'),
        TF('T3', 'For an increasing function, the right endpoint sum is an overestimate.', True, explain='Each right rectangle uses the tallest height on its piece.'),
        MC('T4', 'As the number of rectangles $n$ grows, the sum', ['gets closer to the exact area', 'always gets bigger', 'always gets smaller', 'stays the same'], explain='The exact area is the limit as $n -> infty$.'),
        MC('T5', 'The area under a velocity graph from $t = a$ to $t = b$ gives', ['the distance traveled', 'the acceleration', 'the average velocity', 'the final position'], explain='Speed × time, added up.'),
        MC('T6', 'Which is the right endpoint sum in sigma notation?', ['$sum[i=1,n] f(x_i) Delta x$', '$sum[i=1,n] f(x_(i-1)) Delta x$', '$sum[i=1,n] x_i Delta x$', '$sum[i=1,n] f(Delta x)$'],
           explain='Right endpoints are $x_1$ through $x_n$.'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    for a0, b0, n in [(0, 2, 4), (1, 5, 8), (0, 3, 6), (2, 4, 5), (-1, 1, 4), (0, 1, 10), (3, 6, 6), (0, 10, 5)]:
        dx = sp.Rational(b0 - a0, n)
        Q.append(N(d.qid('X'), f'Find $Delta x$ for $n = {n}$ rectangles on $[{a0}, {b0}]$.', dx, label='$Delta x$ =', level=1, explain=f'$frac{{{b0} - ({a0})}}{{{n}}} = {frac_str(dx)}$'))
    for a0, b0, n, i in [(0, 2, 4, 3), (1, 5, 8, 2), (0, 3, 6, 5), (2, 4, 5, 1), (-1, 1, 4, 3), (0, 1, 10, 7), (3, 6, 6, 4), (0, 10, 5, 2)]:
        dx = sp.Rational(b0 - a0, n)
        Q.append(N(d.qid('E'), f'$[{a0}, {b0}]$ is cut into $n = {n}$ pieces, with $x_i = a + i Delta x$. Find $x_{i}$.', a0 + i * dx, label=f'$x_{i}$ =', level=1,
                   explain=f'$Delta x = {frac_str(dx)}$, so $x_{i} = {a0} + {i}·{frac_str(dx)} = {frac_str(a0 + i * dx)}$.'))
    fns = [('x^2', 0, 2, 4), ('x^2 + 1', 0, 3, 3), ('2x + 1', 0, 4, 4), ('10 - x^2', 1, 2, 4), ('x^3', 0, 2, 2), ('4 - x', 0, 4, 4), ('x^2', 1, 3, 4), ('sqrt(x)', 0, 4, 4),
           ('1/x', 1, 3, 2), ('x^2 - x', 1, 4, 3)]
    for k, (f, a0, b0, n) in enumerate(fns):
        fe = S(f)
        dx = sp.Rational(b0 - a0, n)
        rule = 'left' if k % 2 == 0 else 'right'
        pts = [a0 + i * dx for i in (range(n) if rule == 'left' else range(1, n + 1))]
        hs = [fe.subs(x, p) for p in pts]
        val = dx * sum(hs)
        nm = ('L' if rule == 'left' else 'R') + f'_{n}'
        Q.append(N(d.qid('S'), f'Find ${nm}$ for {F("f(x)", f)} on $[{a0}, {b0}]$ ({rule} endpoints, $n = {n}$).', val, label=f'${nm}$ =', tol=0.01, level=2,
                   explain=f'$Delta x = {frac_str(dx)}$ and the heights at $x$ = {", ".join(frac_str(p) for p in pts)} add to {num(sum(hs))}, so ${nm} = {num(val)}$.'))
        Q.append(STEPS(d.qid('W'), f'Estimate the area under {F("f(x)", f)} on $[{a0}, {b0}]$ with ${nm}$.', [
            N(None, '', dx, label='$Delta x$ =', work=f'$Delta x = {frac_str(dx)}$'),
            N(None, f'Add the heights at the {rule} endpoints, $x$ = {", ".join(frac_str(p) for p in pts)}.', sum(hs), label='sum of heights =', tol=0.01,
              work=f'heights add to {num(sum(hs))}'),
            N(None, 'Multiply by the width.', val, label=f'${nm}$ =', tol=0.01, work=f'${nm} = {num(val)}$'),
        ], level=3, explain=f'${nm} = {num(val)}$'))
    for f, inc in [('x^2 on [0, 3]', True), ('10 - x^2 on [0, 3]', False), ('e^x on [0, 1]', True), ('frac{1}{x} on [1, 4]', False), ('sqrt(x) on [1, 9]', True), ('cos(x) on [0, frac{pi}{2}]', False)]:
        for rule in ['left', 'right']:
            over = (rule == 'right') == inc
            Q.append(MC(d.qid('O'), f'$f(x) = {f.split(" on ")[0]}$ on ${f.split(" on ")[1]}$ is {"increasing" if inc else "decreasing"}. Is the {rule} endpoint sum an over- or underestimate?',
                        ['an overestimate', 'an underestimate'], 0 if over else 1, fixed=True, level=2,
                        explain=f'{"Increasing" if inc else "Decreasing"}: the {rule} endpoints give the {"tallest" if over else "shortest"} height on each piece.'))
    for ts, vs, rule in [([0, 1, 2, 3], [10, 14, 20, 24], 'left'), ([0, 2, 4, 6], [5, 8, 6, 9], 'right'), ([0, 1, 2, 3, 4], [0, 3, 8, 15, 24], 'left'), ([0, 5, 10, 15], [30, 28, 25, 20], 'right')]:
        dt = ts[1] - ts[0]
        use = vs[:-1] if rule == 'left' else vs[1:]
        tab = ' · '.join(f'$v({a_}) = {b_}$' for a_, b_ in zip(ts, vs))
        Q.append(N(d.qid('V'), f'Velocity readings (ft/s): {tab}. Estimate the distance traveled with {rule} endpoints.', dt * sum(use), label='distance =', level=3,
                   explain=f'Each piece lasts {dt} s. Using the {rule} readings: ${dt} × ({" + ".join(map(str, use))}) = {dt * sum(use)}$ ft.'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== review: summation notation
def deck_sumnot():
    d = Deck('w-sumnot', 'Summation Notation', 'Review: reading and adding up Σ sums.', 'Integration')
    L = [
        N('L1', '$sum[i=1,4] (2i + 1)$ means: plug in $i = 1, 2, 3, 4$ and add. $3 + 5 + 7 + 9 =$', 24, label='sum =', hint='Add the four numbers.', explain='24'),
        MC('L2', 'Which sum is $25 + 21 + 17 + 13 + 9 + 5 + 1 - 3$?', ['$sum[k=0,7] (25 - 4k)$', '$sum[k=1,8] (25 - 4k)$', '$sum[k=0,7] (25 + 4k)$', '$sum[k=0,7] 4k$'],
           hint='It starts at 25 and goes down by 4 each time.', explain='$k = 0$ gives 25, and $k = 7$ gives $-3$.'),
        N('L3', 'Formulas help with long sums: $sum[k=1,n] k = frac{n(n + 1)}{2}$. Find $sum[k=1,100] k$.', 5050, label='sum =', hint='$frac{100·101}{2}$', explain='5050'),
    ]
    d.lesson(L, optional=True)
    Q = []
    small = [('k', 1, 6), ('k^2 - 5', 3, 5), ('1/k', 1, 3), ('5', 1, 5), ('2i + 1', 1, 4), ('k^2', 1, 4), ('3k - 1', 1, 5), ('(-1)^k', 1, 5), ('2^k', 0, 4), ('k(k + 1)', 1, 3),
             ('10 - k', 1, 4), ('k^3', 1, 3), ('(2k + 1)^2', 1, 3), ('1/2^k', 1, 3)]
    for f, lo, hi in small:
        var = 'i' if 'i' in f else 'k'
        v = sp.Symbol(var)
        val = sp.summation(S(f.replace('i', 'k')).subs(sp.Symbol('k'), v) if var == 'i' else S(f), (v, lo, hi))
        Q.append(N(d.qid('A'), f'Find $sum[{var}={lo},{hi}] {D(f, False)}$.', val, label='sum =', level=1,
                   explain=f'Plug in {var} = {lo} to {hi} and add: {frac_str(val)}.'))
    for c, n in [(5, 5), (7, 10), (3, 20), (-2, 6)]:
        Q.append(N(d.qid('C'), f'Find $sum[k=1,{n}] {c}$.', c * n, label='sum =', level=1, explain=f'{n} copies of {c}: $sum[k=1,n] c = nc = {c * n}$.'))
    for n in [10, 20, 50, 100]:
        Q.append(N(d.qid('F'), f'Use $sum[k=1,n] k = frac{{n(n + 1)}}{{2}}$ to find $sum[k=1,{n}] k$.', n * (n + 1) // 2, label='sum =', level=2, explain=f'$frac{{{n}·{n + 1}}}{{2}} = {n * (n + 1) // 2}$'))
    for n in [5, 10, 20]:
        Q.append(N(d.qid('G'), f'Use $sum[k=1,n] k^2 = frac{{n(n + 1)(2n + 1)}}{{6}}$ to find $sum[k=1,{n}] k^2$.', n * (n + 1) * (2 * n + 1) // 6, label='sum =', level=2,
                   explain=f'$frac{{{n}·{n + 1}·{2 * n + 1}}}{{6}} = {n * (n + 1) * (2 * n + 1) // 6}$'))
    for f, n, val_expr in [('2k - k^2', 8, None), ('k^3 - k', 100, None), ('(2k + 1)^2', 10, None), ('3k + 2', 20, None)]:
        val = sp.summation(S(f), (sp.Symbol('k'), 1, n))
        Q.append(N(d.qid('H'), f'Find $sum[k=1,{n}] ({D(f, False)})$. Split it up and use the formulas.', val, label='sum =', level=3,
                   explain=f'Split into separate sums, use the formulas for $sum k$, $sum k^2$ and $sum k^3 = (frac{{n(n+1)}}{{2}})^2$: {num(val)}.'))
    for A_, B_, ca, cb in [(10, 4, 3, -1), (6, 2, 2, 5), (12, -3, 1, 1), (8, 5, -1, 2), (7, 1, 4, 0), (20, 6, 1, -2)]:
        Q.append(N(d.qid('P'), f'$sum[k=1,n] a_k = {A_}$ and $sum[k=1,n] b_k = {B_}$. Find $sum[k=1,n] ({ca}a_k + {cb}b_k)$.'.replace('+ -', '- ').replace('(1a', '(a').replace('+ 1b', '+ b').replace('+ 0b_k', ''),
                   ca * A_ + cb * B_, label='sum =', level=2, explain=f'Sums split and constants come out: ${ca}({A_}) + {cb}({B_}) = {ca * A_ + cb * B_}$.'))
    for seq, r_, w_ in [('$2 + 4 + 6 + 8 + 10$', '$sum[k=1,5] 2k$', ['$sum[k=2,10] k$', '$sum[k=1,10] 2k$', '$sum[k=1,5] (k + 2)$']),
                        ('$1 + 4 + 9 + 16$', '$sum[k=1,4] k^2$', ['$sum[k=1,4] 2k$', '$sum[k=1,16] k$', '$sum[k=1,4] (k + 3)$']),
                        ('$frac{1}{2} + frac{1}{3} + frac{1}{4}$', '$sum[k=2,4] frac{1}{k}$', ['$sum[k=1,3] frac{1}{k}$', '$sum[k=2,4] k$', '$sum[k=1,4] frac{1}{2k}$']),
                        ('$3 + 3 + 3 + 3 + 3 + 3$', '$sum[k=1,6] 3$', ['$sum[k=1,3] 6$', '$sum[k=1,6] k$', '$sum[k=3,6] 3$'])]:
        Q.append(MC(d.qid('W'), f'Write {seq} in sigma notation.', [r_] + w_, level=2, explain=r_))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 2. The definite integral
def pw_graph(pts):
    """a piecewise-linear graph through integer points"""
    pieces = []
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        m = sp.Rational(y1 - y0, x1 - x0)
        e = sp.expand(y0 + m * (x - x0))
        pieces.append({'expr': str(e).replace('**', '^'), 'from': x0, 'to': x1})
    return pieces


def pw_int(pts, a0, b0):
    tot = 0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        lo, hi = max(a0, x0), min(b0, x1)
        if lo >= hi:
            continue
        m = sp.Rational(y1 - y0, x1 - x0)
        tot += sp.integrate(y0 + m * (x - x0), (x, lo, hi))
    return tot


def deck_definite():
    d = Deck('w-definite', 'The Definite Integral', 'The exact area, as a limit of rectangle sums.', 'Integration')
    gT = d.graph('trap', {'window': [-0.5, 4.5, -0.5, 9.5], 'pieces': [{'expr': '2*x+1', 'from': 0, 'to': 4}], 'vlines': [4], 'ystep': 1})
    gC = d.graph('quarter', {'window': [-0.5, 3.5, -0.5, 3.5], 'pieces': [{'expr': 'sqrt(9-x^2)', 'from': 0, 'to': 3}]})
    gS = d.graph('sine', {'window': [-3.4, 3.4, -1.4, 1.4], 'pieces': [{'expr': 'sin(x)', 'from': -3.1416, 'to': 3.1416}]})
    L = []
    L.append(MC('L1', 'The **definite integral** is the exact area: the limit of the rectangle sums.\n$int[a,b] f(x) dx = lim[n->infty] sum[i=1,n] f(x_i) Delta x$\nThe $int$ sign is a stretched-out S. S for…',
                ['Sum', 'Slope', 'Square', 'Second'], hint='What do the rectangles do?', explain='It adds up (sums) infinitely many thin rectangles $f(x) dx$.'))
    L.append(dict(N('L2', 'Often geometry does the work. Find $int[0,4] (2x + 1) dx$, the area under this line: a trapezoid.', 20, label='integral =',
                    hint='Heights 1 and 9, width 4: $frac{1 + 9}{2}·4$.', explain='$frac{1 + 9}{2}·4 = 20$'), graph=gT))
    L.append(dict(N('L3', '$int[0,3] sqrt(9 - x^2) dx$ is a quarter of a circle of radius 3. Find it (a decimal is fine).', 9 * sp.pi / 4, label='integral =', tol=0.01,
                    hint='A full circle has area $pi r^2$. Take a quarter.', explain='$frac{1}{4}pi(3^2) = frac{9pi}{4} ≈ 7.07$'), graph=gC))
    L.append(dict(MC('L4', 'Area **below** the $x$-axis counts as negative. What is $int[-pi,pi] sin(x) dx$?', ['0', '2', '4', '$-2$'],
                     hint='The part below the axis exactly cancels the part above.', explain='The two humps are the same size with opposite signs, so they cancel: 0.'), graph=gS))
    L.append(N('L5', 'Integrals split and combine like sums. $int[1,3] f(x) dx = 10$, $int[3,5] f(x) dx = 3$ and $int[1,5] g(x) dx = 9$. Find $int[1,5] (3f(x) - g(x)) dx$.', 30,
               label='integral =', hint='First $int[1,5] f = 10 + 3$. Then $3·13 - 9$.', explain='$int[1,5] f = 13$, so $3(13) - 9 = 30$.'))
    d.lesson(L)

    T = [
        TF('T1', 'If $f$ is continuous on $[a, b]$, then $f$ is integrable on $[a, b]$.', True, explain='Continuous functions always have a definite integral.'),
        MC('T2', '$int[a,a] f(x) dx =$', ['0', '$f(a)$', '$a$', '1'], explain='No width, no area.'),
        MC('T3', '$int[b,a] f(x) dx =$', ['$-int[a,b] f(x) dx$', '$int[a,b] f(x) dx$', '0', '$frac{1}{int[a,b] f(x) dx}$'], explain='Running backwards flips the sign.'),
        MC('T4', 'What is the difference between $int[0,2] x^2 dx$ and $int x^2 dx$?', ['The first is a number; the second is a family of functions', 'There is no difference', 'The first is a function; the second is a number', 'The second is always bigger'],
           explain='Definite integrals give numbers (areas). Indefinite integrals give antiderivatives $+ C$.'),
        MC('T5', '$f(x) = 2x$ on $[-3, 3]$. Which is true?', ['The net signed area is 0 but the total area is 18', 'The net signed area is 18', 'Both are 0', 'Both are 18'],
           explain='Two triangles of area 9, one below the axis: $-9 + 9 = 0$, but total area $9 + 9 = 18$.'),
        TF('T6', 'If $f(x) >= g(x)$ on $[a, b]$, then $int[a,b] f(x) dx >= int[a,b] g(x) dx$.', True, explain='A taller function has more area under it.'),
        MC('T7', '$int[a,b] c dx$ for a constant $c$ is', ['$c(b - a)$', '$c$', '$cb$', '0'], explain='A rectangle of height $c$ and width $b - a$.'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    shapes = [[(0, 2), (2, 2), (4, 0), (6, -2)], [(0, 0), (2, 4), (4, 4), (6, 0)], [(0, 3), (3, 0), (6, 3)], [(0, -2), (2, 2), (4, 2), (6, -2)], [(0, 4), (4, 0), (6, -2)]]
    for k, pts in enumerate(shapes):
        g = d.graph(f'pw{k}', {'window': [-0.5, 6.5, -3, 5], 'pieces': pw_graph(pts)})
        for a0, b0 in [(0, 2), (0, 4), (2, 6), (0, 6)]:
            val = pw_int(pts, a0, b0)
            lv = 1 if all(pw_int(pts, a0, b0) * 0 == 0 for _ in [0]) and min(p[1] for p in pts if a0 <= p[0] <= b0) >= 0 else 2
            q = N(d.qid('G'), f'Use the graph of $f$ (straight-line pieces). Find $int[{a0},{b0}] f(x) dx$. Area below the axis counts as negative.', val, label='integral =', level=lv,
                  explain=f'Add the triangles and rectangles, with a minus sign below the axis: {frac_str(val)}.')
            q['graph'] = g
            Q.append(q)
    for r_, a0, b0, frac_, desc in [(2, -2, 2, sp.Rational(1, 2), 'half of a circle of radius 2'), (3, 0, 3, sp.Rational(1, 4), 'a quarter of a circle of radius 3'),
                                    (4, -4, 4, sp.Rational(1, 2), 'half of a circle of radius 4'), (1, -1, 1, sp.Rational(1, 2), 'half of a circle of radius 1')]:
        g = d.graph(f'circ{r_}{a0}', {'window': [-r_ - 0.5, r_ + 0.5, -0.5, r_ + 0.5], 'pieces': [{'expr': f'sqrt({r_ * r_}-x^2)', 'from': a0, 'to': b0}]})
        q = N(d.qid('C'), f'Find $int[{a0},{b0}] sqrt({r_ * r_} - x^2) dx$. (It is {desc}. A decimal is fine.)', frac_ * sp.pi * r_ ** 2, label='integral =', tol=0.01, level=2,
              explain=f'${frac_str(frac_)}·pi({r_})^2 = {num(frac_ * sp.pi * r_ ** 2)}$')
        q['graph'] = g
        Q.append(q)
    props = [('$int[0,3] f = 5$ and $int[3,7] f = 2$.', '$int[0,7] f(x) dx$', 7), ('$int[1,4] f = 8$.', '$int[4,1] f(x) dx$', -8), ('$int[2,6] f = 9$.', '$int[2,6] 4f(x) dx$', 36),
             ('$int[0,5] f = 3$ and $int[0,5] g = -2$.', '$int[0,5] (f(x) + g(x)) dx$', 1), ('$int[0,5] f = 3$ and $int[0,5] g = -2$.', '$int[0,5] (2f(x) - 3g(x)) dx$', 12),
             ('$int[1,9] f = 20$ and $int[1,4] f = 6$.', '$int[4,9] f(x) dx$', 14), ('$f$ is any function.', '$int[3,3] f(x) dx$', 0), ('$int[0,2] f = 4$.', '$int[0,2] (f(x) + 1) dx$', 6),
             ('$int[1,3] f = 10$, $int[3,5] f = 3$ and $int[1,5] g = 9$.', '$int[1,5] (3f(x) - g(x)) dx$', 30), ('$int[-2,2] f = 6$ and $int[0,2] f = 1$.', '$int[-2,0] f(x) dx$', 5),
             ('$int[0,4] f = 7$.', '$int[4,0] 2f(x) dx$', -14), ('nothing else is needed.', '$int[2,7] 3 dx$', 15)]
    for given, ask, val in props:
        Q.append(N(d.qid('P'), f'Given {given} Find {ask}.', val, label='integral =', level=2 if '-' in ask or '3f' in ask else 1,
                   explain=f'Use the properties of integrals: {val}.'))
    for m in [2, 1, 3]:
        g = d.graph(f'line{m}', {'window': [-3.5, 3.5, -3 * m - 1, 3 * m + 1], 'pieces': [{'expr': f'{m}*x', 'from': -3, 'to': 3}]})
        q = N(d.qid('N'), f'$f(x) = {m}x$ on $[-3, 3]$. Find the **total** area between the graph and the $x$-axis.', 9 * m, label='total area =', level=2,
              explain=f'Two triangles each of area $frac{{1}}{{2}}·3·{3 * m} = {sp.Rational(9 * m, 2)}$, both counted positive: {9 * m}.')
        q['graph'] = g
        Q.append(q)
        q = N(d.qid('N'), f'$f(x) = {m}x$ on $[-3, 3]$. Find the **net signed** area, $int[-3,3] {m}x dx$.', 0, label='integral =', level=2,
              explain='The triangle below the axis cancels the one above: 0.')
        q['graph'] = g
        Q.append(q)
    for f1, f2, a0, b0, big in [('x^2', 'e^x + 1', 3, 5, 1), ('sqrt(x)', 'x', 0, 1, 0), ('1/x', 'x', 2, 3, 1), ('sin(x)', '1', 0, 3, 1), ('x^3', 'x^2', 0, 1, 1)]:
        v1, v2 = float(sp.integrate(S(f1), (x, a0, b0))), float(sp.integrate(S(f2), (x, a0, b0)))
        assert (v2 > v1) == bool(big), (f1, f2)
        Q.append(MC(d.qid('B'), f'Which is bigger: $int[{a0},{b0}] {D(f1, False)} dx$ or $int[{a0},{b0}] {D(f2, False)} dx$?', [f'$int[{a0},{b0}] {D(f1, False)} dx$', f'$int[{a0},{b0}] {D(f2, False)} dx$'],
                    big, fixed=True, level=3, explain=f'On $[{a0}, {b0}]$ one function is always at least as big as the other, so its integral is bigger.'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 3. Antiderivatives
POW_ANTI = [('x^5', 'x^6/6'), ('x^3', 'x^4/4'), ('3x^2', 'x^3'), ('4x^3', 'x^4'), ('x', 'x^2/2'), ('7', '7x'), ('x^(-2)', '-1/x'), ('1/x^3', '-1/(2x^2)'), ('sqrt(x)', '(2/3)x^(3/2)'),
            ('x^(2/3)', '(3/5)x^(5/3)'), ('6x^5', 'x^6'), ('1/sqrt(x)', '2sqrt(x)'), ('10x^4', '2x^5'), ('x^(1/3)', '(3/4)x^(4/3)'), ('4/x^3', '-2/x^2'), ('x^9', 'x^10/10')]
BASIC_ANTI = [('cos(x)', 'sin(x)'), ('sin(x)', '-cos(x)'), ('sec(x)^2', 'tan(x)'), ('e^x', 'e^x'), ('1/x', 'ln(x)'), ('4/(x^2 + 1)', '4arctan(x)'), ('3x^2 + 2x', 'x^3 + x^2'),
              ('x^5 + 2', 'x^6/6 + 2x'), ('2sec(x)^2', '2tan(x)'), ('5e^x - x', '5e^x - x^2/2'), ('2cos(x) + 3sin(x)', '2sin(x) - 3cos(x)'), ('1/sqrt(1 - x^2)', 'arcsin(x)'),
              ('x^2 - 4x + 1', 'x^3/3 - 2x^2 + x'), ('sec(x)tan(x)', 'sec(x)'), ('3/x', '3ln(x)'), ('e^x + x^e', 'e^x + x^(e + 1)/(e + 1)')]
AK = ['sin(', 'cos(', 'tan(', 'sqrt(', 'e^(', 'ln(']


def deck_anti():
    d = Deck('w-anti', 'Antiderivatives', 'Running the derivative backwards.', 'Integration')
    d.keys = AK
    L = []
    L.append(MC('L1', '$F$ is an **antiderivative** of $f$ when $F\' = f$: you run the derivative backwards. Which is an antiderivative of $f(x) = 2x$?', ['$x^2$', '$2$', '$2x^2$', '$frac{1}{2x}$'],
                hint='Which one has derivative $2x$?', explain="$(x^2)' = 2x$"))
    L.append(MC('L2', '$frac{x^2}{2} + 3$ and $frac{x^2}{2} + 10$ are **both** antiderivatives of $x$. So the general antiderivative of $x$ is', ['$frac{x^2}{2} + C$', '$frac{x^2}{2}$', '$frac{x^2}{2} + 3$', '$x^2 + C$'],
                hint='Any constant disappears when you take the derivative.', explain='We write $int x dx = frac{x^2}{2} + C$, and yes, you need the $+ C$.'))
    L.append(E(d, 'L3', '**Anti-power rule:** $int x^n dx = frac{x^(n+1)}{n + 1} + C$ (for $n ≠ -1$). Raise the power by one and divide by the new power. Find $int x^5 dx$.', 'x^6/6', x ** 6 / 6,
               label='$int x^5 dx$ =', post='$+ C$', upToC=True, hint='New power: 6. Divide by 6.', explain='$frac{x^6}{6} + C$. Check: the derivative of $frac{x^6}{6}$ is $x^5$.'))
    L.append(MATCH('L4', 'Every derivative you know gives an antiderivative. Match each function to its antiderivative.', [['$cos(x)$', '$sin(x)$'], ['$sin(x)$', '$-cos(x)$'],
                   ['$sec^2(x)$', '$tan(x)$'], ['$e^x$', '$e^x$'], ['$frac{1}{x}$', '$ln|x|$']], hint='Read the derivative table backwards.', explain='Always add $+ C$.'))
    L.append(STEPS('L5', '**Initial value problem:** a little extra information pins down $C$. Solve $frac{dy}{dx} = 6x^2$ with $y(1) = 5$.', [
        E(d, 'L5.1', 'Find the general antiderivative.', '2x^3', 2 * x ** 3, label='$y$ =', post='$+ C$', upToC=True, hint='$int 6x^2 dx = 6·frac{x^3}{3}$', work='$y = 2x^3 + C$'),
        N('L5.2', 'Use $y(1) = 5$: $2(1)^3 + C = 5$.', 3, label='$C$ =', hint='$2 + C = 5$', work='$C = 3$'),
        E(d, 'L5.3', 'Write the solution.', '2x^3 + 3', 2 * x ** 3 + 3, label='$y$ =', hint='Put $C = 3$ back in.', work='$y = 2x^3 + 3$'),
    ]))
    d.lesson(L)

    T = [
        MC('T1', '$F$ is an antiderivative of $f$ means', ["$F'(x) = f(x)$", "$f'(x) = F(x)$", '$F(x) = frac{1}{f(x)}$', '$F(x) = f(x) + C$'], explain='The derivative of the antiderivative gives back $f$.'),
        TF('T2', 'The $+ C$ can be left off of an indefinite integral.', False, explain='Every antiderivative shifted up or down is still an antiderivative, so the answer is a whole family.'),
        MC('T3', 'How can you check that $int x cos(x) dx = x sin(x) + cos(x) + C$?', ['Take the derivative of $x sin(x) + cos(x)$', 'Take the derivative of $x cos(x)$', 'Plug in $x = 0$', 'You cannot check it'],
           explain="$(x sin(x) + cos(x))' = sin(x) + x cos(x) - sin(x) = x cos(x)$ ✓"),
        MC('T4', '$int (f(x) + g(x)) dx =$', ['$F(x) + G(x) + C$', '$F(x)G(x) + C$', '$f(x) + g(x) + C$', "$F'(x) + G'(x)$"], explain='Integrals go term by term.'),
        MC('T5', '$int kf(x) dx$ for a constant $k$ is', ['$kF(x) + C$', '$F(kx) + C$', '$k + F(x)$', '$frac{F(x)}{k} + C$'], explain='Constants come out front.'),
        MC('T6', 'The anti-power rule fails for $int x^(-1) dx$. What is it instead?', ['$ln|x| + C$', '$frac{x^0}{0} + C$', '$-x^(-2) + C$', '$e^x + C$'], explain='$(ln|x|)\' = frac{1}{x}$'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    for f, ans in POW_ANTI:
        Q.append(E(d, d.qid('P'), f'Find {I(f)}.', ans, anti(f), label=f'{I(f)} =', post='$+ C$', upToC=True, level=1,
                   explain=f'Raise the power by one and divide by the new power: ${D(ans)} + C$.'))
    ver = [('x sin(x) + cos(x)', 'x cos(x)', True), ('x^3 + 7', '3x^2', True), ('sin(x^2)', 'cos(x^2)', False), ('e^(2x)', 'e^(2x)', False), ('ln(x) + 4', '1/x', True), ('-cos(x) + x', 'sin(x) + 1', True),
           ('x^4/4', 'x^3', True), ('tan(x)', 'sec(x)', False)]
    for Fs, fs, tv in ver:
        ok = sp.simplify(sp.diff(S(Fs), x) - S(fs)) == 0
        assert ok == tv, Fs
        Q.append(TF(d.qid('V'), f'$F(x) = {D(Fs, False)}$ is an antiderivative of $f(x) = {D(fs, False)}$.', tv, level=1,
                    explain=f"Check: $F'(x) = {D(sp_app(sp.diff(S(Fs), x)), False)}$" + (', which matches.' if tv else ', which is not $f$.')))
    for f, ans in BASIC_ANTI:
        Q.append(E(d, d.qid('B'), f'Find {I(f)}.', ans, anti(f) if 'x^e' not in f else S(ans), label=f'{I(f)} =', post='$+ C$', upToC=True, level=2, keys=AK + ['arctan(', 'arcsin(', 'sec('],
                   ranges={'x': [0.2, 0.9]}, explain=f'${D(ans)} + C$'))
    ivps = [('6x^2', 1, 5), ('sin(x)', 0, 5), ('2x + 3', 0, 1), ('3x^2 - 4', 2, 0), ('e^x', 0, 4), ('cos(x)', 0, -2), ('1/x', 1, 3), ('4x^3 + 1', 1, 1), ('8x', 2, 20), ('2 - x', 0, 6),
            ('x^2', 3, 10), ('sec(x)^2', 0, 2)]
    for f, x0, y0 in ivps:
        Fa = sp.integrate(S(f), x)
        C = y0 - Fa.subs(x, x0)
        Fs = sp_app(Fa)
        Fs = {'sec(x)^2': 'tan(x)', '1/x': 'ln(x)'}.get(f, Fs)
        sol = tidy(f'{Fs} + {frac_str(C)}') if C != 0 else Fs
        Q.append(STEPS(d.qid('I'), f'Solve $frac{{dy}}{{dx}} = {D(f, False)}$ with $y({x0}) = {y0}$.', [
            E(d, None, 'General antiderivative.', Fs, Fa, label='$y$ =', post='$+ C$', upToC=True, keys=AK + ['sec('], ranges={'x': [0.2, 1.2]}, work=f'$y = {D(Fs, False)} + C$'),
            N(None, f'Use $y({x0}) = {y0}$.', C, label='$C$ =', work=f'$C = {frac_str(C)}$'),
            E(d, None, 'Write the solution.', sol, Fa + C, label='$y$ =', keys=AK + ['sec('], ranges={'x': [0.2, 1.2]}, work=f'$y = {D(sol, False)}$'),
        ], level=3, explain=f'$y = {D(sol, False)}$'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 4. The Fundamental Theorem of Calculus
DEFS = [('x^2', 0, 2), ('x + 2', 0, 2), ('3x^2', 1, 2), ('2x + 1', 0, 4), ('x^3', 0, 2), ('4x - x^2', 0, 4), ('cos(x)', 0, 'pi/2'), ('sin(x)', 0, 'pi'), ('e^x', 0, 1),
        ('1/x', 1, 'e'), ('sqrt(x)', 0, 4), ('x^2 + 2', 0, 1), ('6x^2 - 2x', 1, 3), ('1/x^2', 1, 2), ('sec(x)^2', 0, 'pi/4'), ('2/(1 + x^2)', 0, 1)]
NICE_A = {'cos(x)': 'sin(x)', 'sin(x)': '-cos(x)', 'e^x': 'e^x', '1/x': 'ln(x)', 'sec(x)^2': 'tan(x)', '2/(1 + x^2)': '2arctan(x)'}


def deck_ftc():
    d = Deck('w-ftc', 'The Fundamental Theorem of Calculus', 'Areas from antiderivatives, and derivatives of areas.', 'Integration')
    d.keys = AK
    L = []
    L.append(MC('L1', '**FTC, part 2:** if $F$ is any antiderivative of $f$, then $int[a,b] f(x) dx = F(b) - F(a)$. No more rectangles! For $int[0,2] x^2 dx$, which $F$ can you use?',
                ['$F(x) = frac{x^3}{3}$', '$F(x) = 2x$', '$F(x) = x^2$', '$F(x) = frac{x^2}{2}$'], hint="We need $F' = x^2$.", explain='$frac{x^3}{3}$ (or $frac{x^3}{3} + C$; the $C$ cancels).'))
    L.append(N('L2', 'So $int[0,2] x^2 dx = F(2) - F(0) = frac{8}{3} - 0$. Enter it.', sp.Rational(8, 3), label='integral =', hint='Use the fraction key, or 2.667.',
               explain='$frac{8}{3}$, exactly what the rectangles were closing in on.'))
    L.append(E(d, 'L3', '**FTC, part 1:** $frac{d}{dx} int[a,x] f(t) dt = f(x)$. The derivative of the area function is the function. Find $frac{d}{dx} int[1,x] t^3 dt$.', 'x^3', x ** 3,
               label='derivative =', hint='Put $x$ in for $t$.', explain='$x^3$'))
    L.append(E(d, 'L4', 'With the chain rule: $frac{d}{dx} int[a,g(x)] f(t) dt = f(g(x))·g\'(x)$. Find $frac{d}{dx} int[0,x^2] sin(t) dt$.', 'sin(x^2)(2x)', sp.sin(x ** 2) * 2 * x,
               label='derivative =', hint='Put $x^2$ in for $t$, then multiply by the derivative of $x^2$.', explain='$sin(x^2)·2x$'))
    L.append(N('L5', 'The **average value** of $f$ on $[a, b]$ is $frac{1}{b - a} int[a,b] f(x) dx$. Find the average of $f(x) = x^2 + 2$ on $[0, 1]$.', sp.Rational(7, 3), label='average =',
               hint='$int[0,1] (x^2 + 2) dx = frac{1}{3} + 2$, and $b - a = 1$.', explain='$frac{7}{3}$'))
    d.lesson(L)

    T = [
        MATCH('T1', 'Match each part of the Fundamental Theorem.', [['Part 1', '$frac{d}{dx} int[a,x] f(t) dt = f(x)$'], ['Part 2', '$int[a,b] f(x) dx = F(b) - F(a)$']],
              explain='Part 1: differentiating undoes integrating. Part 2: compute areas with antiderivatives.'),
        TF('T2', 'In $F(b) - F(a)$, it does not matter which antiderivative $F$ you use.', True, explain='$(F(b) + C) - (F(a) + C) = F(b) - F(a)$. The $C$ cancels.'),
        MC('T3', '$frac{d}{dx} int[a,g(x)] f(t) dt =$', ["$f(g(x))·g'(x)$", '$f(g(x))$', "$f(x)g'(x)$", '$F(g(x))$'], explain='Part 1 plus the chain rule.'),
        MC('T4', 'The average value of $f$ on $[a, b]$ is', ['$frac{1}{b - a} int[a,b] f(x) dx$', '$frac{f(a) + f(b)}{2}$', '$int[a,b] f(x) dx$', '$frac{f(b) - f(a)}{b - a}$'],
           explain='Total area divided by the width.'),
        MC('T5', 'What is $int[-pi,pi] sin(x) dx$?', ['0', '2', '$-2$', '$2pi$'], explain='$-cos(pi) - (-cos(-pi)) = 1 - 1 = 0$'),
        MC('T6', '$int[a,b] f(x) dx$ is a', ['number', 'function of $x$', 'function of $t$', 'family of functions'], explain='Definite integrals are numbers.'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    for Fs, a0, b0 in [('x^3/3', 0, 3), ('x^2 + x', 1, 2), ('sin(x)', 0, 'pi/2'), ('e^x', 0, 1), ('ln(x)', 1, 'e'), ('x^4', -1, 1), ('2x^3 - x', 0, 2), ('-cos(x)', 0, 'pi'), ('sqrt(x)', 1, 9), ('x^5/5', 0, 1)]:
        val = S(Fs).subs(x, S(str(b0))) - S(Fs).subs(x, S(str(a0)))
        Q.append(N(d.qid('F'), f'$F(x) = {D(Fs, False)}$ is an antiderivative of $f$. Find $F({D(str(b0))}) - F({D(str(a0))})$.', val, label='value =', tol=0.005, level=1,
                   explain=f'${frac_str(sp.nsimplify(val)) if val.is_rational else num(val)}$'))
    for f, ans in [('t^3', 'x^3'), ('sin(t)', 'sin(x)'), ('sqrt(1 + t^2)', 'sqrt(1 + x^2)'), ('e^(t^2)', 'e^(x^2)'), ('cos(t) + t', 'cos(x) + x'), ('1/(1 + t^4)', '1/(1 + x^4)'),
                   ('ln(t)', 'ln(x)'), ('t^2 - 3t', 'x^2 - 3x')]:
        Q.append(E(d, d.qid('P'), f'Find $frac{{d}}{{dx}} int[1,x] {D(f, False)} dt$.', ans, S(ans), label='derivative =', level=1, explain=f'Part 1: put $x$ in for $t$: ${D(ans)}$.'))
    for f, g, ans in [('sin(t)', 'x^2', 'sin(x^2)(2x)'), ('t^3', '2x', '(2x)^3(2)'), ('cos(t)', 'x^3', 'cos(x^3)(3x^2)'), ('sqrt(t)', 'x^2', 'x(2x)'), ('e^t', 'sin(x)', 'e^(sin(x))cos(x)'),
                      ('1/t', 'x^2', '2/x'), ('t^2 + 1', '3x', '3((3x)^2 + 1)'), ('ln(t)', 'e^x', 'xe^x')]:
        truth = S(tsub(f, 'u')).subs(u, S(g)) * sp.diff(S(g), x)
        Q.append(E(d, d.qid('C'), f'Find $frac{{d}}{{dx}} int[0,{D(g, False)}] {D(f, False)} dt$.', ans, truth, label='derivative =', level=2, ranges={'x': [0.3, 1.2]},
                   explain=f"$f(g(x))·g'(x) = {D(ans, False)}$"))
    for f, a0, b0 in DEFS:
        Fa = sp.integrate(S(f), x)
        val = sp.integrate(S(f), (x, S(str(a0)), S(str(b0))))
        Fs = NICE_A.get(f) or sp_app(Fa)
        nice = frac_str(val) if val.is_rational else num(val)
        Q.append(N(d.qid('D'), f'Evaluate {Idef(f, D(str(a0)), D(str(b0)))}.', val, label='integral =', tol=0.005, level=2, explain=f'$F(x) = {D(Fs, False)}$, and $F({D(str(b0))}) - F({D(str(a0))}) = {nice}$.'))
        Q.append(STEPS(d.qid('W'), f'Evaluate {Idef(f, D(str(a0)), D(str(b0)))} with the Fundamental Theorem.', [
            E(d, None, 'Find an antiderivative.', Fs, Fa, label='$F(x)$ =', upToC=True, keys=AK + ['arctan('], ranges={'x': [0.3, 1.2]}, work=f'$F(x) = {D(Fs, False)}$'),
            N(None, f'$F({D(str(b0))}) - F({D(str(a0))})$ (a decimal is fine).', val, label='integral =', tol=0.005, work=f'integral $= {nice}$'),
        ], level=3, explain=f'{nice}'))
    for f, a0, b0 in [('x^2 + 2', 0, 1), ('x + 1', 2, 5), ('x^2', 0, 3), ('sin(x)', 0, 'pi'), ('3x^2', 0, 2), ('e^x', 0, 1)]:
        tot = sp.integrate(S(f), (x, S(str(a0)), S(str(b0))))
        av = tot / (S(str(b0)) - S(str(a0)))
        Q.append(STEPS(d.qid('A'), f'Find the average value of $f(x) = {D(f, False)}$ on $[{D(str(a0))}, {D(str(b0))}]$.', [
            N(None, f'First the integral {Idef(f, D(str(a0)), D(str(b0)))}.', tot, label='integral =', tol=0.005, work=f'integral $= {frac_str(tot) if tot.is_rational else num(tot)}$'),
            N(None, 'Divide by the width $b - a$.', av, label='average =', tol=0.005, work=f'average $= {frac_str(av) if av.is_rational else num(av)}$'),
        ], level=3, explain=f'{frac_str(av) if av.is_rational else num(av)}'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


def deck_proof():
    d = Deck('w-proof', 'Proof of the Fundamental Theorem', 'Optional: why the Fundamental Theorem is true.', 'Integration')
    L = [
        MC('L1', 'Define the area function $g(x) = int[a,x] f(t) dt$: the area under $f$ from $a$ up to $x$. When $x$ grows a tiny bit to $x + h$, the area grows by', ['$int[x,x+h] f(t) dt$', '$f(h)$', '$g(h)$', '$h$'],
           hint='The new strip runs from $x$ to $x + h$.', explain='$g(x + h) - g(x) = int[x,x+h] f(t) dt$, a thin strip.'),
        MC('L2', 'That thin strip is almost a rectangle of width $h$ and height', ['$f(x)$', '$g(x)$', '1', '$x$'], hint='How tall is the curve right at $x$?', explain='So $g(x + h) - g(x) ≈ f(x)·h$.'),
        MC('L3', 'Divide by $h$: $frac{g(x + h) - g(x)}{h} ≈ f(x)$. Let $h -> 0$. The left side becomes', ["$g'(x)$", '$g(x)$', '0', '$f\'(x)$'], hint='That is the definition of the derivative.',
           explain="$g'(x) = f(x)$. That is **Part 1**: the area function is an antiderivative of $f$."),
        MC('L4', 'Now let $F$ be **any** antiderivative of $f$. Two antiderivatives of the same function differ by a constant, so $F(x) = g(x) + C$. Then $F(b) - F(a) =$',
           ['$g(b) - g(a)$', '$g(b) + 2C$', '$C$', '$g(a) - g(b)$'], hint='The $C$s cancel.', explain='$(g(b) + C) - (g(a) + C) = g(b) - g(a)$.'),
        MC('L5', 'Finally $g(b) = int[a,b] f(t) dt$ and $g(a) = int[a,a] f(t) dt = 0$. So $F(b) - F(a) =$', ['$int[a,b] f(t) dt$', '0', '$f(b) - f(a)$', '$g(a)$'],
           hint='Plug in what $g(b)$ and $g(a)$ are.', explain='That is **Part 2**: $int[a,b] f = F(b) - F(a)$. ∎'),
    ]
    d.lesson(L)
    T = [
        ORDER('T1', 'Put the steps of the proof of Part 1 in order.', ['Define the area function $g(x) = int[a,x] f(t) dt$', 'The extra area from $x$ to $x + h$ is about $f(x)h$',
              'Divide by $h$', "Let $h -> 0$ to get $g'(x) = f(x)$"], explain='Thin strip, divide, take the limit.'),
        TF('T2', 'Two antiderivatives of the same function always differ by a constant.', True, explain='Their difference has derivative 0, so it is constant (by the Mean Value Theorem).'),
        MC('T3', 'Why is $g(a) = 0$?', ['There is no width from $a$ to $a$', 'Because $f(a) = 0$', 'Because $C = 0$', 'It is not always 0'], explain='$int[a,a] f = 0$.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    d.save()


# ====================================================================== 5. Indefinite integrals and net change
def deck_indef():
    d = Deck('w-indef', 'Indefinite Integrals and Net Change', 'Antiderivatives as integrals, and what a rate adds up to.', 'Integration')
    d.keys = AK
    L = []
    L.append(MC('L1', 'Two kinds of integral: the **indefinite** $int f(x) dx$ and the **definite** $int[a,b] f(x) dx$. Which is a number?', ['the definite one', 'the indefinite one', 'both', 'neither'],
                hint='Which one has limits on it?', explain='$int[a,b]$ is a number (an area). $int f(x) dx = F(x) + C$ is a family of functions.'))
    L.append(E(d, 'L2', 'Game time from class! Find $int (x^5 + 2) dx$.', 'x^6/6 + 2x', x ** 6 / 6 + 2 * x, label='$int (x^5 + 2) dx$ =', post='$+ C$', upToC=True,
               hint='Term by term: $frac{x^6}{6}$ and $2x$.', explain='$frac{x^6}{6} + 2x + C$'))
    L.append(MC('L3', '**Net change theorem:** $int[a,b] F\'(x) dx = F(b) - F(a)$. Integrating a rate gives the total change. If $v(t)$ is velocity, $int[0,3] v(t) dt$ is the', ['displacement (change in position)', 'acceleration', 'speed at $t = 3$', 'average velocity'],
                hint='Velocity is the rate of change of position.', explain='Total change in position from $t = 0$ to $t = 3$.'))
    L.append(STEPS('L4', 'A particle moves with velocity $v(t) = t^2 - 4t$ (m/s) for $0 <= t <= 6$.', [
        N('L4.1', 'Displacement: $int[0,6] (t^2 - 4t) dt$.', 0, label='displacement =', hint='$frac{t^3}{3} - 2t^2$ from 0 to 6: $72 - 72$.', work='displacement $= 0$ m'),
        N('L4.2', 'Total distance: it moves backward for $0 < t < 4$ (where $v < 0$) and forward after. Add $|int[0,4] v dt| + int[4,6] v dt$.', sp.Rational(64, 3), label='distance =',
          hint='$int[0,4] v = -frac{32}{3}$ and $int[4,6] v = frac{32}{3}$.', work='distance $= frac{64}{3}$ m'),
    ]))
    L.append(N('L5', 'Water flows into a tank at $r(t) = 3t^2$ liters per minute. How much water flows in during the first 2 minutes?', 8, label='liters =', hint='$int[0,2] 3t^2 dt$',
               explain='$t^3$ from 0 to 2: 8 liters.'))
    d.lesson(L)

    T = [
        MC('T1', '$int[a,b] F\'(x) dx =$', ['$F(b) - F(a)$', "$F'(b) - F'(a)$", '$F(a) - F(b)$', '$F(b)$'], explain='The net change theorem.'),
        MC('T2', 'Velocity $v(t)$ is negative for part of a trip. Then $int[a,b] v(t) dt$ gives', ['the displacement, with backward motion subtracted', 'the total distance', 'the top speed', 'the time traveled'],
           explain='For total distance, integrate $|v(t)|$.'),
        MC('T3', 'If $r(t)$ is the rate oil leaks from a tank (gallons per hour), then $int[0,5] r(t) dt$ is', ['the gallons that leak out in the first 5 hours', 'the leak rate at hour 5', 'the gallons left in the tank', 'how fast the leak speeds up'],
           explain='Integrating a rate gives the total amount.'),
        TF('T4', 'An indefinite integral is a number.', False, explain='It is a family of functions, $F(x) + C$.'),
        MC('T5', '$int sec^2(x) dx =$', ['$tan(x) + C$', '$sec(x) + C$', '$frac{sec^3(x)}{3} + C$', '$2sec(x)tan(x) + C$'], explain="$(tan(x))' = sec^2(x)$"),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    games = [('sin(x)', '-cos(x)'), ('x^5 + 2', 'x^6/6 + 2x'), ('2sec(x)^2', '2tan(x)'), ('1/x', 'ln(x)'), ('4/x^3', '-2/x^2'), ('cos(x) - x', 'sin(x) - x^2/2'), ('e^x + 1', 'e^x + x'),
             ('3x^2 - 2x + 5', 'x^3 - x^2 + 5x'), ('sqrt(x) + 1', '(2/3)x^(3/2) + x'), ('(x + 1)^2', 'x^3/3 + x^2 + x'), ('x(x - 3)', 'x^3/3 - 3x^2/2'), ('(x^2 + 1)/x', 'x^2/2 + ln(x)'),
             ('5', '5x'), ('1/(1 + x^2)', 'arctan(x)'), ('2e^x - 3sin(x)', '2e^x + 3cos(x)'), ('x^(-1/2)', '2sqrt(x)'), ('6x^5 - 4x^3', 'x^6 - x^4'), ('sec(x)tan(x) + x', 'sec(x) + x^2/2'),
             ('(1 - x)/sqrt(x)', '2sqrt(x) - (2/3)x^(3/2)'), ('8x^7', 'x^8')]
    for k, (f, ans) in enumerate(games):
        Q.append(E(d, d.qid('I'), f'Find {I(f)}.', ans, sp.integrate(S(f), x), label=f'{I(f)} =', post='$+ C$', upToC=True, level=1 if k < 8 else 2, keys=AK + ['arctan(', 'sec('],
                   ranges={'x': [0.2, 1.2]}, explain=f'${D(ans)} + C$'))
    nets = [('Water flows into a tank at $r(t) = 3t^2$ L/min.', 'How many liters flow in from $t = 0$ to $t = 2$?', '3t^2', 0, 2),
            ('A population grows at $P\'(t) = 20t$ people per year.', 'By how much does it grow from $t = 1$ to $t = 3$?', '20t', 1, 3),
            ('Oil leaks at $r(t) = 6 - t$ gallons per hour.', 'How much leaks in the first 4 hours?', '6 - t', 0, 4),
            ('A car accelerates with $v(t) = 4t + 10$ ft/s.', 'How far does it go from $t = 0$ to $t = 5$?', '4t + 10', 0, 5),
            ('A town uses electricity at $E(t) = 2 + sin(t)$ (in megawatts).', 'How much energy (megawatt-hours) is used from $t = 0$ to $t = pi$?', '2 + sin(t)', 0, 'pi'),
            ('A snowball melts at $V\'(t) = -2t$ cm³/min.', 'How much does its volume change from $t = 0$ to $t = 3$?', '-2t', 0, 3),
            ('A runner\'s velocity is $v(t) = 3sqrt(t)$ m/s.', 'How far does she run from $t = 0$ to $t = 4$?', '3sqrt(t)', 0, 4),
            ('Revenue comes in at $R\'(t) = 100e^t$ dollars per day.', 'How much comes in from $t = 0$ to $t = 1$? (A decimal is fine.)', '100e^t', 0, 1),
            ('Sand pours onto a pile at $12 - 2t$ kg/min.', 'How much sand lands from $t = 0$ to $t = 6$?', '12 - 2t', 0, 6),
            ('A balloon rises at $v(t) = 6t - t^2$ m/s.', 'How much higher is it at $t = 3$ than at $t = 0$?', '6t - t^2', 0, 3)]
    for ctx, ask, r_, a0, b0 in nets:
        val = sp.integrate(S(tsub(r_, 'x')), (x, S(str(a0)), S(str(b0))))
        Q.append(N(d.qid('N'), f'{ctx} {ask}', val, label='total =', tol=0.01, level=2,
                   explain=f'Integrate the rate: $int[{D(str(a0))},{D(str(b0))}] {D(r_, False)} dt = {frac_str(val) if val.is_rational else num(val)}$.'))
    trips = [('t^2 - 4t', 0, 6, 4), ('t - 2', 0, 4, 2), ('3t^2 - 12', 0, 3, 2), ('2t - 6', 0, 5, 3), ('t^2 - 1', 0, 2, 1), ('4 - 2t', 0, 3, 2)]
    for v_, a0, b0, cross in trips:
        vv = S(tsub(v_, 'x'))
        disp = sp.integrate(vv, (x, a0, b0))
        dist = abs(sp.integrate(vv, (x, a0, cross))) + abs(sp.integrate(vv, (x, cross, b0)))
        Q.append(STEPS(d.qid('T'), f'A particle has velocity $v(t) = {D(v_, False)}$ m/s for ${a0} <= t <= {b0}$. It changes direction at $t = {cross}$.', [
            N(None, f'Displacement: $int[{a0},{b0}] v(t) dt$.', disp, label='displacement =', work=f'displacement $= {frac_str(disp)}$'),
            N(None, f'Total distance: add the size of each part, $|int[{a0},{cross}] v| + |int[{cross},{b0}] v|$.', dist, label='distance =', work=f'distance $= {frac_str(dist)}$'),
        ], level=3, explain=f'Displacement {frac_str(disp)} m, distance {frac_str(dist)} m.'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 6. Substitution
# (integrand display, u, du/dx, integral in u, answer in x, in-u integrand)
SUBS = [('6x(3x^2 + 4)^4', '3x^2 + 4', '6x', 'u^4', '(3x^2 + 4)^5/5'), ('3x^2(x^3 - 3)^2', 'x^3 - 3', '3x^2', 'u^2', '(x^3 - 3)^3/3'),
        ('2x cos(x^2)', 'x^2', '2x', 'cos(u)', 'sin(x^2)'), ('cos(x) sin^3(x)', 'sin(x)', 'cos(x)', 'u^3', 'sin(x)^4/4'), ('2x e^(x^2)', 'x^2', '2x', 'e^u', 'e^(x^2)'),
        ('frac{2x}{x^2 + 1}', 'x^2 + 1', '2x', '1/u', 'ln(x^2 + 1)'), ('3(3x + 1)^5', '3x + 1', '3', 'u^5', '(3x + 1)^6/6'), ('2x sqrt(x^2 + 5)', 'x^2 + 5', '2x', 'sqrt(u)', '(2/3)(x^2 + 5)^(3/2)'),
        ('-sin(x) cos^2(x)', 'cos(x)', '-sin(x)', 'u^2', 'cos(x)^3/3'), ('5e^(5x)', '5x', '5', 'e^u', 'e^(5x)'), ('frac{3x^2}{x^3 + 2}', 'x^3 + 2', '3x^2', '1/u', 'ln(x^3 + 2)'),
        ('4x^3(x^4 + 1)^2', 'x^4 + 1', '4x^3', 'u^2', '(x^4 + 1)^3/3'), ('frac{e^x}{e^x + 1}', 'e^x + 1', 'e^x', '1/u', 'ln(e^x + 1)'), ('frac{arctan(x)}{1 + x^2}', 'arctan(x)', '1/(1 + x^2)', 'u', 'arctan(x)^2/2')]
# need a constant fixed:  (integrand, u, du/dx, constant k so that the leftover is k du)
SUBS_K = [('x(x^2 + 1)^3', 'x^2 + 1', '2x', sp.Rational(1, 2), '(x^2 + 1)^4/8'), ('x e^(4x^2 + 3)', '4x^2 + 3', '8x', sp.Rational(1, 8), 'e^(4x^2 + 3)/8'),
          ('z sqrt(z^2 - 5)', 'z^2 - 5', '2z', sp.Rational(1, 2), '(z^2 - 5)^(3/2)/3'), ('frac{sin(x)}{cos^2(x)}', 'cos(x)', '-sin(x)', -1, '1/cos(x)'),
          ('tan(x)', 'cos(x)', '-sin(x)', -1, '-ln(cos(x))'), ('sin(theta) cos^2(theta)', 'cos(theta)', '-sin(theta)', -1, '-cos(theta)^3/3'), ('x^2 sin(x^3)', 'x^3', '3x^2', sp.Rational(1, 3), '-cos(x^3)/3'),
          ('cos(4x)', '4x', '4', sp.Rational(1, 4), 'sin(4x)/4')]


def deck_subst():
    d = Deck('w-subst', 'Substitution', 'Undoing the chain rule.', 'Integration')
    d.keys = AK
    L = []
    L.append(MC('L1', 'Substitution undoes the chain rule. In $int 6x(3x^2 + 4)^4 dx$, notice that $6x$ is the derivative of $3x^2 + 4$. So we let $u =$', ['$3x^2 + 4$', '$6x$', '$(3x^2 + 4)^4$', '$x$'],
                hint='Pick the inside function whose derivative is sitting next to it.', explain='$u = 3x^2 + 4$'))
    L.append(STEPS('L2', 'Finish $int 6x(3x^2 + 4)^4 dx$ with $u = 3x^2 + 4$.', [
        E(d, 'L2.1', None, '6x', 6 * x, label='$frac{du}{dx}$ =', hint='The derivative of $3x^2 + 4$.', work='$du = 6x dx$, so the integral is $int u^4 du$'),
        E(d, 'L2.2', 'Integrate in $u$.', 'u^5/5', u ** 5 / 5, ['u'], label='$int u^4 du$ =', post='$+ C$', upToC=True, hint='Anti-power rule.', work='$int u^4 du = frac{u^5}{5} + C$'),
        E(d, 'L2.3', 'Put $u = 3x^2 + 4$ back.', '(3x^2 + 4)^5/5', (3 * x ** 2 + 4) ** 5 / 5, label='answer =', post='$+ C$', upToC=True, hint='Replace $u$.', work='$frac{(3x^2 + 4)^5}{5} + C$'),
    ]))
    L.append(E(d, 'L3', 'Your turn: $int 3x^2(x^3 - 3)^2 dx$. (Let $u = x^3 - 3$.)', '(x^3 - 3)^3/3', (x ** 3 - 3) ** 3 / 3, label='answer =', post='$+ C$', upToC=True,
               hint='$du = 3x^2 dx$, so it is $int u^2 du = frac{u^3}{3}$.', explain='$frac{(x^3 - 3)^3}{3} + C$'))
    L.append(MC('L4', 'Sometimes a constant is missing. In $int x e^(4x^2 + 3) dx$ let $u = 4x^2 + 3$. Then $du = 8x dx$, so $x dx =$', ['$frac{1}{8} du$', '$8 du$', '$du$', '$frac{1}{4x} du$'],
                hint='Divide $du = 8x dx$ by 8.', explain='So the integral is $frac{1}{8} int e^u du = frac{1}{8}e^(4x^2 + 3) + C$.'))
    L.append(MC('L5', 'For a **definite** integral, change the limits too. In $int[0,1] x e^(4x^2 + 3) dx$ with $u = 4x^2 + 3$, the limits $x = 0$ and $x = 1$ become', ['$u = 3$ and $u = 7$', '$u = 0$ and $u = 1$', '$u = 3$ and $u = 4$', '$u = 0$ and $u = 8$'],
                hint='Plug each $x$ into $u = 4x^2 + 3$.', explain='Then $frac{1}{8} int[3,7] e^u du = frac{e^7 - e^3}{8}$.'))
    d.lesson(L)

    T = [
        MC('T1', 'Substitution is the reverse of which derivative rule?', ['the chain rule', 'the product rule', 'the quotient rule', 'the power rule'], explain='$int f(g(x))g\'(x) dx = F(g(x)) + C$'),
        MC('T2', 'A good choice for $u$ is usually', ['an inside function whose derivative also appears', 'the whole integrand', 'always $x$', 'the outside function'], explain='Then $du$ soaks up the derivative.'),
        TF('T3', 'Your final answer to an indefinite integral should be written in terms of $u$.', False, explain='Put $x$ back in at the end.'),
        TF('T4', 'In a definite integral, after substituting you can either change the limits to $u$-values or go back to $x$ first.', True, explain='Just do not mix them: $u$-limits go with a $u$-integral.'),
        ORDER('T5', 'Put the steps of substitution in order.', ['Choose $u$', 'Find $du$ in terms of $dx$', 'Rewrite the integral in $u$ and integrate', 'Put $x$ back in (and $+ C$)'],
              explain='Choose, differentiate, rewrite and integrate, substitute back.'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    for f, uu, dudx, iu, ans in SUBS:
        Q.append(E(d, d.qid('U'), f'What is a good $u$ for $int {D(f, False)} dx$?', uu, S(uu), label='$u$ =', level=1, keys=AK + ['arctan('], ranges={'x': [0.2, 1.2]},
                   explain=f'$u = {D(uu, False)}$, because its derivative ${D(dudx)}$ is right there.'))
    for f, uu, dudx, k_, ans in SUBS_K:
        var = 'z' if 'z' in f else 'theta' if 'theta' in f else 'x'
        if var != 'x':
            continue
        Q.append(E(d, d.qid('V'), f'With $u = {D(uu, False)}$, find $frac{{du}}{{dx}}$.', dudx, sp.diff(S(uu), x), label='$frac{du}{dx}$ =', level=1, ranges={'x': [0.2, 1.2]},
                   explain=f'$du = {D(dudx, False)} dx$'))
    for f, uu, dudx, iu, ans in SUBS[:12]:
        Fu = sp.integrate(S(iu), u)
        fu = {'cos(u)': 'sin(u)', 'e^u': 'e^u', '1/u': 'ln(u)', 'sqrt(u)': '(2/3)u^(3/2)'}.get(iu) or sp_app(Fu)
        Q.append(E(d, d.qid('W'), f'$int {D(f, False)} dx$ with $u = {D(uu, False)}$ becomes $int {D(iu, False)} du$. Integrate in $u$.', fu, Fu, ['u'], label=f'$int {D(iu, False)} du$ =', post='$+ C$',
                   upToC=True, level=2, ranges={'u': [0.3, 1.5]}, explain=f'${D(fu)} + C$'))
    for f, uu, dudx, k_, ans in SUBS_K:
        var = 'z' if 'z' in f else 'theta' if 'theta' in f else 'x'
        Q.append(N(d.qid('K'), f'In $int {D(f, False)} d{var}$ let $u = {D(uu, False)}$, so $du = {D(dudx, False)} d{var}$. The leftover piece is $k du$. What is $k$?', k_, label='$k$ =', level=2,
                   explain=f'Divide $du$ by what is missing: $k = {frac_str(k_)}$.'))
    for f, uu, dudx, iu, ans in SUBS:
        truth = sp.integrate(S(f.replace('frac{2x}{x^2 + 1}', '2x/(x^2 + 1)').replace('frac{3x^2}{x^3 + 2}', '3x^2/(x^3 + 2)').replace('frac{e^x}{e^x + 1}', 'e^x/(e^x + 1)')
                                 .replace('frac{arctan(x)}{1 + x^2}', 'arctan(x)/(1 + x^2)').replace('sin^3(x)', 'sin(x)^3').replace('cos^2(x)', 'cos(x)^2')), x)
        Q.append(STEPS(d.qid('S'), f'Use substitution: $int {D(f, False)} dx$.', [
            E(d, None, None, uu, S(uu), label='$u$ =', keys=AK + ['arctan('], ranges={'x': [0.2, 1.2]}, work=f'$u = {D(uu, False)}$'),
            E(d, None, None, dudx, sp.diff(S(uu), x), label='$frac{du}{dx}$ =', keys=AK + ['arctan('], ranges={'x': [0.2, 1.2]}, work=f'$du = {D(dudx, False)} dx$, so it is $int {D(iu, False)} du$'),
            E(d, None, 'Integrate, then put $x$ back.', ans, truth, label='answer =', post='$+ C$', upToC=True, keys=AK + ['arctan('], ranges={'x': [0.2, 1.2]}, work=f'${D(ans)} + C$'),
        ], level=3, explain=f'${D(ans)} + C$'))
    defs = [('2x(x^2 + 1)^3', 'x^2 + 1', 0, 1, 'u^3'), ('x e^(4x^2 + 3)', '4x^2 + 3', 0, 1, 'e^u/8'), ('frac{arctan(x)}{1 + x^2}', 'arctan(x)', 0, 1, 'u'),
            ('x^2(1 + 2x^3)^5', '1 + 2x^3', 0, 1, 'u^5/6'), ('2x cos(x^2)', 'x^2', 0, 'sqrt(pi)', 'cos(u)'), ('frac{2x}{x^2 + 1}', 'x^2 + 1', 0, 2, '1/u')]
    for f, uu, a0, b0, iu in defs:
        ue = S(uu)
        ua, ub = ue.subs(x, S(str(a0))), ue.subs(x, S(str(b0)))
        val = sp.integrate(S(iu), (u, ua, ub))
        show = lambda v: frac_str(v) if v.is_rational else D(sp_app(v))
        Q.append(STEPS(d.qid('D'), f'Evaluate $int[{a0},{D(str(b0))}] {D(f, False)} dx$ with $u = {D(uu, False)}$.', [
            N(None, f'New lower limit: $u$ at $x = {a0}$.', ua, label='lower $u$ =', tol=0.005, work=f'lower: $u = {show(ua)}$'),
            N(None, f'New upper limit: $u$ at $x = {D(str(b0))}$.', ub, label='upper $u$ =', tol=0.005, work=f'upper: $u = {show(ub)}$'),
            N(None, f'The integral is $int[{show(ua)},{show(ub)}] {D(iu, False)} du$. Evaluate it (a decimal is fine).', val, label='integral =', tol=0.01, work=f'integral $≈ {num(val)}$'),
        ], level=3, explain=f'{num(val)}'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== chapter review
def deck_review4():
    import json, copy, os
    d = Deck('review4', 'Chapter Review: Integration', 'Mixed practice from every stop, and a practice test.', 'Integration')
    cases = [('$int[0,4] sqrt(16 - x^2) dx$', 'Geometry (a known shape)'), ('$int 6x(3x^2 + 4)^4 dx$', 'Substitution'), ('$int (x^5 + 2) dx$', 'Antiderivative rules (term by term)'),
             ('$frac{d}{dx} int[1,x] t^3 dt$', 'FTC part 1'), ('$int[0,2] x^2 dx$', 'FTC part 2 (antiderivative, then F(b) − F(a))'), ('$int 2x cos(x^2) dx$', 'Substitution'),
             ('$int[-3,3] 2x dx$', 'Geometry (a known shape)'), ('$int sec^2(x) dx$', 'Antiderivative rules (term by term)'), ('$frac{d}{dx} int[0,x^2] sin(t) dt$', 'FTC part 1'),
             ('$int[1,e] frac{1}{x} dx$', 'FTC part 2 (antiderivative, then F(b) − F(a))'), ('$int frac{e^x}{e^x + 1} dx$', 'Substitution'), ('$int (3x^2 - 2x + 5) dx$', 'Antiderivative rules (term by term)'),
             ('$int[0,4] (2x + 1) dx$', 'Geometry (a known shape)'), ('$int x sqrt(x^2 + 5) dx$', 'Substitution'), ('$frac{d}{dx} int[2,x] e^(t^2) dt$', 'FTC part 1'),
             ('$int[0,pi] sin(x) dx$', 'FTC part 2 (antiderivative, then F(b) − F(a))'), ('$int frac{4}{x^3} dx$', 'Antiderivative rules (term by term)'), ('$int tan(x) dx$', 'Substitution')]
    opts = ['Geometry (a known shape)', 'Substitution', 'Antiderivative rules (term by term)', 'FTC part 1', 'FTC part 2 (antiderivative, then F(b) − F(a))']
    tool = []
    for k, (f, r) in enumerate(cases):
        o = [r] + [w for w in opts if w != r][:3]
        tool.append(MC(f'W{k + 1}', f'What is the best first move for {f}?', o, level=1 + (k % 3 == 2), topic='Which tool?', explain=f'{r}.'))
    d.drill('tool', 'Which tool?', tool, 'pool', setSize=10)
    topics = {'w-areas': 'Areas and Riemann sums', 'w-definite': 'Definite integrals', 'w-anti': 'Antiderivatives', 'w-ftc': 'Fundamental Theorem', 'w-indef': 'Net change', 'w-subst': 'Substitution'}
    ex = []
    rr = random.Random(9)
    for did, top in topics.items():
        src = json.load(open(os.path.join(ROOT, 'decks', did + '.json')))
        qs = [q for q in src['drills']['practice']['questions'] if q.get('level', 1) >= 2]
        rr.shuffle(qs)
        for q in qs[:9]:
            q = copy.deepcopy(q)
            pre = did[2:].upper()[:3]
            q['id'] = pre + q['id']
            for st in q.get('steps', []):
                st['id'] = pre + st['id']
            q['topic'] = top
            q.pop('level', None)
            if q.get('graph'):
                g = src['graphs'][q['graph']]
                q['graph'] = did + '-' + q['graph']
                d.graph(q['graph'], g)
            ex.append(q)
    d.drill('exam', 'Practice test', ex, None, exam=True, setSize=20)
    del d.d['drills']['exam']['mode']
    d.save()


if __name__ == '__main__':
    deck_areas()
    deck_sumnot()
    deck_definite()
    deck_anti()
    deck_ftc()
    deck_proof()
    deck_indef()
    deck_subst()
    deck_review4()
    write_manifest('world4')
