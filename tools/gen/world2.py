"""World 2 (Derivatives): one short lesson, a theory set (every question required) and a big practice
pool (12 at random per set, 80% to pass) for each stop. See lib.py before re-running: it overwrites decks."""
import random, sys, re
import sympy as sp
from lib import *

R = random.Random(2026)
DERIV_KEYS = ['sin(', 'cos(', 'sqrt(']


def F(name, s):
    """'f(x) = ...' in math markup"""
    return f'${name} = {D(s)}$'


def lin(m, b0, var='x'):
    return tidy(poly_str([m, b0], var))


def quad(R, small=True):
    a_ = R.choice([1, 1, 2, 3, -1, -2]) if small else R.choice([1, 2, 3, 4, -1, -2, -3])
    b_ = R.choice([0, 1, 2, 3, -1, -2, -4, 5])
    c_ = R.choice([0, 1, 2, -3, 4, 5, -1])
    return [a_, b_, c_]


def P(coeffs, var='x'):
    return sp.Poly(coeffs, sp.Symbol(var)).as_expr()


# ====================================================================== 1. Definition of the derivative
def deck_defn():
    d = Deck('d-defn', 'Definition of the Derivative', 'Slopes of secant lines become the slope of the tangent line.', 'Derivatives')
    d.keys = []
    L = []
    L.append({'id': 'L1', 'type': 'secant', 'title': 'From secant to tangent',
              'text': 'The slope of a secant line is $m = frac{f(b) - f(a)}{b - a}$. Slide the teal point toward the black point at $x = 2$ on $f(x) = x^2$ and watch the slope.',
              'fn': 'x^2', 'a': 2, 'h': -2, 'goal': 0.01, 'left': True, 'window': [-0.6, 3.4, -1, 9],
              'after': 'The secant slopes settle on **4**. That number is the slope of the **tangent line** at $x = 2$. We call it the **derivative**: $f\'(2) = 4$.'})
    L.append(MC('L2', 'Write $b = a + h$. The secant slope is then $frac{f(a+h) - f(a)}{h}$. How do we turn it into the slope of the tangent line?',
                ['Take the limit as $h -> 0$', 'Plug in $h = 0$', 'Let $h -> infty$', 'Plug in $h = 1$'],
                hint='Plugging in $h = 0$ gives $frac{0}{0}$. We want $h$ to get close to 0 without being 0.',
                explain='$f\'(a) = lim[h->0] frac{f(a+h) - f(a)}{h}$. That is the **definition of the derivative**.'))
    L.append(STEPS('L3', 'Use the definition to find $f\'(1)$ for ' + F('f(x)', 'x^2 + x') + '. One line at a time.', [
        E(d, 'L3.1', None, 'h^2 + 3h + 2', (1 + h) ** 2 + (1 + h), ['h'], label='$f(1 + h)$ =',
          hint='Replace every $x$ with $(1 + h)$: $(1 + h)^2 + (1 + h)$, then multiply out.', work='$f(1 + h) = h^2 + 3h + 2$'),
        N('L3.2', '', 2, label='$f(1)$ =', hint='$1^2 + 1$', work='$f(1) = 2$'),
        E(d, 'L3.3', 'Subtract, then cancel the $h$: $frac{(h^2 + 3h + 2) - 2}{h}$', 'h + 3', h + 3, ['h'], label='$frac{f(1+h) - f(1)}{h}$ =',
          hint='The top is $h^2 + 3h$. Divide each term by $h$.', work='$frac{f(1+h) - f(1)}{h} = h + 3$'),
        N('L3.4', 'Now let $h -> 0$.', 3, label="$f'(1)$ =", hint='What does $h + 3$ approach when $h$ goes to 0?', work="$f'(1) = 3$"),
    ]))
    L.append(E(d, 'L4', "The **tangent line** at $x = a$ is $y = f'(a)(x - a) + f(a)$. For $f(x) = x^2 + 1$ at $a = 1$: $f(1) = 2$ and $f'(1) = 2$. Type the tangent line.",
               '2(x - 1) + 2', 2 * (x - 1) + 2, label='$y$ =', hint="Put $f'(1) = 2$, $a = 1$ and $f(1) = 2$ into $y = f'(a)(x - a) + f(a)$.",
               explain='$y = 2(x - 1) + 2$, which is the same line as $y = 2x$.'))
    L.append(MC('L5', 'The derivative is the **instantaneous rate of change**. If $s(t)$ is your position at time $t$, then $s\'(t)$ is your…',
                ['velocity', 'acceleration', 'distance traveled', 'average position'],
                hint='How fast is your position changing?', explain='Position changes at the rate of your velocity. (And $v\'(t)$ is acceleration.)'))
    d.lesson(L)

    T = []
    T.append(MC('T1', 'The slope of the secant line through $(a, f(a))$ and $(b, f(b))$ is', ['$frac{f(b) - f(a)}{b - a}$', '$frac{b - a}{f(b) - f(a)}$', '$frac{f(b) + f(a)}{b + a}$', '$f(b) - f(a)$'],
                explain='Rise over run: change in $y$ over change in $x$.'))
    T.append(MC('T2', "$f'(a)$ is the slope of the", ['tangent line at $x = a$', 'secant line from 0 to $a$', 'graph at its highest point', 'line through the origin and $(a, f(a))$'],
                explain="The derivative at a point is the slope of the tangent line there: how steep the graph is right at $x = a$."))
    T.append(TF('T3', 'To find $f\'(a)$, you can just plug $h = 0$ into $frac{f(a+h) - f(a)}{h}$.', False,
                explain='That gives $frac{0}{0}$. Simplify first (cancel the $h$), then let $h -> 0$.'))
    T.append(MATCH('T4', 'Match each word to what it means.', [['Secant line', 'meets the curve at two points'], ['Tangent line', 'has the slope of the curve at one point'],
                   ['Derivative $f\'(a)$', 'the slope of the tangent line'], ['Difference quotient', '$frac{f(a+h) - f(a)}{h}$']],
                   explain='The difference quotient is a secant slope. Its limit as $h -> 0$ is the derivative.'))
    T.append(MC('T5', 'The equation of the tangent line to $f$ at $x = a$ is', ["$y = f'(a)(x - a) + f(a)$", "$y = f(a)(x - a) + f'(a)$", "$y = f'(x)(x - a)$", "$y = f'(a)x$"],
                explain='Point-slope form with slope $f\'(a)$ through the point $(a, f(a))$.'))
    T.append(MC('T6', "Which limit is also equal to $f'(a)$?", ['$lim[x->a] frac{f(x) - f(a)}{x - a}$', '$lim[x->a] frac{f(x) + f(a)}{x + a}$', '$lim[x->0] frac{f(x)}{x}$', '$lim[h->a] frac{f(h)}{h}$'],
                explain='This is the same idea with $b$ called $x$: the secant from $a$ to $x$, as $x -> a$.'))
    T.append(MC('T7', 'If $T(t)$ is the temperature at time $t$, then $T\'(t)$ tells you', ['how fast the temperature is changing at time $t$', 'the temperature at time $t$', 'the average temperature', 'the highest temperature'],
                explain='A derivative is a rate of change.'))
    T.append(MC('T8', 'The graph of $f(x) = |x|$ has a sharp corner at $x = 0$. What is $f\'(0)$?', ['It does not exist', '0', '1', '−1'],
                explain='From the left the slopes are −1, from the right they are 1. They do not agree, so there is no single tangent line.'))
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    fs = [[1, 0, 0], [1, 1, 0], [2, 0, 1], [1, -2, 3], [3, -4, 1], [1, 0, -4], [-1, 2, 0], [2, -1, 0], [1, 3, -2], [-2, 0, 5], [1, -1, 1], [4, 0, -3]]
    # L1: secant slopes
    for k in range(12):
        c = fs[k]
        f = P(c)
        a0 = R.choice([0, 1, 2, -1])
        b0 = a0 + R.choice([1, 2, 3])
        m = (f.subs(x, b0) - f.subs(x, a0)) / (b0 - a0)
        Q.append(N(d.qid('S'), f'Find the slope of the secant line of {F("f(x)", poly_str(c))} from $x = {a0}$ to $x = {b0}$.', m, label='$m$ =', level=1,
                   explain=f'$f({b0}) = {num(f.subs(x, b0))}$ and $f({a0}) = {num(f.subs(x, a0))}$, so $m = frac{{{num(f.subs(x, b0))} - ({num(f.subs(x, a0))})}}{{{b0} - ({a0})}} = {num(m)}$.'))
    # L1: f(a+h)
    for k in range(10):
        c = fs[(k * 5 + 3) % len(fs)]
        f = P(c)
        a0 = R.choice([1, 2, 3, -1, -2])
        val = sp.expand(f.subs(x, a0 + h))
        ans = tidy(poly_str(sp.Poly(val, h).all_coeffs(), 'h'))
        Q.append(E(d, d.qid('A'), f'For {F("f(x)", poly_str(c))}, find $f({a0} + h)$. Multiply it out.', ans, val, ['h'], label=f'$f({a0} + h)$ =', level=1,
                   explain=f'Replace each $x$ with $({a0} + h)$ and expand.'))
    # L2: simplify the difference quotient
    for k in range(10):
        c = fs[(k * 7 + 1) % len(fs)]
        f = P(c)
        a0 = R.choice([1, 2, 3, -1, -2, 4])
        fah = sp.expand(f.subs(x, a0 + h))
        q = sp.expand((fah - f.subs(x, a0)) / h)
        ans = tidy(poly_str(sp.Poly(q, h).all_coeffs(), 'h'))
        Q.append(E(d, d.qid('Q'), f'For {F("f(x)", poly_str(c))}: $f({a0} + h) = {D(tidy(poly_str(sp.Poly(fah, h).all_coeffs(), "h")))}$ and $f({a0}) = {num(f.subs(x, a0))}$. Simplify the difference quotient.',
                   ans, q, ['h'], label=f'$frac{{f({a0}+h) - f({a0})}}{{h}}$ =', level=2,
                   explain=f'Subtract $f({a0})$, then divide every term by $h$: ${D(ans)}$.'))
    # L2: take the limit
    for k in range(8):
        m1, m0 = R.choice([1, 2, 3, -1, 4]), R.choice([-5, -3, -2, 1, 2, 4, 6, 7])
        qa = tidy(poly_str([m1, m0], 'h'))
        Q.append(N(d.qid('H'), f'The difference quotient for $f$ at $x = 3$ simplifies to ${D(qa)}$. What is $f\'(3)$?', m0, label="$f'(3)$ =", level=2,
                   explain=f'Let $h -> 0$: ${D(qa)} -> {m0}$.'))
    # L2: tangent line from f(a), f'(a)
    for k in range(8):
        a0, fa, m = R.choice([1, 2, 3, 4, -1, -2]), R.choice([0, 1, 3, -2, 5, 7]), R.choice([2, -1, 3, -2, 4, 1, -3])
        ans = tidy(f'{m}(x - {a0}) + {fa}')
        Q.append(E(d, d.qid('T'), f'$f({a0}) = {fa}$ and $f\'({a0}) = {m}$. Write the tangent line at $x = {a0}$.', ans, m * (x - a0) + fa, label='$y$ =', level=2,
                   explain=f"$y = f'(a)(x - a) + f(a) = {D(ans)}$."))
    # L3: the whole definition
    for k in range(12):
        c = fs[(k * 3 + 2) % len(fs)]
        f = P(c)
        a0 = R.choice([1, 2, 3, -1, -2])
        fah = sp.expand(f.subs(x, a0 + h))
        top = sp.expand(fah - f.subs(x, a0))
        q = sp.expand(top / h)
        sfah, stop, sq = [tidy(poly_str(sp.Poly(e, h).all_coeffs(), 'h')) for e in (fah, top, q)]
        der = q.subs(h, 0)
        Q.append(STEPS(d.qid('W'), f'Use the definition to find $f\'({a0})$ for {F("f(x)", poly_str(c))}.', [
            E(d, None, None, sfah, fah, ['h'], label=f'$f({a0} + h)$ =', work=f'$f({a0} + h) = {D(sfah)}$'),
            E(d, None, f'Subtract $f({a0}) = {num(f.subs(x, a0))}$.', stop, top, ['h'], label=f'$f({a0}+h) - f({a0})$ =', work=f'$f({a0}+h) - f({a0}) = {D(stop)}$'),
            E(d, None, 'Divide by $h$.', sq, q, ['h'], label='quotient =', work=f'$frac{{f({a0}+h) - f({a0})}}{{h}} = {D(sq)}$'),
            N(None, 'Let $h -> 0$.', der, label=f"$f'({a0})$ =", work=f"$f'({a0}) = {num(der)}$"),
        ], level=3, explain=f"$f'({a0}) = {num(der)}$."))
    # L3: tangent line problems
    for k in range(6):
        c = fs[(k * 5 + 4) % len(fs)]
        f = P(c)
        a0 = R.choice([1, 2, -1, 3])
        q = sp.expand((sp.expand(f.subs(x, a0 + h)) - f.subs(x, a0)) / h)
        sq = tidy(poly_str(sp.Poly(q, h).all_coeffs(), 'h'))
        fa, m = f.subs(x, a0), q.subs(h, 0)
        line = tidy(f'{num(m)}(x - {a0}) + {num(fa)}')
        Q.append(STEPS(d.qid('G'), f'Find the tangent line to {F("f(x)", poly_str(c))} at $x = {a0}$.', [
            N(None, '', fa, label=f'$f({a0})$ =', work=f'$f({a0}) = {num(fa)}$'),
            E(d, None, 'Simplify the difference quotient.', sq, q, ['h'], label=f'$frac{{f({a0}+h) - f({a0})}}{{h}}$ =', work=f'$frac{{f({a0}+h) - f({a0})}}{{h}} = {D(sq)}$'),
            N(None, '', m, label=f"$f'({a0})$ =", work=f"$f'({a0}) = {num(m)}$"),
            E(d, None, None, line, m * (x - a0) + fa, label='$y$ =', work=f'$y = {D(line)}$'),
        ], level=3, explain=f'$y = {D(line)}$'))
    # L3: f(x) = c/x
    for k in range(4):
        c0, a0 = R.choice([1, 2, 3, 4]), R.choice([1, 2, -1, 3])
        f = c0 / x
        q = sp.simplify((f.subs(x, a0 + h) - f.subs(x, a0)) / h)
        qs = f'{-c0}/({a0}({a0} + h))'.replace('+ -', '- ')
        der = -sp.Rational(c0, a0 ** 2)
        Q.append(STEPS(d.qid('R'), f'Use the definition to find $f\'({a0})$ for $f(x) = frac{{{c0}}}{{x}}$.', [
            E(d, None, 'Combine $frac{' + str(c0) + '}{' + str(a0) + ' + h} - frac{' + str(c0) + '}{' + str(a0) + '}$ over a common denominator, then divide by $h$.',
              qs, q, ['h'], label=f'$frac{{f({a0}+h) - f({a0})}}{{h}}$ =', work=f'$frac{{f({a0}+h) - f({a0})}}{{h}} = {D(qs)}$'),
            N(None, 'Let $h -> 0$.', der, label=f"$f'({a0})$ =", work=f"$f'({a0}) = {frac_str(der)}$"),
        ], level=3, explain=f"$f'({a0}) = -frac{{{c0}}}{{{a0 ** 2}}}$"))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 2. Derivative as a function
def defn_general(d, cs, level=3):
    """steps: the definition of the derivative at a general x, for a polynomial with coefficients cs"""
    f = P(cs)
    fxh = sp.expand(f.subs(x, x + h))
    top = sp.expand(fxh - f)
    q = sp.expand(top / h)
    der = sp.expand(q.subs(h, 0))
    ps = lambda e: tidy(str(e).replace('**', '^').replace('*', ''))
    return STEPS(d.qid('W'), f'Use the definition to find $f\'(x)$ for {F("f(x)", poly_str(cs))}.', [
        E(d, None, 'Replace $x$ with $x + h$ and multiply out.', ps(fxh), fxh, ['x', 'h'], label='$f(x + h)$ =', work=f'$f(x + h) = {D(ps(fxh))}$'),
        E(d, None, 'Subtract $f(x)$. Everything without an $h$ cancels.', ps(top), top, ['x', 'h'], label='$f(x+h) - f(x)$ =', work=f'$f(x+h) - f(x) = {D(ps(top))}$'),
        E(d, None, 'Divide by $h$.', ps(q), q, ['x', 'h'], label='$frac{f(x+h) - f(x)}{h}$ =', work=f'$frac{{f(x+h) - f(x)}}{{h}} = {D(ps(q))}$'),
        E(d, None, 'Let $h -> 0$.', ps(der), der, ['x'], label="$f'(x)$ =", work=f"$f'(x) = {D(ps(der))}$"),
    ], level=level, explain=f"$f'(x) = {D(ps(der))}$")


def deck_func():
    d = Deck('d-func', 'Derivative as a Function', 'Every point gets a slope, so the slopes make a new function.', 'Derivatives')
    L = []
    L.append({'id': 'L1', 'type': 'dtrace', 'title': 'A slope at every point',
              'text': 'Every point on $f$ has a slope. Slide along $f(x) = x^3 - 3x$. Each slope you visit drops a dot on the lower graph.',
              'fn': 'x^3-3*x', 'window': [-2.2, 2.2, -3.2, 3.2], 'dwindow': [-4, 12], 'dstep': 2,
              'after': "Those dots are the graph of $f'$. It crosses 0 exactly where $f$ is flat ($x = -1$ and $x = 1$), it is above the axis where $f$ rises, and below where $f$ falls."})
    L.append(MC('L2', "Where the graph of $f$ has a **flat** (horizontal) tangent line, the graph of $f'$…",
                ['is on the $x$-axis ($f\' = 0$)', 'has a flat tangent too', 'is undefined', 'is at its highest point'],
                hint='A flat line has slope 0.', explain="A horizontal tangent has slope 0, so $f' = 0$ there."))
    L.append(STEPS('L3', "The same definition works at **every** $x$: $f'(x) = lim[h->0] frac{f(x+h) - f(x)}{h}$. Find $f'(x)$ for $f(x) = x^2 - x$.", [
        E(d, 'L3.1', 'Replace $x$ with $x + h$ and multiply out.', 'x^2 + 2xh + h^2 - x - h', (x + h) ** 2 - (x + h), ['x', 'h'], label='$f(x + h)$ =',
          hint='$(x + h)^2 - (x + h)$, and $(x + h)^2 = x^2 + 2xh + h^2$.', work='$f(x + h) = x^2 + 2xh + h^2 - x - h$'),
        E(d, 'L3.2', 'Subtract $f(x) = x^2 - x$.', '2xh + h^2 - h', 2 * x * h + h ** 2 - h, ['x', 'h'], label='$f(x+h) - f(x)$ =',
          hint='The $x^2$ and the $-x$ cancel.', work='$f(x+h) - f(x) = 2xh + h^2 - h$'),
        E(d, 'L3.3', 'Divide by $h$, then let $h -> 0$.', '2x - 1', 2 * x - 1, ['x'], label="$f'(x)$ =",
          hint='Dividing by $h$ gives $2x + h - 1$.', work="$f'(x) = 2x - 1$"),
    ]))
    L.append(PICK('L4', 'People write the derivative of $y = f(x)$ many ways. Select **all** that mean the derivative.',
                  ["$f'(x)$", "$y'$", '$frac{dy}{dx}$', '$frac{d}{dx} f(x)$', '$frac{dx}{dy}$', '$f(x)^2$'], [0, 1, 2, 3],
                  hint='Four of them are standard names for the derivative.', explain="$f'(x)$, $y'$, $frac{dy}{dx}$ and $frac{d}{dx} f(x)$ all mean the same thing."))
    L.append(MATCH('L5', 'Take the derivative of the derivative to get the **second derivative**. If $s(t)$ is position, match each one.',
                   [["$s(t)$", 'position'], ["$s'(t)$", 'velocity'], ["$s''(t)$", 'acceleration'], ["$s'''(t)$", 'jerk']],
                   hint='Velocity is how fast position changes; acceleration is how fast velocity changes.',
                   explain='Each derivative tells how fast the one before it is changing.'))
    d.lesson(L)

    T = [
        TF('T1', 'If $f$ is differentiable at $a$, then $f$ is continuous at $a$.', True, explain='Differentiable implies continuous.'),
        TF('T2', 'If $f$ is continuous at $a$, then $f$ is differentiable at $a$.', False, explain='$|x|$ is continuous at 0 but has a corner there, so it is not differentiable. The converse is not true.'),
        PICK('T3', 'At which of these does the derivative **fail** to exist? Select all.', ['a sharp corner', 'a cusp', 'a vertical tangent line', 'a jump', 'a smooth hilltop', 'a point where $f(x) = 0$'], [0, 1, 2, 3],
             explain='Corners, cusps, vertical tangents and breaks have no single slope. A smooth hilltop has slope 0, and $f(x) = 0$ says nothing about the slope.'),
        MC('T4', "On an interval where $f$ is **increasing**, $f'$ is", ['positive', 'negative', 'zero', 'increasing'], explain='Rising graph, positive slopes.'),
        MC('T5', "On an interval where $f$ is **decreasing**, the graph of $f'$ is", ['below the $x$-axis', 'above the $x$-axis', 'on the $x$-axis', 'decreasing'], explain='Falling graph, negative slopes.'),
        MATCH('T6', 'Match each derivative of position $s(t)$ to its name.', [["$s'(t)$", 'velocity'], ["$s''(t)$", 'acceleration'], ["$s'''(t)$", 'jerk']], explain='Each is the rate of change of the one before.'),
        MC('T7', '$frac{d^2 y}{dx^2}$ means', ['the second derivative of $y$', 'the derivative squared', '$y$ times 2', 'the derivative of $x^2$'], explain="$frac{d^2y}{dx^2} = y''$: the derivative of the derivative."),
        MC('T8', "In $f'(x) = lim[h->0] frac{f(x+h) - f(x)}{h}$, the answer is a function of", ['$x$', '$h$', 'both $x$ and $h$', 'neither'], explain='$h$ goes away in the limit. What is left depends on $x$: a slope for every $x$.'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    g1 = d.graph('cubic', {'window': [-2.4, 2.4, -3.2, 3.2], 'pieces': [{'expr': 'x^3-3*x', 'from': -2.4, 'to': 2.4}]})
    g2 = d.graph('hill', {'window': [-1, 4, -2, 5], 'pieces': [{'expr': '4-(x-1)^2', 'from': -1, 'to': 4}]})
    g3 = d.graph('wave', {'window': [-3, 3, -2.5, 2.5], 'pieces': [{'expr': '2*sin(pi*x/2)', 'from': -3, 'to': 3}]})
    pts = [(g1, 'x^3-3*x', [-2, -1, 0, 1, 2, -1.5, 1.5]), (g2, '4-(x-1)^2', [-0.5, 0, 1, 2, 3]), (g3, '2*sin(pi*x/2)', [-3, -2, -1, 0, 1, 2, 3])]
    OPTS = ['positive', 'negative', 'zero']
    for g, fe, xs in pts:
        fx = S(fe.replace('*', ' '))
        for x0 in xs:
            sl = sp.diff(fx, x).subs(x, x0)
            k = 2 if abs(float(sl)) < 1e-9 else 0 if sl > 0 else 1
            Q.append(MC(d.qid('G'), f"Use the graph of $f$. Is $f'({x0})$ positive, negative, or zero?", OPTS, k, graph=g, fixed=True, level=1,
                        explain=['The graph is rising there, so the slope is positive.', 'The graph is falling there, so the slope is negative.', 'The tangent line is flat there, so the slope is 0.'][k]))
    cs_list = [[1, 0, 0], [1, 1, 0], [2, 0, 1], [1, -2, 3], [3, -4, 1], [1, 0, -4], [-1, 2, 0], [2, -1, 0], [1, 3, -2], [-2, 0, 5], [0, 3, 1], [0, -2, 7], [4, 0, -3], [1, -1, 1]]
    ps = lambda e: tidy(str(e).replace('**', '^').replace('*', ''))
    for k in range(8):
        cs = cs_list[(k * 3) % len(cs_list)]
        f = P(cs)
        fxh = sp.expand(f.subs(x, x + h))
        Q.append(E(d, d.qid('A'), f'For {F("f(x)", poly_str(cs))}, find $f(x + h)$. Multiply it out.', ps(fxh), fxh, ['x', 'h'], label='$f(x + h)$ =', level=1,
                   explain=f'Replace every $x$ with $(x + h)$: ${D(ps(fxh))}$.'))
    for k in range(10):
        cs = cs_list[(k * 5 + 1) % len(cs_list)]
        f = P(cs)
        fxh = sp.expand(f.subs(x, x + h))
        q = sp.expand((fxh - f) / h)
        Q.append(E(d, d.qid('Q'), f'For {F("f(x)", poly_str(cs))}, $f(x + h) - f(x) = {D(ps(sp.expand(fxh - f)))}$. Divide by $h$.', ps(q), q, ['x', 'h'],
                   label='$frac{f(x+h) - f(x)}{h}$ =', level=2, explain=f'Divide each term by $h$: ${D(ps(q))}$.'))
    for k in range(8):
        m2, m1, m0 = R.choice([2, 4, 6, -2, 3]), R.choice([1, 2, 3, -1]), R.choice([-5, -1, 0, 2, 3])
        qq = m2 * x + m1 * h + m0
        Q.append(E(d, d.qid('H'), f'The difference quotient simplifies to ${D(ps(qq))}$. Let $h -> 0$.', ps(m2 * x + m0), m2 * x + m0, ['x'], label="$f'(x)$ =", level=2,
                   explain=f'Every term with an $h$ goes to 0: ${D(ps(m2 * x + m0))}$.'))
    sv = [("$s'(3) = 5$", 'At $t = 3$, the velocity is 5.', ['At $t = 3$, the position is 5.', 'At $t = 3$, the acceleration is 5.', 'At $t = 5$, the velocity is 3.']),
          ("$s''(2) = -4$", 'At $t = 2$, the acceleration is −4.', ['At $t = 2$, the velocity is −4.', 'At $t = 2$, the position is −4.', 'At $t = -4$, the acceleration is 2.']),
          ("$v'(1) = 9$", 'At $t = 1$, the acceleration is 9.', ['At $t = 1$, the velocity is 9.', 'At $t = 1$, the position is 9.', 'At $t = 9$, the velocity is 1.']),
          ("$s'(4) = 0$", 'At $t = 4$, the object is momentarily stopped.', ['At $t = 4$, the object is at the starting line.', 'At $t = 4$, the acceleration is 0.', 'At $t = 4$, the object is speeding up.'])]
    for stmt, right, wrong in sv:
        Q.append(MC(d.qid('V'), f'$s(t)$ is position and $v(t)$ is velocity. What does {stmt} say?', [right] + wrong, level=2,
                    explain="$s'$ is velocity, $s''$ (or $v'$) is acceleration."))
    for k in range(10):
        Q.append(defn_general(d, cs_list[(k * 4 + 2) % len(cs_list)]))
    for c0 in [1, 2, 3]:
        Q.append(STEPS(d.qid('R'), f'Use the definition to find $f\'(x)$ for $f(x) = frac{{{c0}}}{{x}}$.', [
            MC(None, f'$frac{{{c0}}}{{x + h}} - frac{{{c0}}}{{x}}$ over a common denominator is', [f'$frac{{-{c0}h}}{{x(x + h)}}$', f'$frac{{{c0}h}}{{x(x + h)}}$', f'$frac{{-{c0}}}{{h}}$', '$0$'],
               work=f'$f(x+h) - f(x) = frac{{-{c0}h}}{{x(x + h)}}$'),
            E(d, None, 'Divide by $h$.', f'-{c0}/(x(x + h))', -c0 / (x * (x + h)), ['x', 'h'], label='$frac{f(x+h) - f(x)}{h}$ =', work=f'$frac{{f(x+h) - f(x)}}{{h}} = frac{{-{c0}}}{{x(x + h)}}$'),
            E(d, None, 'Let $h -> 0$.', f'-{c0}/x^2', -c0 / x ** 2, ['x'], label="$f'(x)$ =", work=f"$f'(x) = -frac{{{c0}}}{{x^2}}$"),
        ], level=3, explain=f"$f'(x) = -frac{{{c0}}}{{x^2}}$"))
    for c0 in [1, 3]:
        Q.append(STEPS(d.qid('R'), f'Use the definition to find $f\'(x)$ for $f(x) = {"" if c0 == 1 else c0}sqrt(x)$.', [
            MC(None, 'Multiply top and bottom of $frac{sqrt(x+h) - sqrt(x)}{h}$ by the **conjugate** $sqrt(x+h) + sqrt(x)$. The top becomes', ['$h$', '$x + h - x^2$', '$2sqrt(x)$', '$h^2$'],
               work='$(sqrt(x+h) - sqrt(x))(sqrt(x+h) + sqrt(x)) = h$'),
            MC(None, 'Cancel the $h$. The quotient is now', ['$frac{1}{sqrt(x+h) + sqrt(x)}$', '$sqrt(x+h) + sqrt(x)$', '$frac{h}{sqrt(x)}$', '$1$'], work='$frac{1}{sqrt(x+h) + sqrt(x)}$'),
            E(d, None, f'Let $h -> 0$ (and remember the {c0} in front).', f'{c0}/(2sqrt(x))', c0 / (2 * sp.sqrt(x)), ['x'], label="$f'(x)$ =", keys=['sqrt('],
              work=f"$f'(x) = frac{{{c0}}}{{2sqrt(x)}}$"),
        ], level=3, explain=f"$f'(x) = frac{{{c0}}}{{2sqrt(x)}}$"))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 3. Derivative rules
def pw(c, n, var='x'):
    """c x^n in app syntax"""
    c, n = sp.nsimplify(c), sp.nsimplify(n)
    if c == 0:
        return '0'
    cs = '' if c == 1 else '-' if c == -1 else (str(c) if c.is_Integer else '(' + frac_str(c) + ')')
    if n == 0:
        return str(c) if c.is_Integer else frac_str(c)
    ns = '' if n == 1 else ('^' + str(n) if (n.is_Integer and n > 0) else '^(' + frac_str(n) + ')')
    return cs + var + ns


def pstr(e, var='x'):
    return tidy(poly_str(sp.Poly(sp.expand(e), sp.Symbol(var)).all_coeffs(), var))


def deck_rules():
    d = Deck('d-rules', 'Derivative Rules', 'Shortcuts so you never need the limit definition again.', 'Derivatives')
    L = []
    L.append(MC('L1', '**Power rule:** $frac{d}{dx} x^n = nx^(n-1)$. Bring the power down in front, then lower the power by one. What is $frac{d}{dx} x^5$?',
                ['$5x^4$', '$x^4$', '$5x^5$', '$4x^5$'], hint='Bring the 5 down, then subtract 1 from the power.', explain='$5x^4$'))
    L.append(E(d, 'L2', 'Constants in front stay, and a sum is differentiated one term at a time. A constant alone has derivative 0. Find the derivative of $f(x) = 3x^2 + 2x + 1$.',
               '6x + 2', 6 * x + 2, label="$f'(x)$ =", hint='$3x^2 -> 3·2x$, $2x -> 2$, and $1 -> 0$.', explain='$6x + 2$'))
    L.append(STEPS('L3', '**Product rule:** if $f = gk$ then $f\' = gk\' + g\'k$. Take $f(x) = (x^2 + 2)(3x + 1)$ with $g = x^2 + 2$ and $k = 3x + 1$.', [
        E(d, 'L3.1', None, '2x', 2 * x, label="$g'$ =", hint='Power rule on $x^2$; the 2 is a constant.', work="$g' = 2x$"),
        E(d, 'L3.2', None, '3', sp.Integer(3), label="$k'$ =", hint='The slope of $3x + 1$.', work="$k' = 3$"),
        E(d, 'L3.3', "Put it together: $gk' + g'k$.", '(x^2 + 2)(3) + 2x(3x + 1)', 9 * x ** 2 + 2 * x + 6, label="$f'(x)$ =",
          hint="$(x^2 + 2)·3 + 2x·(3x + 1)$", work="$f'(x) = 3(x^2 + 2) + 2x(3x + 1)$"),
    ]))
    L.append(STEPS('L4', '**Quotient rule:** $(frac{g}{k})\' = frac{kg\' - gk\'}{k^2}$ ("low d-high minus high d-low, over low squared"). Take $f(x) = frac{4x^2}{2x + 1}$.', [
        E(d, 'L4.1', None, '8x', 8 * x, label="top: $g'$ =", hint='$4x^2 -> 4·2x$', work="$g' = 8x$"),
        E(d, 'L4.2', None, '2', sp.Integer(2), label="bottom: $k'$ =", work="$k' = 2$", hint='The slope of $2x + 1$.'),
        E(d, 'L4.3', 'Low d-high minus high d-low, over low squared.', '((2x + 1)(8x) - 4x^2(2))/(2x + 1)^2', sp.diff(4 * x ** 2 / (2 * x + 1), x), label="$f'(x)$ =",
          hint='$frac{(2x + 1)(8x) - (4x^2)(2)}{(2x + 1)^2}$. Use ( ) around the top and the bottom.', work="$f'(x) = frac{(2x + 1)(8x) - 8x^2}{(2x + 1)^2}$"),
    ]))
    L.append(E(d, 'L5', 'The power rule works for **negative** powers too. Rewrite $f(x) = frac{1}{x^3}$ as $x^(-3)$, then use the power rule.',
               '-3x^(-4)', -3 * x ** -4, label="$f'(x)$ =", hint='Bring down the $-3$, then $-3 - 1 = -4$.', explain='$-3x^(-4) = -frac{3}{x^4}$'))
    d.lesson(L)

    T = [
        MATCH('T1', 'Match each rule to its formula.', [['Constant rule', "$frac{d}{dx}(c) = 0$"], ['Power rule', '$frac{d}{dx} x^n = nx^(n-1)$'],
              ['Constant multiple rule', "$frac{d}{dx}(cf) = cf'$"], ['Sum rule', "$(f + g)' = f' + g'$"]], explain='These four handle every polynomial.'),
        MC('T2', 'The product rule says $(gk)\' =$', ["$gk' + g'k$", "$g'k'$", "$g'k - gk'$", "$frac{g'}{k'}$"], explain="Each factor takes a turn being differentiated: $gk' + g'k$."),
        TF('T3', 'The derivative of a product is the product of the derivatives.', False, explain="No! $(x·x)' = (x^2)' = 2x$, but $(x)'(x)' = 1$."),
        MC('T4', 'The quotient rule says $(frac{g}{k})\' =$', ["$frac{kg' - gk'}{k^2}$", "$frac{gk' - kg'}{k^2}$", "$frac{g'}{k'}$", "$frac{kg' + gk'}{k^2}$"],
           explain='Low d-high minus high d-low, over low squared. The order matters because of the minus sign.'),
        MC('T5', 'To use the power rule on $frac{5}{x^4}$, first rewrite it as', ['$5x^(-4)$', '$5x^4$', '$x^(-5)$', '$frac{1}{5}x^4$'], explain='$frac{1}{x^4} = x^(-4)$.'),
        MC('T6', '$sqrt(x)$ is the same as', ['$x^(1/2)$', '$x^2$', '$x^(-2)$', '$frac{x}{2}$'], explain='A square root is the $frac{1}{2}$ power.'),
        MC('T7', 'What is $frac{d}{dx}(pi^2)$?', ['$0$', '$2pi$', '$pi^2$', '$2x$'], explain='$pi^2$ is just a number (about 9.87), so its derivative is 0.'),
        TF('T8', "$(f - g)' = f' - g'$", True, explain='Derivatives go term by term, sums and differences alike.'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    terms = [(3, 2), (5, 3), (2, 4), (-4, 3), (7, 1), (1, 6), (2, -1), (3, -2), (-1, -3), (4, sp.Rational(1, 2)), (6, sp.Rational(3, 2)), (2, sp.Rational(-1, 2)), (9, sp.Rational(1, 3)), (-2, 5)]
    for c, n in terms:
        f, ans = pw(c, n), pw(c * n, n - 1)
        Q.append(E(d, d.qid('P'), f'Find the derivative of $f(x) = {D(f)}$.', ans, sp.diff(c * x ** n, x), label="$f'(x)$ =", level=1,
                   explain=f'Bring down the ${frac_str(n)}$ and lower the power by 1: ${D(ans)}$.'))
    rw = [('frac{1}{x^3}', -3), ('sqrt(x)', sp.Rational(1, 2)), ('frac{1}{x}', -1), ('frac{1}{sqrt(x)}', sp.Rational(-1, 2)), ('x^2 sqrt(x)', sp.Rational(5, 2)),
          ('frac{1}{x^5}', -5), ('x sqrt(x)', sp.Rational(3, 2))]
    for disp, n in rw:
        Q.append(N(d.qid('X'), f'Rewrite as a power of $x$: ${disp} = x^n$. What is $n$?', n, label='$n$ =', level=1,
                   explain=f'${disp} = x^({frac_str(n)})$'))
    for k in range(8):
        cs = [R.choice([1, 2, -3, 4, 5]), R.choice([0, -2, 3, 1]), R.choice([2, -1, 6, 0]), R.choice([7, -4, 1, 0, 9])][k % 2:]
        f = P(cs)
        Q.append(E(d, d.qid('Y'), f'Find the derivative of {F("f(x)", poly_str(cs))}.', pstr(sp.diff(f, x)), sp.diff(f, x), label="$f'(x)$ =", level=2 if len(cs) == 4 else 1,
                   explain=f'Term by term: ${D(pstr(sp.diff(f, x)))}$.'))
    pairs = [([1, 0, 2], [3, 1]), ([2, -1], [1, 4]), ([1, 0, -3], [2, 5]), ([3, 0], [1, -2, 1]), ([1, 1], [1, -1]), ([4, -1], [1, 0, 1]),
             ([1, 0, 0, 1], [2, 3]), ([5, 2], [1, 0, -1]), ([1, -3], [2, 0, 1]), ([2, 0, 1], [3, -2])]
    for k, (gc, kc) in enumerate(pairs[:8]):
        g, kk = P(gc), P(kc)
        gs, ks, gps, kps = poly_str(gc), poly_str(kc), pstr(sp.diff(g, x)), pstr(sp.diff(kk, x))
        if k % 2 == 0:
            Q.append(E(d, d.qid('F'), f'$f(x) = ({D(gs)})({D(ks)})$. Fill in the missing piece of the product rule.', kps, sp.diff(kk, x),
                       label=f"$f'(x) = ({D(gs)})·($", post=f"$) + ({D(gps)})({D(ks)})$", level=2,
                       explain=f"The missing piece is $k' = {D(kps)}$, the derivative of ${D(ks)}$."))
        else:
            Q.append(E(d, d.qid('F'), f'$f(x) = ({D(gs)})({D(ks)})$. Fill in the missing piece of the product rule.', gps, sp.diff(g, x),
                       label=f"$f'(x) = ({D(gs)})({D(kps)}) + ($", post=f"$)·({D(ks)})$", level=2,
                       explain=f"The missing piece is $g' = {D(gps)}$, the derivative of ${D(gs)}$."))
    qpairs = [([1, 0, 0], [1, 1]), ([3, 0], [2, -1]), ([1, 0, 1], [1, 0]), ([2, 5], [1, 0, 1]), ([1, -2], [1, 3]), ([4, 0, 0], [2, 1]), ([1, 0], [1, 0, 4]), ([5, 0], [1, -1])]
    for k, (gc, kc) in enumerate(qpairs):
        g, kk = P(gc), P(kc)
        gs, ks, gps, kps = poly_str(gc), poly_str(kc), pstr(sp.diff(g, x)), pstr(sp.diff(kk, x))
        Q.append(E(d, d.qid('U'), f'$f(x) = frac{{{D(gs)}}}{{{D(ks)}}}$. Fill in the missing piece of the quotient rule, $frac{{kg\' - gk\'}}{{k^2}}$.', gps, sp.diff(g, x),
                   label=f"$f'(x) = [({D(ks)})·($", post=f"$) - ({D(gs)})({D(kps)})] / ({D(ks)})^2$", level=2,
                   explain=f"The missing piece is the derivative of the top: ${D(gps)}$."))
    for gc, kc in pairs:
        g, kk = P(gc), P(kc)
        gs, ks, gps, kps = poly_str(gc), poly_str(kc), pstr(sp.diff(g, x)), pstr(sp.diff(kk, x))
        ans = f'({gs})({kps}) + ({gps})({ks})'
        Q.append(STEPS(d.qid('W'), f'Use the product rule on $f(x) = ({D(gs)})({D(ks)})$.', [
            E(d, None, f'$g = {D(gs)}$', gps, sp.diff(g, x), label="$g'$ =", work=f"$g' = {D(gps)}$"),
            E(d, None, f'$k = {D(ks)}$', kps, sp.diff(kk, x), label="$k'$ =", work=f"$k' = {D(kps)}$"),
            E(d, None, "Put it together: $gk' + g'k$. (No need to multiply out.)", ans, sp.diff(g * kk, x), label="$f'(x)$ =", work=f"$f'(x) = {D(ans)}$"),
        ], level=3, explain=f"$f'(x) = {D(ans)}$"))
    for gc, kc in qpairs:
        g, kk = P(gc), P(kc)
        gs, ks, gps, kps = poly_str(gc), poly_str(kc), pstr(sp.diff(g, x)), pstr(sp.diff(kk, x))
        ans = f'(({ks})({gps}) - ({gs})({kps}))/({ks})^2'
        Q.append(STEPS(d.qid('V'), f'Use the quotient rule on $f(x) = frac{{{D(gs)}}}{{{D(ks)}}}$.', [
            E(d, None, None, gps, sp.diff(g, x), label="top: $g'$ =", work=f"$g' = {D(gps)}$"),
            E(d, None, None, kps, sp.diff(kk, x), label="bottom: $k'$ =", work=f"$k' = {D(kps)}$"),
            E(d, None, 'Low d-high minus high d-low, over low squared. Put ( ) around the whole top.', ans, sp.diff(g / kk, x), label="$f'(x)$ =",
              ranges={'x': [0.35, 2.65]}, work=f"$f'(x) = {D(ans)}$"),
        ], level=3, explain=f"$f'(x) = {D(ans)}$"))
    for cs, a0 in [([1, 2, -1], 2), ([2, 0, -3], 1), ([1, -4, 0], -1), ([1, 0, 0, -2], 1), ([3, -1, 2], 0)]:
        f = P(cs)
        fp = sp.diff(f, x)
        line = tidy(f'{num(fp.subs(x, a0))}(x - {a0}) + {num(f.subs(x, a0))}'.replace('- -', '+ '))
        Q.append(STEPS(d.qid('T'), f'Find the tangent line to {F("f(x)", poly_str(cs))} at $x = {a0}$.', [
            N(None, '', f.subs(x, a0), label=f'$f({a0})$ =', work=f'$f({a0}) = {num(f.subs(x, a0))}$'),
            E(d, None, None, pstr(fp), fp, label="$f'(x)$ =", work=f"$f'(x) = {D(pstr(fp))}$"),
            N(None, '', fp.subs(x, a0), label=f"$f'({a0})$ =", work=f"$f'({a0}) = {num(fp.subs(x, a0))}$"),
            E(d, None, "$y = f'(a)(x - a) + f(a)$", line, fp.subs(x, a0) * (x - a0) + f.subs(x, a0), label='$y$ =', work=f'$y = {D(line)}$'),
        ], level=3, explain=f'$y = {D(line)}$'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 4. Trig functions
TRIG = {'sin': ('sin(x)', 'cos(x)'), 'cos': ('cos(x)', '-sin(x)'), 'tan': ('tan(x)', 'sec(x)^2'), 'sec': ('sec(x)', 'sec(x)tan(x)'),
        'csc': ('csc(x)', '-csc(x)cot(x)'), 'cot': ('cot(x)', '-csc(x)^2')}


NICE_D = {'sin(x)': 'cos(x)', 'cos(x)': '-sin(x)', 'tan(x)': 'sec(x)^2', 'sec(x)': 'sec(x)tan(x)', 'csc(x)': '-csc(x)cot(x)', 'cot(x)': '-csc(x)^2'}


def nd(f):
    """derivative of an app-syntax string, written the way we teach it (sec^2 not tan^2 + 1)"""
    return NICE_D.get(f) or sp_app(sp.diff(S(f), x))


def deck_trig():
    d = Deck('d-trig', 'Derivatives of Trig Functions', 'Slide along sine and the cosine appears.', 'Derivatives')
    d.keys = ['sin(', 'cos(', 'tan(', 'sec(']
    L = []
    L.append({'id': 'L1', 'type': 'dtrace', 'title': 'The slopes of sine',
              'text': 'Slide along $f(x) = sin(x)$ and watch its slopes land on the lower graph. Does the new graph look familiar?',
              'fn': 'sin(x)', 'window': [-6.4, 6.4, -1.6, 1.6], 'dwindow': [-1.6, 1.6], 'xstep': 2, 'ystep': 1, 'dstep': 1,
              'after': 'The slopes of $sin(x)$ trace out $cos(x)$. So $frac{d}{dx} sin(x) = cos(x)$.'})
    L.append(MC('L2', 'At $x = 0$, $cos(x)$ is at its top (flat), then it falls. Which graph has exactly those slopes?', ['$-sin(x)$', '$sin(x)$', '$cos(x)$', '$-cos(x)$'],
                hint='The slope starts at 0 and then goes negative. Which graph is 0 at $x = 0$ and then negative?', explain="$frac{d}{dx} cos(x) = -sin(x)$"))
    L.append(STEPS('L3', 'Trig functions follow all the same rules. Find $frac{dy}{dx}$ for $y = x^2 sin(x)$ with the product rule.', [
        E(d, 'L3.1', '$g = x^2$', '2x', 2 * x, label="$g'$ =", hint='Power rule.', work="$g' = 2x$"),
        E(d, 'L3.2', '$k = sin(x)$', 'cos(x)', sp.cos(x), label="$k'$ =", hint='What did the slider show?', work="$k' = cos(x)$"),
        E(d, 'L3.3', "$gk' + g'k$", 'x^2cos(x) + 2xsin(x)', sp.diff(x ** 2 * sp.sin(x), x), label="$y'$ =", hint='$x^2·cos(x) + 2x·sin(x)$',
          work="$y' = x^2 cos(x) + 2x sin(x)$"),
    ]))
    L.append(MATCH('L4', 'The other four come from writing them with sine and cosine and using the quotient rule. Match each function to its derivative.',
                   [['$tan(x)$', '$sec^2(x)$'], ['$sec(x)$', '$sec(x)tan(x)$'], ['$cot(x)$', '$-csc^2(x)$'], ['$csc(x)$', '$-csc(x)cot(x)$']],
                   hint='The "co" functions (cos, cot, csc) all get a minus sign.', explain='Tip: the co-functions get the minus signs.'))
    L.append(MC('L5', 'Derivatives of sine go around a cycle of four: $sin -> cos -> -sin -> -cos -> sin$. What is $frac{d^4}{dx^4} sin(x)$?', ['$sin(x)$', '$cos(x)$', '$-sin(x)$', '$-cos(x)$'],
                hint='Four steps around a cycle of four brings you back to the start.', explain='Every 4 derivatives you are back where you started.'))
    d.lesson(L)

    T = [
        MATCH('T1', 'Match each function to its derivative.', [['$sin(x)$', '$cos(x)$'], ['$cos(x)$', '$-sin(x)$'], ['$tan(x)$', '$sec^2(x)$']], explain='Learn these three by heart.'),
        MATCH('T2', 'Match each function to its derivative.', [['$sec(x)$', '$sec(x)tan(x)$'], ['$csc(x)$', '$-csc(x)cot(x)$'], ['$cot(x)$', '$-csc^2(x)$']], explain='The co-functions get the minus signs.'),
        TF('T3', '$frac{d}{dx} cos(x) = sin(x)$', False, explain='It is $-sin(x)$: cosine starts falling right after $x = 0$.'),
        MC('T4', 'Which limit is the key fact behind $frac{d}{dx} sin(x) = cos(x)$?', ['$lim[x->0] frac{sin(x)}{x} = 1$', '$lim[x->0] sin(x) = 1$', '$lim[x->infty] frac{sin(x)}{x} = 1$', '$lim[x->0] frac{x}{sin(x)} = 0$'],
           explain='It comes from the definition of the derivative with $sin(x + h)$.'),
        MC('T5', 'What is $frac{d^47}{dx^47} cos(x)$?', ['$sin(x)$', '$cos(x)$', '$-sin(x)$', '$-cos(x)$'],
           explain='47 = 44 + 3. After 44 derivatives you are back at $cos(x)$; three more: $-sin(x)$, $-cos(x)$, $sin(x)$.'),
        MC('T6', 'How would you find $frac{d}{dx} tan(x)$ if you forgot it?', ['Write $tan(x) = frac{sin(x)}{cos(x)}$ and use the quotient rule', 'Use the power rule', 'Take the derivative of the top and the bottom separately', 'It cannot be done'],
           explain='$frac{cos(x)cos(x) - sin(x)(-sin(x))}{cos^2(x)} = frac{1}{cos^2(x)} = sec^2(x)$'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    combos = [('3sin(x)', '3cos(x)'), ('5cos(x)', '-5sin(x)'), ('2tan(x)', '2sec(x)^2'), ('sec(x)', 'sec(x)tan(x)'), ('4sin(x) - cos(x)', '4cos(x) + sin(x)'),
              ('x^2 + cos(x)', '2x - sin(x)'), ('csc(x)', '-csc(x)cot(x)'), ('cot(x)', '-csc(x)^2'), ('7x - 2sin(x)', '7 - 2cos(x)'),
              ('tan(x) + sec(x)', 'sec(x)^2 + sec(x)tan(x)'), ('-6cos(x) + x^3', '6sin(x) + 3x^2'), ('2sec(x)', '2sec(x)tan(x)'),
              ('sin(x) + cos(x)', 'cos(x) - sin(x)'), ('3x^2 - tan(x)', '6x - sec(x)^2')]
    for f, ans in combos:
        der = sp.diff(S(f), x)
        Q.append(E(d, d.qid('B'), f'Find the derivative of {F("f(x)", f)}.', ans, der, label="$f'(x)$ =", level=1, keys=d.keys + ['csc(', 'cot('],
                   ranges={'x': [0.3, 1.3]}, explain=f"${D(ans)}$"))
    for f, x0 in [('sin(x)', '0'), ('cos(x) + 2x', '0'), ('tan(x)', '0'), ('5sin(x) + x', '0'), ('sec(x)', '0'), ('x + cos(x)', 'pi')]:
        fe = S(f)
        v = sp.diff(fe, x).subs(x, S(x0))
        Q.append(N(d.qid('V'), f'For {F("f(x)", f)}, find $f\'({x0})$.', v, label=f"$f'({x0})$ =", level=1, explain=f"$f'(x) = {D(sp_app(sp.diff(fe, x)))}$, so $f'({x0}) = {num(v)}$."))
    prods = [('x', 'cos(x)'), ('x^2', 'sin(x)'), ('x', 'tan(x)'), ('x^3', 'cos(x)'), ('sin(x)', 'cos(x)'), ('x', 'sec(x)'), ('4x', 'sin(x)'), ('x^2', 'tan(x)')]
    for k, (g, kk) in enumerate(prods):
        ge, ke = S(g), S(kk)
        gp, kp = nd(g), nd(kk)
        if k % 2 == 0:
            Q.append(E(d, d.qid('F'), f'$f(x) = {D(g)}·{D(kk)}$. Fill in the missing piece of the product rule.', kp, sp.diff(ke, x), label=f"$f'(x) = {D(g)}·($",
                       post=f"$) + ({D(gp)})·{D(kk)}$", level=2, ranges={'x': [0.3, 1.3]}, explain=f"The derivative of ${D(kk)}$ is ${D(kp)}$."))
        else:
            Q.append(E(d, d.qid('F'), f'$f(x) = {D(g)}·{D(kk)}$. Fill in the missing piece of the product rule.', gp, sp.diff(ge, x), label=f"$f'(x) = {D(g)}·({D(kp)}) + ($",
                       post=f"$)·{D(kk)}$", level=2, ranges={'x': [0.3, 1.3]}, explain=f"The derivative of ${D(g)}$ is ${D(gp)}$."))
    cyc = ['sin(x)', 'cos(x)', '-sin(x)', '-cos(x)']
    for n, start in [(2, 0), (3, 0), (4, 1), (5, 1), (6, 0), (47, 1), (10, 0), (101, 0)]:
        ans = cyc[(start + n) % 4]
        opts = [f'${D(c)}$' for c in cyc]
        Q.append(MC(d.qid('C'), f'What is $frac{{d^{n}}}{{dx^{n}}} {cyc[start]}$?', opts, opts.index(f'${D(ans)}$'), fixed=True, level=2,
                    explain=f'The derivatives repeat every 4. {n} = {4 * (n // 4)} + {n % 4}, so take {n % 4} more step{"s" if n % 4 != 1 else ""} from ${D(cyc[start])}$.'))
    quots = [('cos(x)', '2x'), ('sin(x)', 'x'), ('cos(x)', 'x^2 + 1'), ('x', 'cos(x)'), ('sin(x)', '1 + cos(x)'), ('x^2', 'sin(x)')]
    for g, kk in quots:
        ge, ke = S(g), S(kk)
        gp, kp = nd(g), nd(kk)
        ans = f'(({kk})({gp}) - ({g})({kp}))/({kk})^2'
        Q.append(STEPS(d.qid('Q'), f'Use the quotient rule on $f(x) = frac{{{D(g)}}}{{{D(kk)}}}$.', [
            E(d, None, None, gp, sp.diff(ge, x), label="top: $g'$ =", ranges={'x': [0.3, 1.3]}, work=f"$g' = {D(gp)}$"),
            E(d, None, None, kp, sp.diff(ke, x), label="bottom: $k'$ =", ranges={'x': [0.3, 1.3]}, work=f"$k' = {D(kp)}$"),
            E(d, None, 'Low d-high minus high d-low, over low squared.', ans, sp.diff(ge / ke, x), label="$f'(x)$ =", ranges={'x': [0.3, 1.3]}, work=f"$f'(x) = {D(ans)}$"),
        ], level=3, explain=f"$f'(x) = {D(ans)}$"))
    for g, kk in prods:
        ge, ke = S(g), S(kk)
        gp, kp = nd(g), nd(kk)
        ans = f'{g}({kp}) + ({gp}){kk}'
        Q.append(STEPS(d.qid('W'), f'Use the product rule on $f(x) = {D(g)}·{D(kk)}$.', [
            E(d, None, f'$g = {D(g)}$', gp, sp.diff(ge, x), label="$g'$ =", ranges={'x': [0.3, 1.3]}, work=f"$g' = {D(gp)}$"),
            E(d, None, f'$k = {D(kk)}$', kp, sp.diff(ke, x), label="$k'$ =", ranges={'x': [0.3, 1.3]}, work=f"$k' = {D(kp)}$"),
            E(d, None, "$gk' + g'k$", ans, sp.diff(ge * ke, x), label="$f'(x)$ =", ranges={'x': [0.3, 1.3]}, work=f"$f'(x) = {D(ans)}$"),
        ], level=3, explain=f"$f'(x) = {D(ans)}$"))
    for f, x0 in [('frac{x}{x^2 + 1}', 0), ('x cos(x)', 0), ('sin(x)cos(x)', 0), ('(x^2 + 1) + (x - 2)', 1)]:
        fe = S(f.replace('frac{x}{x^2 + 1}', 'x/(x^2 + 1)'))
        fp = sp.diff(fe, x)
        Q.append(STEPS(d.qid('S'), f'Find the slope of the tangent line to $y = {f}$ at $x = {x0}$.', [
            E(d, None, None, sp_app(fp), fp, label="$y'$ =", ranges={'x': [0.3, 1.3]}, work=f"$y' = {D(sp_app(fp))}$"),
            N(None, f'Plug in $x = {x0}$.', fp.subs(x, x0), label='slope =', work=f'slope = ${num(fp.subs(x, x0))}$'),
        ], level=3, explain=f'The slope is ${num(fp.subs(x, x0))}$.'))
    Q.append(STEPS(d.qid('A'), 'A particle has position $s(t) = 2sin(t) - t$ for $0 <= t <= 2pi$. When is it at rest?', [
        E(d, None, None, '2cos(t) - 1', 2 * sp.cos(t) - 1, ['t'], label="$v(t) = s'(t)$ =", keys=['sin(', 'cos('], work="$v(t) = 2cos(t) - 1$"),
        MC(None, 'At rest means $v(t) = 0$, so $cos(t) = frac{1}{2}$. In $[0, 2pi]$ that happens at', ['$t = frac{pi}{3}$ and $t = frac{5pi}{3}$', '$t = frac{pi}{6}$ and $t = frac{5pi}{6}$', '$t = 0$ and $t = pi$', '$t = frac{pi}{2}$ only'],
           work='$t = frac{pi}{3}$ and $t = frac{5pi}{3}$'),
    ], level=3, explain="$v(t) = 2cos(t) - 1 = 0$ when $cos(t) = frac{1}{2}$."))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 5. Chain rule
OUTS = {'u^10': '10u^9', 'sin(u)': 'cos(u)', 'sqrt(u)': '1/(2sqrt(u))', 'u^2': '2u', 'tan(u)': 'sec(u)^2', 'sec(u)': 'sec(u)tan(u)', 'u^3': '3u^2',
        '1/u^3': '-3/u^4', 'cos(u)': '-sin(u)', 'u^4': '4u^3', 'u^5': '5u^4', 'u^(-2)': '-2u^(-3)', 'u^7': '7u^6', '1/u': '-1/u^2', 'u^6': '6u^5'}


def _call(g):
    """is g one function call like tan(x) or sqrt(x^2 + 1)?"""
    m = re.match(r'^[a-z]+\(', g)
    if not m or not g.endswith(')'):
        return False
    dpt = 0
    for i, c in enumerate(g[m.end() - 1:]):
        dpt += (c == '(') - (c == ')')
        if dpt == 0 and i < len(g) - m.end():
            return False
    return True


def sub_u(s_, g):
    """put the inside function g in for u, with parentheses only where they are needed"""
    out = ''
    i = 0
    while i < len(s_):
        c = s_[i]
        if c == 'u':
            inarg = i > 0 and s_[i - 1] == '(' and i + 1 < len(s_) and s_[i + 1] == ')'
            if inarg or _call(g) or re.fullmatch(r'[a-z]', g):
                out += g
            else:
                out += '(' + g + ')'
        else:
            out += c
        i += 1
    return out


# (outside, inside, how f is shown)
COMPS = [('u^10', '3x^2 + 1', '(3x^2 + 1)^10'), ('sin(u)', 'x^2', 'sin(x^2)'), ('sqrt(u)', '1 - x^2', 'sqrt(1 - x^2)'), ('u^2', 'tan(x)', 'tan^2(x)'),
         ('tan(u)', 'x^2 - 2x + 5', 'tan(x^2 - 2x + 5)'), ('sec(u)', '4x^5 + 5', 'sec(4x^5 + 5)'), ('u^3', 'x + sin(x)', '(x + sin(x))^3'),
         ('1/u^3', '3x - 1', 'frac{1}{(3x - 1)^3}'), ('cos(u)', '5x', 'cos(5x)'), ('sqrt(u)', 'x^2 - x + 1', 'sqrt(x^2 - x + 1)'), ('u^4', '2x^3 - x', '(2x^3 - x)^4'),
         ('sin(u)', '1/x', 'sin(frac{1}{x})'), ('u^5', 'cos(x)', 'cos^5(x)'), ('cos(u)', 'x^3', 'cos(x^3)'), ('tan(u)', '3x', 'tan(3x)'),
         ('u^(-2)', 'x^2 + 4', '(x^2 + 4)^(-2)'), ('sin(u)', 'sqrt(x)', 'sin(sqrt(x))'), ('u^7', '1 - 4x', '(1 - 4x)^7'), ('u^2', 'sin(x)', 'sin^2(x)'),
         ('sqrt(u)', 'sin(x)', 'sqrt(sin(x))'), ('u^6', 'x^2 + x', '(x^2 + x)^6'), ('1/u', 'x^2 + 1', 'frac{1}{x^2 + 1}'), ('cos(u)', 'x^2 + 3x', 'cos(x^2 + 3x)'),
         ('sec(u)', '2x', 'sec(2x)')]
CH_KEYS = ['sin(', 'cos(', 'tan(', 'sec(', 'sqrt(']


def deck_chain():
    d = Deck('d-chain', 'The Chain Rule', 'The derivative of a function inside a function.', 'Derivatives')
    d.keys = CH_KEYS
    L = []
    L.append(MC('L1', 'The chain rule is for a **composition**, a function inside a function: $f(x) = h(g(x))$. In $f(x) = (3x^2 + 1)^10$, what is the **inside** function $g(x)$?',
                ['$3x^2 + 1$', '$(3x^2 + 1)^10$', '$u^10$', '$10$'], hint='What gets raised to the 10th power?',
                explain='The inside is $g(x) = 3x^2 + 1$. The outside is "raise it to the 10th": $h(u) = u^10$.'))
    L.append(STEPS('L2', "**Chain rule:** $f'(x) = h'(g(x))·g'(x)$. Derivative of the outside, with the inside left alone, times the derivative of the inside. Let's do $f(x) = (3x^2 + 1)^10$.", [
        E(d, 'L2.1', 'The outside is $h(u) = u^10$.', '10u^9', 10 * u ** 9, ['u'], label="$h'(u)$ =", hint='Power rule.', work="$h'(u) = 10u^9$"),
        E(d, 'L2.2', 'Put the inside back in for $u$. Leave it alone.', '10(3x^2 + 1)^9', 10 * (3 * x ** 2 + 1) ** 9, label="$h'(g(x))$ =", hint='Replace $u$ with $(3x^2 + 1)$.',
          work="$h'(g(x)) = 10(3x^2 + 1)^9$"),
        E(d, 'L2.3', 'Now the derivative of the inside, $g(x) = 3x^2 + 1$.', '6x', 6 * x, label="$g'(x)$ =", work="$g'(x) = 6x$", hint='Power rule.'),
        E(d, 'L2.4', 'Multiply.', '10(3x^2 + 1)^9(6x)', sp.diff((3 * x ** 2 + 1) ** 10, x), label="$f'(x)$ =", hint='$10(3x^2 + 1)^9·6x$',
          work="$f'(x) = 10(3x^2 + 1)^9·6x$"),
    ]))
    L.append(MC('L3', '$sin^2(x)$ means $(sin(x))^2$. Which function is on the **outside**?', ['the square', 'the sine', 'neither: it is a product', 'the $x$'],
                hint='What is the last thing you would do to compute it on a calculator?', explain="Find $sin(x)$ first, then square it. The square is outside, so $f' = 2sin(x)·cos(x)$."))
    L.append(E(d, 'L4', 'Your turn: $f(x) = sin(x^2)$. Outside: sine. Inside: $x^2$.', 'cos(x^2)(2x)', sp.diff(sp.sin(x ** 2), x), label="$f'(x)$ =",
               hint="Derivative of the outside with the inside left alone: $cos(x^2)$. Then times the derivative of the inside.", explain="$cos(x^2)·2x$"))
    L.append(MC('L5', 'Some functions are three deep: $f(x) = (sin(sqrt(x)))^2$. Peel from the outside in, one factor per layer:\n$f\'(x) = 2sin(sqrt(x))·cos(sqrt(x))·frac{1}{2sqrt(x)}$\nWhich factor is the derivative of the **innermost** function?',
                ['$frac{1}{2sqrt(x)}$', '$cos(sqrt(x))$', '$2sin(sqrt(x))$', '$sqrt(x)$'], hint='The innermost function is $sqrt(x)$.',
                explain='Square → sine → square root. Each layer adds one factor.'))
    d.lesson(L)

    T = [
        MC('T1', 'Which of these is a **composition** (a function inside a function)?', ['$sqrt(sin(x))$', '$x sin(x)$', '$x + sin(x)$', '$frac{sin(x)}{x}$'],
           explain='$sqrt(sin(x))$ puts $sin(x)$ inside the square root. The others combine $x$ and $sin(x)$ by multiplying, adding or dividing.'),
        BANK('T2', "The chain rule: if $f(x) = h(g(x))$ then $f'(x) =$ ___ $·$ ___", ["$h'(g(x))$", "$g'(x)$"], ["$h'(x)$", "$g(x)$", "$h(g'(x))$"],
             explain="Outside derivative (inside left alone) times the inside derivative."),
        MC('T3', 'In Leibniz notation, with $y = h(u)$ and $u = g(x)$, the chain rule is', ['$frac{dy}{dx} = frac{dy}{du}·frac{du}{dx}$', '$frac{dy}{dx} = frac{dy}{du} + frac{du}{dx}$', '$frac{dy}{dx} = frac{du}{dy}·frac{dx}{du}$', '$frac{dy}{dx} = frac{dy}{du}$'],
           explain='It looks like the $du$\'s cancel, which is a nice way to remember it.'),
        TF('T4', '$frac{d}{dx} sin(x^2) = cos(2x)$', False, explain='$cos(x^2)·2x$. The inside $x^2$ stays inside the cosine, and the $2x$ multiplies on the outside.'),
        TF('T5', 'When you take the derivative of the outside function, the inside function is left unchanged.', True, explain='That is why $(3x^2 + 1)^10$ becomes $10(3x^2 + 1)^9$, with $3x^2 + 1$ still inside.'),
        MC('T6', 'A student says $frac{d}{dx}(3x^2 + 1)^10 = 10(3x^2 + 1)^9$. What is missing?', ['the factor $6x$', 'nothing, it is correct', 'the factor $10$', 'a minus sign'],
           explain='Always multiply by the derivative of the inside.'),
        MC('T7', '$f(x) = sin(sin(sin(x)))$. When you use the chain rule, how many factors does $f\'(x)$ have?', ['3', '1', '2', '4'],
           explain='Three layers, three factors: $cos(sin(sin(x)))·cos(sin(x))·cos(x)$.'),
        MC('T8', 'Which one needs the **product** rule, not the chain rule, at the top level?', ['$x sin(x)$', '$sin(x^2)$', '$(x + 1)^5$', '$sqrt(cos(x))$'],
           explain='$x sin(x)$ is $x$ times $sin(x)$: a product.'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    for k, (o, g, disp) in enumerate(COMPS[:13]):
        Q.append(E(d, d.qid('I'), f'Write $f(x) = {disp}$ as $h(g(x))$. What is the **inside** function?', g, S(g), label='$g(x)$ =', level=1, ranges={'x': [0.3, 1.2]},
                   explain=f'The inside is $g(x) = {D(g)}$ and the outside is $h(u) = {D(o)}$.'))
    for k, (o, g, disp) in enumerate(COMPS[11:]):
        Q.append(E(d, d.qid('O'), f'Write $f(x) = {disp}$ as $h(g(x))$ with inside $g(x) = {D(g)}$. What is the **outside** function $h(u)$?', o, S(o), ['u'], label='$h(u)$ =',
                   level=1, explain=f'Put $u$ where the inside was: $h(u) = {D(o)}$.'))
    for o in ['u^10', 'sin(u)', 'sqrt(u)', '1/u^3', 'tan(u)', 'sec(u)', 'u^(-2)', 'cos(u)']:
        Q.append(E(d, d.qid('D'), f'The outside function is $h(u) = {D(o)}$. Find $h\'(u)$.', OUTS[o], sp.diff(S(o), u), ['u'], label="$h'(u)$ =", level=1,
                   explain=f"$h'(u) = {D(OUTS[o])}$"))
    for k, (o, g, disp) in enumerate(COMPS[2:12]):
        hg = sub_u(OUTS[o], g)
        Q.append(E(d, d.qid('P'), f'$f(x) = {disp}$ has outside $h(u) = {D(o)}$, so $h\'(u) = {D(OUTS[o])}$. Put the inside $g(x) = {D(g)}$ back in.', hg,
                   sp.diff(S(o), u).subs(u, S(g)), label="$h'(g(x))$ =", level=2, ranges={'x': [0.3, 0.9]},
                   explain=f"Replace $u$ with ${D(g)}$ and leave it alone: ${D(hg)}$."))
    for k, (o, g, disp) in enumerate(COMPS[:12]):
        hg, gp = sub_u(OUTS[o], g), nd(g)
        Q.append(E(d, d.qid('F'), f'Finish the chain rule for $f(x) = {disp}$.', gp, sp.diff(S(g), x), label=f"$f'(x) = {D(hg)}·($", post='$)$', level=2,
                   ranges={'x': [0.3, 0.9]}, explain=f"The missing factor is the derivative of the inside, ${D(g)}$: that's ${D(gp)}$."))
    for k, (o, g, disp) in enumerate(COMPS[12:18]):
        hg, gp = sub_u(OUTS[o], g), nd(g)
        Q.append(E(d, d.qid('G'), f'Finish the chain rule for $f(x) = {disp}$.', hg, sp.diff(S(o), u).subs(u, S(g)), label="$f'(x) = ($", post=f'$)·({D(gp)})$',
                   level=2, ranges={'x': [0.3, 0.9]}, explain=f"The missing factor is the outside's derivative with the inside left alone: ${D(hg)}$."))
    for k, (o, g, disp) in enumerate(COMPS[:24:2]):
        hp, hg, gp = OUTS[o], sub_u(OUTS[o], g), nd(g)
        fe = S(o).subs(u, S(g))
        ans = f'{hg}({gp})' if not hg.endswith(')') or True else hg
        ans = f'({hg})({gp})'
        Q.append(STEPS(d.qid('W'), f'Use the chain rule on $f(x) = {disp}$.', [
            E(d, None, 'What is inside?', g, S(g), label='$g(x)$ =', ranges={'x': [0.3, 0.9]}, work=f'inside: $g(x) = {D(g)}$'),
            E(d, None, f'The outside is $h(u) = {D(o)}$.', hp, sp.diff(S(o), u), ['u'], label="$h'(u)$ =", work=f"$h'(u) = {D(hp)}$"),
            E(d, None, 'Derivative of the inside.', gp, sp.diff(S(g), x), label="$g'(x)$ =", ranges={'x': [0.3, 0.9]}, work=f"$g'(x) = {D(gp)}$"),
            E(d, None, "$f'(x) = h'(g(x))·g'(x)$", ans, sp.diff(fe, x), label="$f'(x)$ =", ranges={'x': [0.3, 0.9]}, work=f"$f'(x) = {D(ans, False)}$"),
        ], level=3, explain=f"$f'(x) = {D(ans, False)}$"))
    one = [('cos(5x)', '-5sin(5x)'), ('(1 - 4x)^7', '-28(1 - 4x)^6'), ('tan(3x)', '3sec(3x)^2'), ('sin^2(x)', '2sin(x)cos(x)'), ('sqrt(2x + 1)', '1/sqrt(2x + 1)'),
           ('(x^2 + 1)^3', '6x(x^2 + 1)^2'), ('sec(2x)', '2sec(2x)tan(2x)'), ('cos(x^3)', '-3x^2sin(x^3)')]
    for disp, ans in one:
        src = {'sin^2(x)': 'sin(x)^2'}.get(disp, disp)
        Q.append(E(d, d.qid('C'), f'Find the derivative of $f(x) = {D(disp)}$.', ans, sp.diff(S(src), x), label="$f'(x)$ =", level=3, ranges={'x': [0.2, 0.7]},
                   explain=f"${D(ans)}$"))
    dbl = [('(sin(sqrt(x)))^2', [('the square', '2sin(sqrt(x))'), ('the sine', 'cos(sqrt(x))'), ('the square root', '1/(2sqrt(x))')]),
           ('tan^3(x^2 + 2x - 1)', [('the cube', '3tan(x^2 + 2x - 1)^2'), ('the tangent', 'sec(x^2 + 2x - 1)^2'), ('the inside polynomial', '2x + 2')]),
           ('sin(sin(sin(x)))', [('the outer sine', 'cos(sin(sin(x)))'), ('the middle sine', 'cos(sin(x))'), ('the inner sine', 'cos(x)')]),
           ('sqrt(cos(x^2 + 1))', [('the square root', '1/(2sqrt(cos(x^2 + 1)))'), ('the cosine', '-sin(x^2 + 1)'), ('the inside polynomial', '2x')]),
           ('cos^2(3x)', [('the square', '2cos(3x)'), ('the cosine', '-sin(3x)'), ('the inside $3x$', '3')])]
    for disp, layers in dbl:
        src = {'tan^3(x^2 + 2x - 1)': 'tan(x^2 + 2x - 1)^3', 'cos^2(3x)': 'cos(3x)^2'}.get(disp, disp)
        steps = []
        for name, fac in layers:
            steps.append(E(d, None, f'Derivative of {name}, with everything inside it left alone.', fac,
                           S(fac), label='factor =', ranges={'x': [0.2, 0.6]}, work=f'{name}: ${D(fac, False)}$'))
        prod = ''.join(f'({fac})' for _, fac in layers)
        steps.append(E(d, None, 'Multiply all the factors.', prod, sp.diff(S(src), x), label="$f'(x)$ =", ranges={'x': [0.2, 0.6]}, work=f"$f'(x) = {D(prod, False)}$"))
        Q.append(STEPS(d.qid('X'), f'Peel the layers of $f(x) = {D(disp)}$ from the outside in.', steps, level=3, explain=f"$f'(x) = {D(prod, False)}$"))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 6. Implicit differentiation
Yf = sp.Function('Y')(x)


def dimp(e):
    """d/dx of an expression in x and y, with y a function of x; result uses y and yp (= y')"""
    ex = e.subs(y, Yf)
    r = sp.diff(ex, x)
    return r.subs(sp.Derivative(Yf, x), yp).subs(Yf, y)


IMP_KEYS = ["y'", 'sin(', 'cos(', 'tan(']


def deck_implicit():
    d = Deck('d-implicit', 'Implicit Differentiation', 'Finding dy/dx when y is not solved for.', 'Derivatives')
    d.keys = []
    V3 = ['x', 'y', "y'"]
    L = []
    L.append(MC('L1', "$x^2 + y^2 = 1$ is a circle, not a function. We can still find slopes: take $frac{d}{dx}$ of **both sides**, treating $y$ as a function of $x$. Then $frac{d}{dx}(y^2) =$",
                ["$2y·y'$", '$2y$', '$2x$', "$(y')^2$"], hint="$y^2$ is (something)$^2$, and the something depends on $x$. That's the chain rule.",
                explain="Chain rule: $2y$ times the derivative of the inside, $y'$. Every time you differentiate a $y$, a $y'$ appears."))
    L.append(STEPS('L2', 'Find the slope of the circle $x^2 + y^2 = 25$ at the point $(3, 4)$.', [
        E(d, 'L2.1', 'Take $frac{d}{dx}$ of the left side.', "2x + 2yy'", 2 * x + 2 * y * yp, V3, label='$frac{d}{dx}(x^2 + y^2)$ =', keys=["y'"],
          hint="$x^2 -> 2x$ and $y^2 -> 2y·y'$.", work="$2x + 2yy' = 0$"),
        E(d, 'L2.2', "The right side, 25, has derivative 0. Solve $2x + 2yy' = 0$ for $y'$.", '-x/y', -x / y, ['x', 'y'], label="$y'$ =",
          hint="Move $2x$ over, then divide by $2y$.", work="$y' = -frac{x}{y}$"),
        N('L2.3', 'Plug in the point $(3, 4)$.', sp.Rational(-3, 4), label='slope =', hint='$-frac{3}{4}$', work='slope $= -frac{3}{4}$'),
    ]))
    L.append(E(d, 'L3', "Products with $y$ need the product rule. Find $frac{d}{dx}(xy)$.", "y + xy'", y + x * yp, V3, label='$frac{d}{dx}(xy)$ =', keys=["y'"],
               hint="$(x)'·y + x·(y)'$", explain="$1·y + x·y'$"))
    L.append(STEPS('L4', "Find $frac{dy}{dx}$ for $x^3 sin(y) + y = 4x + 3$.", [
        E(d, 'L4.1', 'Left side: product rule on $x^3 sin(y)$, plus the derivative of $y$.', "3x^2sin(y) + x^3cos(y)y' + y'", dimp(x ** 3 * sp.sin(y) + y), V3,
          label='left =', keys=IMP_KEYS, hint="$3x^2 sin(y) + x^3·cos(y)y' + y'$", work="$3x^2 sin(y) + x^3 cos(y)y' + y' = 4$"),
        MC('L4.2', "Get the $y'$ terms together and factor out $y'$:", ["$y'(x^3 cos(y) + 1) = 4 - 3x^2 sin(y)$", "$y'(x^3 cos(y)) = 4$", "$y' = 4 - 3x^2 sin(y)$", "$y'(1 - x^3) = 4$"],
           hint="Move the term without $y'$ to the right side.", work="$y'(x^3 cos(y) + 1) = 4 - 3x^2 sin(y)$"),
        E(d, 'L4.3', 'Divide.', '(4 - 3x^2sin(y))/(x^3cos(y) + 1)', (4 - 3 * x ** 2 * sp.sin(y)) / (x ** 3 * sp.cos(y) + 1), ['x', 'y'], label="$y'$ =", keys=['sin(', 'cos('],
          ranges={'x': [0.2, 0.8], 'y': [0.2, 0.8]}, hint="Put ( ) around the top and around the bottom.", work="$y' = frac{4 - 3x^2 sin(y)}{x^3 cos(y) + 1}$"),
    ]))
    L.append(MC('L5', 'Implicit differentiation also proves the power rule for fractional powers. What is $frac{d}{dx} x^(2/3)$?', ['$frac{2}{3}x^(-1/3)$', '$frac{2}{3}x^(1/3)$', '$frac{3}{2}x^(1/2)$', '$x^(-1/3)$'],
                hint='Same power rule: bring down $frac{2}{3}$ and subtract 1.', explain='$frac{2}{3} - 1 = -frac{1}{3}$'))
    d.lesson(L)

    T = [
        MC('T1', "Why does $frac{d}{dx}(y^2)$ give $2y·y'$ and not just $2y$?", ['$y$ depends on $x$, so the chain rule applies', 'It is a typo; $2y$ is right', 'Because of the product rule', 'Because $y$ is a constant'],
           explain="We treat $y$ as $y(x)$. The derivative of the inside, $y$, is $y'$."),
        TF('T2', "$frac{d}{dx}(y^3) = 3y^2$", False, explain="$3y^2·y'$. Never forget the $y'$."),
        MC('T3', '$frac{d}{dx}(sin(y)) =$', ["$cos(y)·y'$", '$cos(y)$', '$-cos(y)y\'$', "$sin(y')$"], explain='Chain rule with $y$ inside.'),
        MC('T4', '$frac{d}{dx}(x^2 y) =$', ["$2xy + x^2 y'$", "$2xy'$", '$2xy$', "$x^2 y'$"], explain="Product rule: $(x^2)'y + x^2(y)'$."),
        ORDER('T5', 'Put the steps of implicit differentiation in order.', ['Take $frac{d}{dx}$ of both sides', "Move every $y'$ term to one side", "Factor out $y'$", "Divide to solve for $y'$"],
              explain='Differentiate, collect, factor, divide.'),
        MC('T6', "To find the slope of the tangent line at $(a, b)$ from a formula for $y'$ in terms of $x$ and $y$, you", ['plug in $x = a$ and $y = b$', 'plug in only $x = a$', 'set $y\' = 0$', 'solve the original equation for $y$ first'],
           explain="$y'$ usually depends on both $x$ and $y$, so use both coordinates."),
        TF('T7', "The derivative of a constant on the right side, like $x^2 + y^2 = 25$, is 0.", True, explain='25 never changes, so its derivative is 0.'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    single = ['y^2', 'y^3', 'y^4', '3y^2', 'y^5', 'sin(y)', 'cos(y)', 'tan(y)', 'sqrt(y)', 'xy', 'x^2y', 'xy^2', '1/y', '2y^3 + x', 'x^3 + y^3', 'xsin(y)']
    NICE = {'tan(y)': "sec(y)^2y'", 'sqrt(y)': "y'/(2sqrt(y))", '1/y': "-y'/y^2", 'cos(y)': "-sin(y)y'", 'sin(y)': "cos(y)y'"}
    for f in single:
        e = S(f)
        der = dimp(e)
        Q.append(E(d, d.qid('B'), f'$y$ is a function of $x$. Find $frac{{d}}{{dx}}({D(f, False)})$.', NICE.get(f) or sp_app(der), der, V3, label='derivative =', level=1, keys=IMP_KEYS + ['sqrt('],
                   ranges={'x': [0.3, 1.2], 'y': [0.3, 1.2]}, explain=f"${D(sp_app(der), False)}$. Every derivative of something with $y$ gets a $y'$."))
    for m_, n_ in [(2, 3), (1, 3), (3, 4), (5, 2), (-1, 3), (4, 3)]:
        r = sp.Rational(m_, n_)
        ans = pw(r, r - 1)
        Q.append(E(d, d.qid('P'), f'Find $frac{{d}}{{dx}} x^({m_}/{n_})$.', ans, sp.diff(x ** r, x), label='derivative =', level=1, explain=f'${D(ans)}$'))
    solve_items = [("2x + 2yy' = 0", '-x/y'), ("2x + 6yy' = 0", '-x/(3y)'), ("y + xy' = 0", '-y/x'), ("3x^2 + 3y^2y' = 0", '-x^2/y^2'), ("2xy + x^2y' = 0", '-2y/x'),
                   ("1 + 2yy' = 4", '3/(2y)'), ("y' + 2xy' = y", 'y/(1 + 2x)'), ("2x - 2yy' = 0", 'x/y'), ("4x + 2yy' = 0", '-2x/y'), ("cos(y)y' = 2x", '2x/cos(y)'),
                   ("3y^2y' + y' = 1", '1/(3y^2 + 1)'), ("y' + xy' = 5 - y", '(5 - y)/(1 + x)')]
    for eq, ans in solve_items:
        lhs, rhs = eq.split(' = ')
        sol = sp.solve(sp.Eq(S(lhs), S(rhs)), yp)[0]
        Q.append(E(d, d.qid('S'), f"Solve for $y'$: ${eq}$", ans, sol, ['x', 'y'], label="$y'$ =", level=2, keys=['cos('], ranges={'x': [0.3, 1.2], 'y': [0.3, 1.2]},
                   explain=f"$y' = {D(ans)}$"))
    for fo, pt in [('-x/y', (3, 4)), ('-x/y', (-5, 12)), ('-y/x', (2, 3)), ('-x^2/y^2', (1, 2)), ('-2y/x', (2, 1)), ('x/y', (2, 1)), ('-2x/y', (1, 2)), ('3/(2y)', (1, 3))]:
        v = S(fo).subs({x: pt[0], y: pt[1]})
        Q.append(N(d.qid('V'), f"$y' = {D(fo)}$. Find the slope at the point $({pt[0]}, {pt[1]})$.", v, label='slope =', level=2,
                   explain=f'Plug in $x = {pt[0]}$ and $y = {pt[1]}$: ${frac_str(v)}$.'))
    eqs = [('x^2 + y^2', '25', (3, 4)), ('x^2 + y^2', '13', (2, 3)), ('xy', '6', (2, 3)), ('x^2y', '4', (2, 1)), ('x^2 + xy + y^2', '7', (1, 2)),
           ('y^3 + x', '2', (1, 1)), ('x^2 - y^2', '3', (2, 1)), ('2x^2 + 3y^2', '14', (1, 2)), ('y^2', '4x', (1, 2)), ('xy^3', '8', (1, 2)),
           ('x^3 + y^3', '3xy', (sp.Rational(3, 2), sp.Rational(3, 2))), ('xy^2 + cos(x)', 'y', None), ('4x^5 + tan(y)', 'y^2 + 5x', None), ('sin(y) + x^2', 'y', None),
           ('x^2 + 4y^2', '8', (2, 1)), ('xy + y', '6', (1, 3))]
    for lhs, rhs, pt in eqs:
        L_, R_ = S(lhs), S(rhs)
        dl, dr = dimp(L_), dimp(R_)
        sol = sp.simplify(sp.solve(sp.Eq(dl, dr), yp)[0])
        OV = {'4x^5 + tan(y)': ("20x^4 + sec(y)^2y'", '(20x^4 - 5)/(2y - sec(y)^2)'), 'sin(y) + x^2': ("2x + cos(y)y'", '2x/(1 - cos(y))'),
              'x^3 + y^3': (None, '(y - x^2)/(y^2 - x)'), 'xy^2 + cos(x)': (None, '(sin(x) - y^2)/(2xy - 1)')}
        sl = (OV.get(lhs, (None, None))[0]) or sp_app(dl)
        steps = [E(d, None, 'Take $frac{d}{dx}$ of the left side.', sl, dl, V3, label='left =', keys=IMP_KEYS, ranges={'x': [0.3, 1.2], 'y': [0.3, 1.2]},
                   work=f"left: ${D(sl, False)}$")]
        if R_.free_symbols:
            sr = sp_app(dr)
            steps.append(E(d, None, 'Take $frac{d}{dx}$ of the right side.', sr, dr, V3, label='right =', keys=IMP_KEYS, ranges={'x': [0.3, 1.2], 'y': [0.3, 1.2]},
                           work=f"right: ${D(sr, False)}$"))
        ys = OV.get(lhs, (None, None))[1] or sp_app(sol)
        steps.append(E(d, None, "Solve for $y'$.", ys, sol, ['x', 'y'], label="$y'$ =", keys=['sin(', 'cos(', 'tan('], ranges={'x': [0.3, 1.2], 'y': [0.3, 1.2]},
                       work=f"$y' = {D(ys)}$"))
        if pt:
            v = sol.subs({x: pt[0], y: pt[1]})
            steps.append(N(None, f'Slope at $({frac_str(pt[0])}, {frac_str(pt[1])})$.', v, label='slope =', work=f'slope $= {frac_str(v)}$'))
        Q.append(STEPS(d.qid('W'), f"Find $frac{{dy}}{{dx}}$ for ${D(lhs, False)} = {D(rhs, False)}$" + (f' and the slope at $({frac_str(pt[0])}, {frac_str(pt[1])})$.' if pt else '.'),
                       steps, level=3, explain=f"$y' = {D(ys)}$"))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 7. Exponentials
def deck_exp():
    d = Deck('d-exp', 'Derivatives of Exponentials', 'The function that is its own derivative.', 'Derivatives')
    d.keys = ['e^(', 'ln(', 'sin(', 'cos(']
    L = []
    L.append({'id': 'L1', 'type': 'dtrace', 'title': 'A function that is its own slope',
              'text': 'Slide along $f(x) = e^x$ and drop its slopes on the lower graph. Compare the two graphs.',
              'fn': 'exp(x)', 'window': [-2, 2, -0.5, 7.5], 'dwindow': [-0.5, 7.5], 'dstep': 1, 'ystep': 1,
              'after': 'The slopes make the **same** graph. $frac{d}{dx} e^x = e^x$. That is what makes $e$ special.'})
    L.append(MC('L2', 'With the chain rule: $frac{d}{dx} e^(f(x)) = e^(f(x))·f\'(x)$. The exponent stays the same, and you multiply by its derivative. What is $frac{d}{dx} e^(sin(x))$?',
                ['$e^(sin(x))cos(x)$', '$e^(cos(x))$', '$cos(x)e^x$', '$e^(sin(x))$'], hint='Keep $e^(sin(x))$, then multiply by the derivative of the exponent.',
                explain='$e^(sin(x))·cos(x)$'))
    L.append(E(d, 'L3', 'Try it: $f(x) = e^(3x^2 + 1) + x^2$.', 'e^(3x^2 + 1)(6x) + 2x', sp.diff(sp.exp(3 * x ** 2 + 1) + x ** 2, x), label="$f'(x)$ =",
               ranges={'x': [0.1, 0.6]}, hint='$e^(3x^2 + 1)·6x$, plus the derivative of $x^2$.', explain='$6x e^(3x^2 + 1) + 2x$'))
    L.append(MC('L4', 'Other bases pick up a natural log: $frac{d}{dx} b^x = b^x ln(b)$. What is $frac{d}{dx} 2^x$?', ['$2^x ln(2)$', '$x 2^(x-1)$', '$2^x$', '$frac{2^x}{ln(2)}$'],
                hint='This is not the power rule: the $x$ is in the exponent.', explain='$2^x ln(2)$. For $b = e$, $ln(e) = 1$, which is why $e^x$ is so clean.'))
    L.append(STEPS('L5', 'All the old rules still work. Use the quotient rule on $f(x) = frac{e^(x^2)}{x}$.', [
        E(d, 'L5.1', 'Top: $e^(x^2)$ (chain rule).', 'e^(x^2)(2x)', sp.diff(sp.exp(x ** 2), x), label="$g'$ =", ranges={'x': [0.2, 0.8]}, hint='$e^(x^2)$ times the derivative of $x^2$.',
          work="$g' = 2x e^(x^2)$"),
        E(d, 'L5.2', 'Bottom: $x$.', '1', sp.Integer(1), label="$k'$ =", work="$k' = 1$", hint='The slope of $x$.'),
        E(d, 'L5.3', 'Low d-high minus high d-low, over low squared.', '(x(2xe^(x^2)) - e^(x^2))/x^2', sp.diff(sp.exp(x ** 2) / x, x), label="$f'(x)$ =", ranges={'x': [0.2, 0.8]},
          hint='$frac{x·2xe^(x^2) - e^(x^2)·1}{x^2}$', work="$f'(x) = frac{2x^2 e^(x^2) - e^(x^2)}{x^2}$"),
    ]))
    d.lesson(L)

    T = [
        MC('T1', '$frac{d}{dx} e^x =$', ['$e^x$', '$xe^(x-1)$', '$e^(x-1)$', '$ln(x)$'], explain='$e^x$ is its own derivative.'),
        MC('T2', '$frac{d}{dx} e^(g(x)) =$', ["$e^(g(x))·g'(x)$", "$e^(g'(x))$", "$g(x)e^(g(x)-1)$", '$e^(g(x))$'], explain='Chain rule: the exponent stays, times its derivative.'),
        MC('T3', '$frac{d}{dx} b^x =$', ['$b^x ln(b)$', '$xb^(x-1)$', '$b^x$', '$frac{b^x}{ln(b)}$'], explain='Every base other than $e$ picks up $ln(b)$.'),
        TF('T4', '$frac{d}{dx} e^(2x) = e^(2x)$', False, explain='$2e^(2x)$: multiply by the derivative of the exponent.'),
        MATCH('T5', 'Match the exponent rules.', [['$a^x a^y$', '$a^(x+y)$'], ['$frac{a^x}{a^y}$', '$a^(x-y)$'], ['$(a^x)^y$', '$a^(xy)$'], ['$a^(-x)$', '$frac{1}{a^x}$']],
              explain='These let you simplify before you differentiate.'),
        MC('T6', 'Which is the derivative of $x^e$ (a **power** of $x$, not an exponential)?', ['$ex^(e-1)$', '$x^e$', '$e^x$', '$x^e ln(x)$'],
           explain='$e$ is just a number (about 2.718), so the power rule applies.'),
        MC('T7', 'The number $e$ is chosen so that', ['$lim[h->0] frac{e^h - 1}{h} = 1$', '$e^0 = e$', '$e = 3$', '$lim[h->0] e^h = 0$'],
           explain='That limit is the slope of $e^x$ at $x = 0$. Making it 1 makes $frac{d}{dx} e^x = e^x$.'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    basic = [('e^(3x)', '3e^(3x)'), ('5e^x', '5e^x'), ('e^(-x)', '-e^(-x)'), ('2^x', '2^xln(2)'), ('e^x + x^3', 'e^x + 3x^2'), ('e^(5x)', '5e^(5x)'),
             ('3^x', '3^xln(3)'), ('10^x', '10^xln(10)'), ('4e^(2x)', '8e^(2x)'), ('e^(x/2)', 'e^(x/2)/2'), ('e^x - 7x', 'e^x - 7'), ('x^e', 'ex^(e - 1)'),
             ('e^(-4x)', '-4e^(-4x)'), ('e^x + e^2', 'e^x'), ('5^x', '5^xln(5)'), ('6e^x + 2^x', '6e^x + 2^xln(2)')]
    for f, ans in basic:
        Q.append(E(d, d.qid('B'), f'Find the derivative of {F("f(x)", f)}.', ans, sp.diff(S(f), x), label="$f'(x)$ =", level=1, ranges={'x': [0.2, 1.2]}, explain=f'${D(ans)}$'))
    for lhs, ans in [('e^3·e^x', 'x + 3'), ('frac{e^(5x)}{e^x}', '4x'), ('(e^x)^3', '3x'), ('frac{1}{e^(2x)}', '-2x'), ('e^x·e^x', '2x'), ('sqrt(e^x)', 'x/2')]:
        Q.append(E(d, d.qid('R'), f'Simplify to a single power of $e$.', ans, S(ans), label=f'${lhs} = e^($', post='$)$', level=1, explain=f'${lhs} = e^({D(ans)})$'))
    chains = [('x^2', '2x'), ('sin(x)', 'cos(x)'), ('3x^2 + 1', '6x'), ('cos(x)', '-sin(x)'), ('x^3 - x', '3x^2 - 1'), ('sqrt(x)', '1/(2sqrt(x))'), ('-x^2', '-2x'),
              ('4x + 1', '4'), ('x^2 + 5x', '2x + 5'), ('tan(x)', 'sec(x)^2')]
    for g, gp in chains:
        Q.append(E(d, d.qid('F'), f'$f(x) = e^({D(g, False)})$. Finish the derivative.', gp, sp.diff(S(g), x), label=f"$f'(x) = e^({D(g, False)})·($", post='$)$', level=2,
                   keys=d.keys + ['sqrt(', 'tan(', 'sec('], ranges={'x': [0.2, 1.2]}, explain=f'Multiply by the derivative of the exponent: ${D(gp)}$.'))
    for f, lab, post, ans in [('xe^x', "$f'(x) = x·($", '$) + e^x$', 'e^x'), ('x^2e^x', "$f'(x) = x^2e^x + ($", '$)e^x$', '2x'), ('e^xsin(x)', "$f'(x) = e^x·($", '$) + e^x sin(x)$', 'cos(x)'),
                              ('e^xcos(x)', "$f'(x) = e^x(-sin(x)) + ($", '$)cos(x)$', 'e^x'), ('x^3e^(2x)', "$f'(x) = x^3·($", '$) + 3x^2e^(2x)$', '2e^(2x)'),
                              ('(x + 1)e^x', "$f'(x) = (x + 1)e^x + ($", '$)e^x$', '1')]:
        Q.append(E(d, d.qid('P'), f'Use the product rule on $f(x) = {D(f, False)}$. Fill in the missing piece.', ans, sp.diff(S(ans if ans != '1' else 'x'), x) if False else S(ans),
                   label=lab, post=post, level=2, ranges={'x': [0.2, 1.2]}, explain=f'The missing piece is ${D(ans)}$.'))
    prods = [('x^2', 'e^x'), ('x', 'e^(3x)'), ('e^x', 'sin(x)'), ('e^x', 'cos(x)'), ('x', '2^x')]
    for g, kk in prods:
        gp, kp = sp_app(sp.diff(S(g), x)), {'e^(3x)': '3e^(3x)', '2^x': '2^xln(2)', 'e^x': 'e^x', 'sin(x)': 'cos(x)', 'cos(x)': '-sin(x)'}[kk]
        gp = {'e^x': 'e^x'}.get(g, gp)
        ans = f'({g})({kp}) + ({gp})({kk})'
        Q.append(STEPS(d.qid('W'), f'Use the product rule on $f(x) = {D(g)}·{D(kk)}$.', [
            E(d, None, f'$g = {D(g)}$', gp, sp.diff(S(g), x), label="$g'$ =", ranges={'x': [0.2, 1.2]}, work=f"$g' = {D(gp)}$"),
            E(d, None, f'$k = {D(kk)}$', kp, sp.diff(S(kk), x), label="$k'$ =", ranges={'x': [0.2, 1.2]}, work=f"$k' = {D(kp)}$"),
            E(d, None, "$gk' + g'k$", ans, sp.diff(S(g) * S(kk), x), label="$f'(x)$ =", ranges={'x': [0.2, 1.2]}, work=f"$f'(x) = {D(ans, False)}$"),
        ], level=3, explain=f"$f'(x) = {D(ans, False)}$"))
    quos = [('e^x', 'x'), ('3^x', '3^x + 1'), ('x', 'e^x'), ('e^x', 'e^x + 1'), ('e^(2x)', 'x^2')]
    for g, kk in quos:
        dd = {'e^x': 'e^x', '3^x': '3^xln(3)', '3^x + 1': '3^xln(3)', 'x': '1', 'e^x + 1': 'e^x', 'e^(2x)': '2e^(2x)', 'x^2': '2x'}
        gp, kp = dd[g], dd[kk]
        ans = f'(({kk})({gp}) - ({g})({kp}))/({kk})^2'
        Q.append(STEPS(d.qid('Q'), f'Use the quotient rule on $f(x) = frac{{{D(g, False)}}}{{{D(kk, False)}}}$.', [
            E(d, None, None, gp, sp.diff(S(g), x), label="top: $g'$ =", ranges={'x': [0.2, 1.2]}, work=f"$g' = {D(gp)}$"),
            E(d, None, None, kp, sp.diff(S(kk), x), label="bottom: $k'$ =", ranges={'x': [0.2, 1.2]}, work=f"$k' = {D(kp)}$"),
            E(d, None, 'Low d-high minus high d-low, over low squared.', ans, sp.diff(S(g) / S(kk), x), label="$f'(x)$ =", ranges={'x': [0.2, 1.2]}, work=f"$f'(x) = {D(ans)}$"),
        ], level=3, explain=f"$f'(x) = {D(ans)}$"))
    for f, ans in [('e^(sin(x))', 'e^(sin(x))cos(x)'), ('e^(x^2 + 1)', '2xe^(x^2 + 1)'), ('2^(3x)', '3(2^(3x))ln(2)'), ('e^(3x^2 + 1) + x^2', '6xe^(3x^2 + 1) + 2x'),
                   ('xe^(-x)', 'e^(-x) - xe^(-x)'), ('e^(e^x)', 'e^(e^x)e^x')]:
        Q.append(E(d, d.qid('C'), f'Find the derivative of $f(x) = {D(f, False)}$.', ans, sp.diff(S(f), x), label="$f'(x)$ =", level=3, ranges={'x': [0.1, 0.9]}, explain=f'${D(ans)}$'))
    for f, a0 in [('e^(2x)', 0), ('xe^x', 0), ('e^x + x', 0), ('3e^x', 0)]:
        fe = S(f)
        fp = sp.diff(fe, x)
        line = tidy(f'{num(fp.subs(x, a0))}x + {num(fe.subs(x, a0))}')
        Q.append(STEPS(d.qid('T'), f'Find the tangent line to $y = {D(f, False)}$ at $x = {a0}$.', [
            N(None, '', fe.subs(x, a0), label=f'$f({a0})$ =', work=f'$f({a0}) = {num(fe.subs(x, a0))}$'),
            N(None, '', fp.subs(x, a0), label=f"$f'({a0})$ =", work=f"$f'({a0}) = {num(fp.subs(x, a0))}$"),
            E(d, None, "$y = f'(a)(x - a) + f(a)$", line, fp.subs(x, a0) * x + fe.subs(x, a0), label='$y$ =', work=f'$y = {D(line)}$'),
        ], level=3, explain=f'$y = {D(line)}$'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 8. Logarithms and inverse functions
def deck_log():
    d = Deck('d-log', 'Derivatives of Logarithms and Inverse Functions', 'ln x, log base b, and the slope of an inverse.', 'Derivatives')
    d.keys = ['ln(', 'e^(', 'sin(', 'cos(']
    L = []
    L.append(MC('L1', "$y = ln(x)$ means $e^y = x$. Differentiate both sides: $e^y·y' = 1$, so $y' = frac{1}{e^y}$. Since $e^y = x$, that is", ['$frac{1}{x}$', '$e^x$', '$ln(x)$', '$frac{1}{e}$'],
                hint='Replace $e^y$ with what it equals.', explain="$frac{d}{dx} ln(x) = frac{1}{x}$"))
    L.append(E(d, 'L2', "With the chain rule, $frac{d}{dx} ln(f(x)) = frac{f'(x)}{f(x)}$: the derivative of the inside over the inside. Try $y = ln(x^3 + 2x + 1)$.",
               '(3x^2 + 2)/(x^3 + 2x + 1)', sp.diff(sp.log(x ** 3 + 2 * x + 1), x), label="$y'$ =", hint='Top: the derivative of $x^3 + 2x + 1$. Bottom: $x^3 + 2x + 1$.',
               explain='$frac{3x^2 + 2}{x^3 + 2x + 1}$'))
    L.append(MC('L3', 'Log rules can make a derivative easy **before** you start. Which is the same as $ln(frac{x^2 sin(x)}{2x + 1})$?',
                ['$2ln(x) + ln(sin(x)) - ln(2x + 1)$', '$frac{ln(x^2) ln(sin(x))}{ln(2x + 1)}$', '$2ln(x) · ln(sin(x)) - ln(2x + 1)$', '$ln(x^2) - ln(sin(x)) + ln(2x + 1)$'],
                hint='Products become sums, quotients become differences, powers come out front.', explain="Now each piece is easy: $frac{2}{x} + frac{cos(x)}{sin(x)} - frac{2}{2x + 1}$."))
    L.append(MC('L4', 'Other bases pick up $ln(b)$: $frac{d}{dx} log_b(x) = frac{1}{x ln(b)}$. What is $frac{d}{dx} log_2(x)$?', ['$frac{1}{x ln(2)}$', '$frac{1}{2x}$', '$frac{ln(2)}{x}$', '$frac{2}{x}$'],
                hint='Put $b = 2$ in the formula.', explain='$frac{1}{x ln(2)}$'))
    L.append(STEPS('L5', "**Inverse functions:** $(f^(-1))'(a) = frac{1}{f'(f^(-1)(a))}$. Flip the graph over $y = x$ and slopes flip too. Let $f(x) = x^3 + x$. Find $(f^(-1))'(2)$.", [
        N('L5.1', 'First find $f^(-1)(2)$: which $x$ gives $x^3 + x = 2$?', 1, label='$f^(-1)(2)$ =', hint='Try small whole numbers.', work='$f^(-1)(2) = 1$'),
        N('L5.2', "$f'(x) = 3x^2 + 1$. Evaluate it there.", 4, label="$f'(1)$ =", hint='$3(1)^2 + 1$', work="$f'(1) = 4$"),
        N('L5.3', 'Flip it.', 0.25, label="$(f^(-1))'(2)$ =", hint='One over the slope you just found.', work="$(f^(-1))'(2) = frac{1}{4}$"),
    ]))
    d.lesson(L)

    T = [
        MC('T1', '$frac{d}{dx} ln(x) =$', ['$frac{1}{x}$', '$ln(x)$', '$e^x$', '$frac{1}{ln(x)}$'], explain='One of the most-used derivatives in calculus.'),
        MC('T2', '$frac{d}{dx} ln(g(x)) =$', ["$frac{g'(x)}{g(x)}$", '$frac{1}{g(x)}$', "$frac{1}{g'(x)}$", "$ln(g'(x))$"], explain='Chain rule: $frac{1}{g(x)}·g\'(x)$.'),
        TF('T3', '$frac{d}{dx} ln(2x) = frac{1}{2x}$', False, explain='$frac{2}{2x} = frac{1}{x}$. (Or: $ln(2x) = ln(2) + ln(x)$, and $ln(2)$ is a constant.)'),
        MATCH('T4', 'Match the log rules.', [['$ln(ab)$', '$ln(a) + ln(b)$'], ['$ln(frac{a}{b})$', '$ln(a) - ln(b)$'], ['$ln(a^r)$', '$r ln(a)$'], ['$ln(e)$', '$1$']],
              explain='Use these to simplify before differentiating.'),
        MC('T5', '$frac{d}{dx} log_b(x) =$', ['$frac{1}{x ln(b)}$', '$frac{1}{x}$', '$frac{ln(b)}{x}$', '$b^x ln(b)$'], explain='$log_b(x) = frac{ln(x)}{ln(b)}$, and $ln(b)$ is a constant.'),
        MC('T6', "The inverse function theorem says $(f^(-1))'(a) =$", ["$frac{1}{f'(f^(-1)(a))}$", "$frac{1}{f'(a)}$", "$-f'(a)$", "$f'(f^(-1)(a))$"],
           explain="Find where $f$ takes the value $a$, take the slope of $f$ there, and flip it."),
        MC('T7', 'The graph of $f^(-1)$ is the graph of $f$', ['reflected over the line $y = x$', 'reflected over the $x$-axis', 'shifted up 1', 'turned upside down'],
           explain='Swapping $x$ and $y$ reflects over $y = x$, which turns a slope $m$ into $frac{1}{m}$.'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    basic = [('ln(5x)', '1/x'), ('ln(x^3)', '3/x'), ('4ln(x)', '4/x'), ('log_2(x)', '1/(xln(2))'), ('ln(x) + x^2', '1/x + 2x'), ('ln(x^7)', '7/x'),
             ('log_10(x)', '1/(xln(10))'), ('ln(x/3)', '1/x'), ('x - ln(x)', '1 - 1/x'), ('ln(sqrt(x))', '1/(2x)'), ('ln(e^x)', '1'), ('ln(3) + ln(x)', '1/x'),
             ('5log_3(x)', '5/(xln(3))'), ('ln(x^2) + e^x', '2/x + e^x')]
    for f, ans in basic:
        src = re.sub(r'log_(\d+)\(x\)', r'(ln(x)/ln(\1))', f)
        Q.append(E(d, d.qid('B'), f'Find the derivative of $f(x) = {D(f, False).replace("log_2", "log_2").replace("log_10", "log_10")}$.', ans, sp.diff(S(src), x), label="$f'(x)$ =",
                   level=1, keys=d.keys + ['sqrt('], explain=f'${D(ans)}$'))
    for expr_, n_ in [('ln(x^5)', 5), ('ln(sqrt(x))', sp.Rational(1, 2)), ('ln(frac{1}{x})', -1), ('ln(x^(2/3))', sp.Rational(2, 3)), ('ln(frac{1}{x^4})', -4), ('ln(x sqrt(x))', sp.Rational(3, 2))]:
        Q.append(N(d.qid('R'), f'Use log rules: ${expr_} = n ln(x)$. What is $n$?', n_, label='$n$ =', level=1, explain=f'${expr_} = {frac_str(n_)} ln(x)$'))
    insides = [('x^2 + 1', '2x'), ('sin(x)', 'cos(x)'), ('3x - 2', '3'), ('x^3 + 2x + 1', '3x^2 + 2'), ('cos(x)', '-sin(x)'), ('e^x + 1', 'e^x'), ('x^4 - x', '4x^3 - 1'),
               ('2x^2 + 7', '4x'), ('x + sqrt(x)', '1 + 1/(2sqrt(x))'), ('1 + e^(2x)', '2e^(2x)')]
    for g, gp in insides:
        Q.append(E(d, d.qid('F'), f'$f(x) = ln({D(g, False)})$. Fill in the top of $frac{{g\'(x)}}{{g(x)}}$.', gp, sp.diff(S(g), x), label="$f'(x) = ($",
                   post=f'$) / ({D(g, False)})$', level=2, keys=d.keys + ['sqrt('], ranges={'x': [0.2, 1.2]}, explain=f'The derivative of the inside: ${D(gp)}$.'))
    invs = [('x^3 + x', 2, 1), ('x^3 + x', 10, 2), ('2x + sin(x)', 0, 0), ('x^5 + x', 2, 1), ('e^x + x', 1, 0), ('x^3 + 2x - 1', 2, 1), ('x + ln(x)', 1, 1)]
    for f, a0, xv in invs:
        fe = S(f)
        assert abs(float(fe.subs(x, xv) - a0)) < 1e-12
        Q.append(N(d.qid('I'), f'$f(x) = {D(f)}$. Find $f^(-1)({a0})$: the $x$ with $f(x) = {a0}$.', xv, label=f'$f^(-1)({a0})$ =', level=2,
                   explain=f'$f({xv}) = {a0}$, so $f^(-1)({a0}) = {xv}$.'))
    for f, a0, xv in invs:
        fe = S(f)
        fp = sp.diff(fe, x)
        v = 1 / fp.subs(x, xv)
        Q.append(STEPS(d.qid('V'), f"$f(x) = {D(f)}$. Find $(f^(-1))'({a0})$.", [
            N(None, f'Which $x$ gives $f(x) = {a0}$?', xv, label=f'$f^(-1)({a0})$ =', work=f'$f^(-1)({a0}) = {xv}$'),
            N(None, f"$f'(x) = {D(sp_app(fp))}$", fp.subs(x, xv), label=f"$f'({xv})$ =", work=f"$f'({xv}) = {num(fp.subs(x, xv))}$"),
            N(None, 'Flip it.', v, label=f"$(f^(-1))'({a0})$ =", work=f"$(f^(-1))'({a0}) = {frac_str(v)}$"),
        ], level=3, explain=f"$(f^(-1))'({a0}) = frac{{1}}{{f'({xv})}} = {frac_str(v)}$"))
    for g, gp in insides[:6]:
        ans = f'({gp})/({g})'
        Q.append(STEPS(d.qid('W'), f'Find the derivative of $f(x) = ln({D(g, False)})$.', [
            E(d, None, f'Inside: $g(x) = {D(g, False)}$', gp, sp.diff(S(g), x), label="$g'(x)$ =", ranges={'x': [0.2, 1.2]}, work=f"$g'(x) = {D(gp)}$"),
            E(d, None, "$frac{g'(x)}{g(x)}$", ans, sp.diff(sp.log(S(g)), x), label="$f'(x)$ =", ranges={'x': [0.2, 1.2]}, work=f"$f'(x) = {D(ans)}$"),
        ], level=3, explain=f"$f'(x) = {D(ans)}$"))
    for f, ans in [('xln(x)', 'ln(x) + 1'), ('x^2ln(x)', '2xln(x) + x'), ('ln(x)/x', '(1 - ln(x))/x^2'), ('ln(x^2 + 1)^3', '3ln(x^2 + 1)^2(2x/(x^2 + 1))'), ('ln(ln(x))', '1/(xln(x))')]:
        Q.append(E(d, d.qid('C'), f'Find the derivative of $f(x) = {D(f, False)}$.', ans, sp.diff(S(f), x), label="$f'(x)$ =", level=3, ranges={'x': [1.2, 2.6]}, explain=f'${D(ans)}$'))
    Q.append(STEPS(d.qid('X'), 'Find $frac{dy}{dx}$ for $y = ln(frac{x^2 sin(x)}{2x + 1})$ by expanding first.', [
        MC(None, 'Expand with log rules:', ['$2ln(x) + ln(sin(x)) - ln(2x + 1)$', '$2ln(x)·ln(sin(x)) - ln(2x + 1)$', '$ln(x^2) - ln(sin(x)) - ln(2x + 1)$', '$2ln(x) + ln(sin(x)) + ln(2x + 1)$'],
           work='$y = 2ln(x) + ln(sin(x)) - ln(2x + 1)$'),
        E(d, None, 'Differentiate each piece.', '2/x + cos(x)/sin(x) - 2/(2x + 1)', sp.diff(sp.log(x ** 2 * sp.sin(x) / (2 * x + 1)), x), label="$y'$ =", ranges={'x': [0.3, 1.2]},
          work="$y' = frac{2}{x} + frac{cos(x)}{sin(x)} - frac{2}{2x + 1}$"),
    ], level=3, explain="$frac{2}{x} + cot(x) - frac{2}{2x + 1}$"))
    Q.append(STEPS(d.qid('X'), 'Find the tangent line to $y = log_2(3x + 1)$ at $x = 1$.', [
        N(None, '', 2, label='$y(1)$ =', work='$y(1) = log_2(4) = 2$'),
        E(d, None, '$frac{d}{dx} log_2(g) = frac{g\'}{g ln(2)}$', '3/((3x + 1)ln(2))', sp.diff(sp.log(3 * x + 1) / sp.log(2), x), label="$y'$ =", work="$y' = frac{3}{(3x + 1)ln(2)}$"),
        N(None, 'Slope at $x = 1$ (a decimal is fine).', 3 / (4 * sp.log(2)), label="$y'(1)$ =", tol=0.005, work="$y'(1) = frac{3}{4 ln(2)} ≈ 1.082$"),
    ], level=3, explain='$y = frac{3}{4 ln(2)}(x - 1) + 2$'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 9. Logarithmic differentiation
# (y, ln y, d/dx of ln y, ranges)
LD = [('x^x', 'xln(x)', 'ln(x) + 1', None), ('x^(sin(x))', 'sin(x)ln(x)', 'cos(x)ln(x) + sin(x)/x', None),
      ('(2x^4 + 1)^(sin(x))', 'sin(x)ln(2x^4 + 1)', 'cos(x)ln(2x^4 + 1) + sin(x)(8x^3)/(2x^4 + 1)', None),
      ('x^(sqrt(x))', 'sqrt(x)ln(x)', 'ln(x)/(2sqrt(x)) + sqrt(x)/x', None), ('(x^2 + 2x + 7)^(sqrt(x))', 'sqrt(x)ln(x^2 + 2x + 7)', 'ln(x^2 + 2x + 7)/(2sqrt(x)) + sqrt(x)(2x + 2)/(x^2 + 2x + 7)', None),
      ('(sin(x))^x', 'xln(sin(x))', 'ln(sin(x)) + xcos(x)/sin(x)', {'x': [0.2, 1.4]}), ('(cos(x))^x', 'xln(cos(x))', 'ln(cos(x)) - xsin(x)/cos(x)', {'x': [0.2, 1.2]}),
      ('x^(e^x)', 'e^xln(x)', 'e^xln(x) + e^x/x', None), ('x^(ln(x))', 'ln(x)^2', '2ln(x)/x', None), ('(ln(x))^x', 'xln(ln(x))', 'ln(ln(x)) + 1/ln(x)', {'x': [1.3, 2.8]}),
      ('(x^2 + 1)^x', 'xln(x^2 + 1)', 'ln(x^2 + 1) + 2x^2/(x^2 + 1)', None), ('x^(1/x)', 'ln(x)/x', '(1 - ln(x))/x^2', None),
      ('x^(x^2)', 'x^2ln(x)', '2xln(x) + x', None), ('(3x)^x', 'xln(3x)', 'ln(3x) + 1', None)]
LP = [('frac{(x + 2)^2(3x - 1)^2}{sqrt(x + 1)}', '((x + 2)^2(3x - 1)^2)/sqrt(x + 1)', '2ln(x + 2) + 2ln(3x - 1) - ln(x + 1)/2', '2/(x + 2) + 6/(3x - 1) - 1/(2(x + 1))'),
      ('frac{(x + 1)^(2/3)}{(x + 2)(x + 1)^5}', '(x + 1)^(2/3)/((x + 2)(x + 1)^5)', '(2/3)ln(x + 1) - ln(x + 2) - 5ln(x + 1)', '(2/3)/(x + 1) - 1/(x + 2) - 5/(x + 1)'),
      ('frac{x^3 sqrt(x^2 + 1)}{(x - 1)^4}', 'x^3sqrt(x^2 + 1)/(x - 1)^4', '3ln(x) + ln(x^2 + 1)/2 - 4ln(x - 1)', '3/x + x/(x^2 + 1) - 4/(x - 1)'),
      ('x^2(x + 3)^5(2x - 1)^3', 'x^2(x + 3)^5(2x - 1)^3', '2ln(x) + 5ln(x + 3) + 3ln(2x - 1)', '2/x + 5/(x + 3) + 6/(2x - 1)')]


def deck_logdiff():
    d = Deck('d-logdiff', 'Logarithmic Differentiation', 'Take ln of both sides to tame variable exponents and long products.', 'Derivatives')
    d.keys = ['ln(', 'e^(', 'sin(', 'cos(', 'sqrt(']
    L = []
    L.append(MC('L1', "Find the derivative of $y = x^x$. The power rule needs a constant power, and $b^x$ needs a constant base. Neither works! The trick: take $ln$ of both sides. Since $ln(a^r) = r ln(a)$, $ln(y) =$",
                ['$x ln(x)$', '$ln(x)^x$', '$x^x ln(x)$', '$ln(x)$'], hint='The power $x$ comes out front.', explain='$ln(y) = x ln(x)$. No more variable exponent.'))
    L.append(STEPS('L2', 'Finish $y = x^x$. We have $ln(y) = x ln(x)$.', [
        MC('L2.1', 'Differentiate the left side, $ln(y)$ (remember $y$ depends on $x$):', ["$frac{y'}{y}$", '$frac{1}{y}$', "$frac{1}{y'}$", "$ln(y')$"],
           hint="Chain rule: $frac{1}{y}·y'$.", work="left: $frac{y'}{y}$"),
        E(d, 'L2.2', 'Differentiate the right side, $x ln(x)$ (product rule).', 'ln(x) + 1', sp.log(x) + 1, label='right =', hint='$1·ln(x) + x·frac{1}{x}$',
          work="$frac{y'}{y} = ln(x) + 1$"),
        E(d, 'L2.3', "Multiply both sides by $y = x^x$.", 'x^x(ln(x) + 1)', sp.diff(x ** x, x), label="$y'$ =", hint="$y' = y(ln(x) + 1)$, and $y = x^x$.",
          work="$y' = x^x(ln(x) + 1)$"),
    ]))
    L.append(MC('L3', 'Same trick for $y = (2x^4 + 1)^(sin(x))$. After taking $ln$ of both sides:', ['$ln(y) = sin(x) ln(2x^4 + 1)$', '$ln(y) = ln(sin(x)) ln(2x^4 + 1)$', '$ln(y) = sin(x) + ln(2x^4 + 1)$', '$ln(y) = (2x^4 + 1) ln(sin(x))$'],
                hint='The exponent comes out front.', explain='Then differentiate with the product rule, and multiply by $y$ at the end.'))
    L.append(MC('L4', 'It also tames long products and quotients. For $y = frac{(x + 2)^2(3x - 1)^2}{sqrt(x + 1)}$, $ln(y) =$',
                ['$2ln(x + 2) + 2ln(3x - 1) - frac{1}{2}ln(x + 1)$', '$2ln(x + 2)·2ln(3x - 1) - frac{1}{2}ln(x + 1)$', '$ln(x + 2)^2 + ln(3x - 1)^2 + ln(x + 1)^(1/2)$', '$2(x + 2) + 2(3x - 1) - frac{1}{2}(x + 1)$'],
                hint='Products → sums, quotients → differences, powers → in front.', explain='Each piece is now a simple $ln$ with no product or quotient rule needed.'))
    L.append(ORDER('L5', 'Put the steps of logarithmic differentiation in order.', ['Take $ln$ of both sides', 'Use log rules to bring powers down', "Differentiate both sides (the left becomes $frac{y'}{y}$)", 'Multiply both sides by $y$'],
                   hint='Logs first, derivative next, and multiply by $y$ last.', explain='ln, simplify, differentiate, multiply by $y$.'))
    d.lesson(L)

    T = [
        MC('T1', 'When do you need logarithmic differentiation?', ['When the variable is in both the base and the exponent, like $x^x$', 'For every exponential like $2^x$', 'For every power like $x^5$', 'Only for $ln(x)$'],
           explain='$x^5$ uses the power rule, $2^x$ uses the $b^x$ rule. $x^x$ needs the trick.'),
        MC('T2', 'After taking $ln$ of both sides, the derivative of the left side $ln(y)$ is', ["$frac{y'}{y}$", '$frac{1}{y}$', "$y'$", '$ln(y\')$'], explain="Chain rule: $frac{1}{y}·y'$."),
        TF('T3', '$frac{d}{dx} x^x = x·x^(x-1)$', False, explain='The power rule needs a constant power. The right answer is $x^x(ln(x) + 1)$.'),
        MC('T4', 'The last step of logarithmic differentiation is to', ['multiply by $y$ (the original function)', 'divide by $y$', 'take $e$ to both sides', 'set $y\' = 0$'], explain="You have $frac{y'}{y} = …$, so multiply by $y$."),
        TF('T5', 'Logarithmic differentiation can make a long product or quotient easier to differentiate.', True, explain='Log rules turn it into a sum of simple logs.'),
        MC('T6', 'For $y = x^(sin(x))$, which is $ln(y)$?', ['$sin(x) ln(x)$', '$ln(x) ln(sin(x))$', '$x ln(sin(x))$', '$sin(ln(x))$'], explain='The exponent $sin(x)$ comes out front.'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    for yy, lny, dr, rg in LD:
        Q.append(E(d, d.qid('A'), f'$y = {D(yy, False)}$. Take $ln$ of both sides and bring the power down.', lny, sp.log(S(yy)), label='$ln(y)$ =', level=1, ranges=rg or {'x': [0.3, 1.4]},
                   explain=f'$ln(y) = {D(lny, False)}$'))
    for disp, src, lny, dr in LP:
        Q.append(E(d, d.qid('A'), f'$y = {disp}$. Take $ln$ of both sides and expand with log rules.', lny, sp.expand_log(sp.log(S(src)), force=True), label='$ln(y)$ =', level=1,
                   ranges={'x': [1.2, 2.5]}, explain=f'$ln(y) = {D(lny, False)}$'))
    for yy, lny, dr, rg in LD:
        Q.append(E(d, d.qid('B'), f'$ln(y) = {D(lny, False)}$. Differentiate the right side: $frac{{y\'}}{{y}} =$ ?', dr, sp.diff(S(lny), x), label="$frac{y'}{y}$ =", level=2,
                   ranges=rg or {'x': [0.3, 1.4]}, explain=f"$frac{{y'}}{{y}} = {D(dr, False)}$"))
    for yy, lny, dr, rg in LD[:6]:
        ans = f'{yy}({dr})'
        Q.append(E(d, d.qid('C'), f"$y = {D(yy, False)}$ and $frac{{y'}}{{y}} = {D(dr, False)}$. Multiply by $y$.", ans, sp.diff(S(yy), x), label="$y'$ =", level=2,
                   ranges=rg or {'x': [0.3, 1.4]}, explain=f"$y' = {D(ans, False)}$"))
    for yy, lny, dr, rg in LD:
        ans = f'{yy}({dr})'
        Q.append(STEPS(d.qid('W'), f'Use logarithmic differentiation on $y = {D(yy, False)}$.', [
            E(d, None, 'Take $ln$ of both sides.', lny, sp.log(S(yy)), label='$ln(y)$ =', ranges=rg or {'x': [0.3, 1.4]}, work=f'$ln(y) = {D(lny, False)}$'),
            E(d, None, 'Differentiate the right side.', dr, sp.diff(S(lny), x), label="$frac{y'}{y}$ =", ranges=rg or {'x': [0.3, 1.4]}, work=f"$frac{{y'}}{{y}} = {D(dr, False)}$"),
            E(d, None, 'Multiply by $y$.', ans, sp.diff(S(yy), x), label="$y'$ =", ranges=rg or {'x': [0.3, 1.4]}, work=f"$y' = {D(ans, False)}$"),
        ], level=3, explain=f"$y' = {D(ans, False)}$"))
    for disp, src, lny, dr in LP:
        ans = f'({src})({dr})'
        Q.append(STEPS(d.qid('W'), f'Use logarithmic differentiation on $y = {disp}$.', [
            E(d, None, 'Take $ln$ of both sides and expand.', lny, sp.expand_log(sp.log(S(src)), force=True), label='$ln(y)$ =', ranges={'x': [1.2, 2.5]}, work=f'$ln(y) = {D(lny, False)}$'),
            E(d, None, 'Differentiate the right side.', dr, sp.diff(S(lny), x), label="$frac{y'}{y}$ =", ranges={'x': [1.2, 2.5]}, work=f"$frac{{y'}}{{y}} = {D(dr, False)}$"),
            E(d, None, 'Multiply by $y$. (Type $y$ back out in full.)', ans, sp.diff(S(src), x), label="$y'$ =", ranges={'x': [1.2, 2.5]}, work=f"$y' = y·({D(dr, False)})$"),
        ], level=3, explain=f"$y' = {disp}·({D(dr, False)})$"))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 10. Inverse trig
def deck_invtrig():
    d = Deck('d-invtrig', 'Derivatives of Inverse Trig Functions', 'arcsin, arccos and arctan, from implicit differentiation.', 'Derivatives')
    d.keys = ['sqrt(', 'arcsin(', 'arctan(', 'arccos(']
    SM = {'x': [0.05, 0.45]}
    L = []
    L.append(MC('L1', "$y = arcsin(x)$ (also written $sin^(-1)(x)$) means $sin(y) = x$. Differentiate implicitly: $cos(y)·y' = 1$, so $y' = frac{1}{cos(y)}$. A right triangle with opposite side $x$ and hypotenuse 1 shows $cos(y) = sqrt(1 - x^2)$. So $frac{d}{dx} arcsin(x) =$",
                ['$frac{1}{sqrt(1 - x^2)}$', '$frac{1}{cos(x)}$', '$-frac{1}{sqrt(1 - x^2)}$', '$sqrt(1 - x^2)$'], hint='Put $sqrt(1 - x^2)$ in for $cos(y)$.',
                explain='$frac{d}{dx} arcsin(x) = frac{1}{sqrt(1 - x^2)}$'))
    L.append(MATCH('L2', 'The same trick gives the others. Match each function to its derivative.', [['$arcsin(x)$', '$frac{1}{sqrt(1 - x^2)}$'], ['$arccos(x)$', '$-frac{1}{sqrt(1 - x^2)}$'], ['$arctan(x)$', '$frac{1}{1 + x^2}$']],
                   hint='arccos is the same as arcsin with a minus sign.', explain='These three are the ones to memorize.'))
    L.append(E(d, 'L3', "Chain rule as always: $frac{d}{dx} arctan(g) = frac{g'}{1 + g^2}$. Find the derivative of $f(x) = arctan(x^2)$.", '2x/(1 + x^4)', sp.diff(sp.atan(x ** 2), x),
               label="$f'(x)$ =", hint='$g = x^2$, so $g\' = 2x$ and $g^2 = x^4$.', explain='$frac{2x}{1 + x^4}$'))
    L.append(MC('L4', 'Triangles also simplify things like $sin(arccos(x))$. Let $theta = arccos(x)$: adjacent side $x$, hypotenuse 1. Then the opposite side is $sqrt(1 - x^2)$, so $sin(arccos(x)) =$',
                ['$sqrt(1 - x^2)$', '$x$', '$frac{1}{x}$', '$sqrt(1 + x^2)$'], hint='Sine is opposite over hypotenuse.', explain='$sin(arccos(x)) = sqrt(1 - x^2)$'))
    L.append(E(d, 'L5', 'Old rules still apply. Use the product rule on $f(x) = x arctan(x)$.', 'arctan(x) + x/(1 + x^2)', sp.diff(x * sp.atan(x), x), label="$f'(x)$ =",
               hint="$1·arctan(x) + x·frac{1}{1 + x^2}$", explain='$arctan(x) + frac{x}{1 + x^2}$'))
    d.lesson(L)

    T = [
        MATCH('T1', 'Match each function to its derivative.', [['$arcsin(x)$', '$frac{1}{sqrt(1 - x^2)}$'], ['$arccos(x)$', '$-frac{1}{sqrt(1 - x^2)}$'], ['$arctan(x)$', '$frac{1}{1 + x^2}$']],
              explain='arccos is arcsin with a minus sign.'),
        TF('T2', '$sin^(-1)(x)$ means $frac{1}{sin(x)}$.', False, explain='$sin^(-1)(x)$ is the inverse function $arcsin(x)$. $frac{1}{sin(x)}$ is $csc(x)$.'),
        MC('T3', 'Where does the formula $frac{d}{dx} arcsin(x) = frac{1}{sqrt(1 - x^2)}$ come from?', ['Implicit differentiation of $sin(y) = x$', 'The quotient rule', 'The power rule', 'The limit definition with $h = 0$'],
           explain='Write $sin(y) = x$, differentiate, and use a triangle to write $cos(y)$ in terms of $x$.'),
        MC('T4', '$frac{d}{dx} arctan(g(x)) =$', ["$frac{g'(x)}{1 + g(x)^2}$", "$frac{1}{1 + g'(x)^2}$", '$frac{1}{1 + g(x)^2}$', "$arctan(g'(x))$"], explain='Chain rule.'),
        MC('T5', 'What is $cos(arctan(x))$? (Draw a triangle with opposite $x$ and adjacent 1.)', ['$frac{1}{sqrt(1 + x^2)}$', '$sqrt(1 + x^2)$', '$frac{x}{sqrt(1 + x^2)}$', '$sqrt(1 - x^2)$'],
           explain='The hypotenuse is $sqrt(1 + x^2)$, and cosine is adjacent over hypotenuse.'),
        MC('T6', '$frac{d}{dx} sec^(-1)(x) =$', ['$frac{1}{|x| sqrt(x^2 - 1)}$', '$sec(x)tan(x)$', '$frac{1}{1 + x^2}$', '$-frac{1}{sqrt(1 - x^2)}$'],
           explain='The less common ones: $sec^(-1)$ gives $frac{1}{|x|sqrt(x^2 - 1)}$, and $csc^(-1)$ and $cot^(-1)$ are the negatives of $sec^(-1)$ and $tan^(-1)$.'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    basic = [('3arcsin(x)', '3/sqrt(1 - x^2)'), ('arctan(x) + x^2', '1/(1 + x^2) + 2x'), ('arccos(x)', '-1/sqrt(1 - x^2)'), ('5arctan(x)', '5/(1 + x^2)'),
             ('arcsin(x) + arccos(x)', '0'), ('x - arctan(x)', '1 - 1/(1 + x^2)'), ('2arccos(x)', '-2/sqrt(1 - x^2)'), ('arctan(x) - 4x', '1/(1 + x^2) - 4'),
             ('arcsin(x) + x^3', '1/sqrt(1 - x^2) + 3x^2'), ('-arcsin(x)', '-1/sqrt(1 - x^2)')]
    for f, ans in basic:
        Q.append(E(d, d.qid('B'), f'Find the derivative of {F("f(x)", f)}.', ans, sp.diff(S(f), x), label="$f'(x)$ =", level=1, ranges=SM, explain=f'${D(ans)}$'))
    tri = [('sin(arccos(x))', '$sqrt(1 - x^2)$', ['$x$', '$frac{1}{x}$', '$sqrt(1 + x^2)$']), ('cos(arcsin(x))', '$sqrt(1 - x^2)$', ['$x$', '$frac{1}{sqrt(1 - x^2)}$', '$1 - x$']),
           ('sec(arctan(x))', '$sqrt(1 + x^2)$', ['$frac{1}{sqrt(1 + x^2)}$', '$sqrt(1 - x^2)$', '$1 + x$']), ('cos(arctan(x))', '$frac{1}{sqrt(1 + x^2)}$', ['$sqrt(1 + x^2)$', '$frac{x}{sqrt(1 + x^2)}$', '$x$']),
           ('tan(arcsin(x))', '$frac{x}{sqrt(1 - x^2)}$', ['$sqrt(1 - x^2)$', '$frac{1}{x}$', '$x sqrt(1 - x^2)$']), ('sin(arctan(x))', '$frac{x}{sqrt(1 + x^2)}$', ['$frac{1}{sqrt(1 + x^2)}$', '$x$', '$sqrt(1 + x^2)$'])]
    for e_, r_, w_ in tri:
        Q.append(MC(d.qid('T'), f'Use a right triangle to simplify ${e_}$.', [r_] + w_, level=1, explain=f'${e_} = {r_[1:-1]}$'))
    chain = [('arctan', 'x^2', '2x'), ('arctan', '3x', '3'), ('arcsin', '2x', '2'), ('arctan', 'e^x', 'e^x'), ('arcsin', 'x^2', '2x'), ('arctan', 'sqrt(x)', '1/(2sqrt(x))'),
             ('arccos', '3x', '3'), ('arctan', 'x^3', '3x^2'), ('arcsin', 'x/2', '1/2'), ('arctan', 'ln(x)', '1/x'), ('arcsin', 'sqrt(x)', '1/(2sqrt(x))'), ('arctan', '5x + 1', '5')]
    for fn_, g, gp in chain:
        rg = {'x': [0.6, 1.5]} if g == 'ln(x)' else SM
        if fn_ == 'arctan':
            lab, post = "$f'(x) = ($", f'$) / (1 + ({D(g, False)})^2)$'
        elif fn_ == 'arcsin':
            lab, post = "$f'(x) = ($", f'$) / sqrt(1 - ({D(g, False)})^2)$'
        else:
            lab, post = "$f'(x) = -($", f'$) / sqrt(1 - ({D(g, False)})^2)$'
        Q.append(E(d, d.qid('F'), f'$f(x) = {fn_}({D(g, False)})$. Fill in the derivative of the inside.', gp, sp.diff(S(g), x), label=lab, post=post, level=2,
                   keys=d.keys + ['e^(', 'ln('], ranges=rg, explain=f'The inside is ${D(g, False)}$, and its derivative is ${D(gp)}$.'))
    for fn_, g, gp in chain[:9]:
        rg = SM
        fe = S(f'{fn_}({g})')
        outer = {'arctan': f'1/(1 + ({g})^2)', 'arcsin': f'1/sqrt(1 - ({g})^2)', 'arccos': f'-1/sqrt(1 - ({g})^2)'}[fn_]
        outer = outer.replace('(x)^2', 'x^2').replace('(e^x)^2', 'e^(2x)').replace('(3x)^2', '9x^2').replace('(2x)^2', '4x^2').replace('(x^2)^2', 'x^4').replace('(sqrt(x))^2', 'x').replace('(x^3)^2', 'x^6').replace('(x/2)^2', 'x^2/4')
        ans = f'({gp})({outer})' if gp not in ('2', '3', '1/2') else f'{gp}({outer})' if gp != '1/2' else f'({outer})/2'
        Q.append(STEPS(d.qid('W'), f'Find the derivative of $f(x) = {fn_}({D(g, False)})$.', [
            E(d, None, 'Derivative of the outside, with the inside left alone.', outer, sp.diff(S(f'{fn_}(u)'), u).subs(u, S(g)), label='outside part =', keys=d.keys + ['e^('], ranges=rg,
              work=f'outside: ${D(outer)}$'),
            E(d, None, 'Derivative of the inside.', gp, sp.diff(S(g), x), label="$g'(x)$ =", keys=d.keys + ['e^('], ranges=rg, work=f"inside: ${D(gp)}$"),
            E(d, None, 'Multiply.', ans, sp.diff(fe, x), label="$f'(x)$ =", keys=d.keys + ['e^('], ranges=rg, work=f"$f'(x) = {D(ans, False)}$"),
        ], level=3, explain=f"$f'(x) = {D(ans, False)}$"))
    for f, ans in [('xarcsin(x)', 'arcsin(x) + x/sqrt(1 - x^2)'), ('x^2arctan(x)', '2xarctan(x) + x^2/(1 + x^2)'), ('arctan(x)/x', '(x/(1 + x^2) - arctan(x))/x^2'),
                   ('e^xarctan(x)', 'e^xarctan(x) + e^x/(1 + x^2)'), ('arcsin(x)^2', '2arcsin(x)/sqrt(1 - x^2)'), ('2^(arctan(x))', '2^(arctan(x))ln(2)/(1 + x^2)')]:
        Q.append(E(d, d.qid('C'), f'Find the derivative of $f(x) = {D(f, False)}$.', ans, sp.diff(S(f), x), label="$f'(x)$ =", level=3, keys=d.keys + ['e^(', 'ln('], ranges=SM, explain=f'${D(ans, False)}$'))
    for f, ans in [('arctan(x^2)', '2x/(1 + x^4)'), ('arcsin(3x)', '3/sqrt(1 - 9x^2)'), ('arctan(1/x)', '-1/(1 + x^2)'), ('arccos(x^2)', '-2x/sqrt(1 - x^4)'),
                   ('arctan(2x^3)', '6x^2/(1 + 4x^6)'), ('arctan(e^(2x))', '2e^(2x)/(1 + e^(4x))'), ('arcsin(sqrt(x))', '1/(2sqrt(x)sqrt(1 - x))'), ('arctan(x/3)', '3/(9 + x^2)'),
                   ('arcsin(5x)', '5/sqrt(1 - 25x^2)'), ('arctan(sin(x))', 'cos(x)/(1 + sin(x)^2)')]:
        Q.append(E(d, d.qid('G'), f'Find the derivative of $f(x) = {D(f, False)}$.', ans, sp.diff(S(f), x), label="$f'(x)$ =", level=2 if len(Q) % 2 else 3,
                   keys=d.keys + ['e^(', 'sin(', 'cos('], ranges={'x': [0.05, 0.18]}, explain=f'${D(ans)}$'))
    for f, x0 in [('arctan(x)', 1), ('arcsin(x)', 0), ('arctan(2x)', 0), ('arcsin(x)', 0.5)]:
        v = sp.diff(S(f), x).subs(x, x0)
        Q.append(N(d.qid('S'), f'Find the slope of $y = {f}$ at $x = {x0}$. (A decimal is fine.)', v, label='slope =', tol=0.002, level=3,
                   explain=f'The slope is ${num(v)}$.'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== review side quests
def deck_compose():
    d = Deck('d-compose', 'Compositions of Functions', 'Review: building and taking apart f(g(x)).', 'Derivatives')
    d.keys = ['sin(', 'cos(', 'sqrt(']
    L = [
        MC('L1', '$f(g(x))$ means: work out $g(x)$ first, then put that answer into $f$. If $g(2) = 5$ and $f(5) = 11$, what is $f(g(2))$?', ['11', '5', '2', '16'],
           hint='Inside first: $g(2) = 5$. Then $f(5)$.', explain='$f(g(2)) = f(5) = 11$'),
        E(d, 'L2', 'As a formula: $f(x) = x^2$ and $g(x) = x + 3$. Then $f(g(x)) = f(x + 3)$. Write it out.', '(x + 3)^2', (x + 3) ** 2, label='$f(g(x))$ =',
          hint='Put $(x + 3)$ wherever $f$ has an $x$.', explain='$(x + 3)^2$'),
        MC('L3', 'Order matters! With the same $f$ and $g$, $g(f(x)) =$', ['$x^2 + 3$', '$(x + 3)^2$', '$x^2 + 6x + 9$', '$3x^2$'], hint='Now $f$ goes inside $g$.',
           explain='$g(x^2) = x^2 + 3$, which is different from $f(g(x))$.'),
        MC('L4', 'Going backwards: $h(x) = sqrt(x^2 + 1)$ is $f(g(x))$ with', ['$g(x) = x^2 + 1$ and $f(x) = sqrt(x)$', '$g(x) = sqrt(x)$ and $f(x) = x^2 + 1$', '$g(x) = x^2$ and $f(x) = sqrt(x)$', '$g(x) = x$ and $f(x) = sqrt(x^2 + 1)$'],
           hint='What do you compute first? That is the inside.', explain='Inside: $x^2 + 1$. Outside: the square root.'),
    ]
    d.lesson(L, optional=True)
    Q = []
    fl = [('x^2', 'x + 3'), ('2x + 1', 'x^2'), ('sqrt(x)', 'x + 7'), ('3x - 4', '2x + 5'), ('x^2 + 1', 'x - 2'), ('1/x', 'x + 1'), ('x^3', '2x'), ('5 - x', 'x^2 + 2')]
    for k, (f, g) in enumerate(fl):
        a0 = [2, 1, 2, 3, 4, 1, 1, 0][k]
        gv = S(g).subs(x, a0)
        fv = S(f).subs(x, gv)
        Q.append(STEPS(d.qid('E'), f'$f(x) = {D(f)}$ and $g(x) = {D(g)}$. Find $f(g({a0}))$.', [
            N(None, 'Inside first.', gv, label=f'$g({a0})$ =', work=f'$g({a0}) = {num(gv)}$'),
            N(None, 'Now put that into $f$.', fv, label=f'$f(g({a0}))$ =', work=f'$f(g({a0})) = f({num(gv)}) = {num(fv)}$'),
        ], level=1, explain=f'$f(g({a0})) = {num(fv)}$'))
        Q.append(N(d.qid('V'), f'$f(x) = {D(f)}$ and $g(x) = {D(g)}$. Find $g(f({a0 + 1}))$.', S(g).subs(x, S(f).subs(x, a0 + 1)), label=f'$g(f({a0 + 1}))$ =', level=1,
                   explain=f'$f({a0 + 1}) = {num(S(f).subs(x, a0 + 1))}$, then $g$ of that is ${num(S(g).subs(x, S(f).subs(x, a0 + 1)))}$.'))
    tf_, tg_ = {1: 3, 2: 1, 3: 4, 4: 2}, {1: 2, 2: 4, 3: 1, 4: 3}
    tab = '$x$: 1, 2, 3, 4 · $f(x)$: 3, 1, 4, 2 · $g(x)$: 2, 4, 1, 3'
    for a0 in [1, 2, 3, 4]:
        Q.append(N(d.qid('T'), f'Use the table. {tab}. Find $f(g({a0}))$.', tf_[tg_[a0]], label=f'$f(g({a0}))$ =', level=1, explain=f'$g({a0}) = {tg_[a0]}$, and $f({tg_[a0]}) = {tf_[tg_[a0]]}$.'))
        Q.append(N(d.qid('T'), f'Use the table. {tab}. Find $g(f({a0}))$.', tg_[tf_[a0]], label=f'$g(f({a0}))$ =', level=1, explain=f'$f({a0}) = {tf_[a0]}$, and $g({tf_[a0]}) = {tg_[tf_[a0]]}$.'))
    for f, g in fl:
        fg = sub_u(f.replace('x', 'u'), g)
        Q.append(E(d, d.qid('B'), f'$f(x) = {D(f)}$ and $g(x) = {D(g)}$. Write $f(g(x))$.', fg, S(f).subs(x, S(g)), label='$f(g(x))$ =', level=2, explain=f'${D(fg)}$'))
    for f, g in fl[:6]:
        gf = sub_u(g.replace('x', 'u'), f)
        Q.append(E(d, d.qid('C'), f'$f(x) = {D(f)}$ and $g(x) = {D(g)}$. Write $g(f(x))$.', gf, S(g).subs(x, S(f)), label='$g(f(x))$ =', level=2, explain=f'${D(gf)}$'))
    for o, g, disp in COMPS[:16]:
        Q.append(E(d, d.qid('I'), f'$h(x) = {disp} = f(g(x))$. What is the inside function $g(x)$?', g, S(g), label='$g(x)$ =', level=3, ranges={'x': [0.3, 1.2]},
                   explain=f'Inside: ${D(g)}$. Outside: ${D(o.replace("u", "x"))}$.'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


def deck_trigrev():
    d = Deck('d-trigrev', 'Trigonometry Review', 'Review: unit circle values and identities.', 'Derivatives')
    d.keys = ['sqrt(', 'pi']
    L = [
        MC('L1', 'On the unit circle, the point at angle $theta$ is $(cos(theta), sin(theta))$. At $theta = frac{pi}{2}$ (straight up), what is $sin(frac{pi}{2})$?', ['1', '0', '−1', '$frac{1}{2}$'],
           hint='Straight up is the point $(0, 1)$.', explain='$(cos, sin) = (0, 1)$, so $sin(frac{pi}{2}) = 1$.'),
        MC('L2', 'The special angles: $sin(frac{pi}{6}) = frac{1}{2}$, $sin(frac{pi}{4}) = frac{sqrt(2)}{2}$, $sin(frac{pi}{3}) = frac{sqrt(3)}{2}$. Cosine runs the same list backwards. What is $cos(frac{pi}{3})$?',
           ['$frac{1}{2}$', '$frac{sqrt(3)}{2}$', '$frac{sqrt(2)}{2}$', '1'], hint='$frac{pi}{3}$ is the last in the list, so cosine takes the first value.', explain='$cos(frac{pi}{3}) = frac{1}{2}$'),
        MC('L3', 'The most important identity: $sin^2(theta) + cos^2(theta) =$', ['1', '0', '$tan^2(theta)$', '2'], hint='The point is on a circle of radius 1.', explain='Pythagoras on the unit circle.'),
        N('L4', 'Radians: $pi$ radians = 180°. How many degrees is $frac{pi}{4}$?', 45, label='degrees =', hint='$frac{180}{4}$', explain='45°'),
    ]
    d.lesson(L, optional=True)
    Q = []
    vals = {('sin', 0): '0', ('sin', 'pi/6'): '1/2', ('sin', 'pi/4'): 'sqrt(2)/2', ('sin', 'pi/3'): 'sqrt(3)/2', ('sin', 'pi/2'): '1', ('sin', 'pi'): '0',
            ('cos', 0): '1', ('cos', 'pi/6'): 'sqrt(3)/2', ('cos', 'pi/4'): 'sqrt(2)/2', ('cos', 'pi/3'): '1/2', ('cos', 'pi/2'): '0', ('cos', 'pi'): '-1',
            ('tan', 0): '0', ('tan', 'pi/4'): '1', ('tan', 'pi/3'): 'sqrt(3)', ('tan', 'pi/6'): 'sqrt(3)/3', ('sin', '3pi/2'): '-1', ('cos', '2pi'): '1',
            ('sin', '5pi/6'): '1/2', ('cos', '2pi/3'): '-1/2', ('sin', '7pi/6'): '-1/2', ('cos', '3pi/4'): '-sqrt(2)/2'}
    for (fn_, ang), val in vals.items():
        lv = 1 if str(ang) in ('0', 'pi/2', 'pi', 'pi/6', 'pi/4', 'pi/3') else 2
        Q.append(E(d, d.qid('V'), f'Find the exact value of ${fn_}({D(str(ang))})$.', val, S(f'{fn_}({ang})'), [], label=f'${fn_}({D(str(ang))})$ =', level=lv,
                   explain=f'${fn_}({D(str(ang))}) = {D(val)}$'))
    for deg in [30, 45, 60, 90, 120, 135, 180, 270, 360, 150]:
        r = sp.Rational(deg, 180)
        ans = ('pi' if r == 1 else f'{r.p}pi' if r.q == 1 else (f'pi/{r.q}' if r.p == 1 else f'{r.p}pi/{r.q}'))
        Q.append(E(d, d.qid('R'), f'Write ${deg}°$ in radians.', ans, r * sp.pi, [], label='radians =', level=1, explain=f'${deg}° = {deg}·frac{{pi}}{{180}} = {D(ans)}$'))
    ids = [('$sin^2(x) + cos^2(x)$', '$1$', ['$0$', '$2$', '$tan^2(x)$']), ('$tan(x)$', '$frac{sin(x)}{cos(x)}$', ['$frac{cos(x)}{sin(x)}$', '$sin(x)cos(x)$', '$frac{1}{cos(x)}$']),
           ('$sec(x)$', '$frac{1}{cos(x)}$', ['$frac{1}{sin(x)}$', '$frac{sin(x)}{cos(x)}$', '$cos(x)$']), ('$csc(x)$', '$frac{1}{sin(x)}$', ['$frac{1}{cos(x)}$', '$frac{cos(x)}{sin(x)}$', '$sin(x)$']),
           ('$cot(x)$', '$frac{cos(x)}{sin(x)}$', ['$frac{sin(x)}{cos(x)}$', '$frac{1}{cos(x)}$', '$cos(x)sin(x)$']), ('$1 + tan^2(x)$', '$sec^2(x)$', ['$csc^2(x)$', '$1$', '$cot^2(x)$']),
           ('$sin(2x)$', '$2sin(x)cos(x)$', ['$2sin(x)$', '$sin^2(x)$', '$sin(x)cos(x)$']), ('$cos^2(x) - sin^2(x)$', '$cos(2x)$', ['$1$', '$sin(2x)$', '$0$']),
           ('$sin(-x)$', '$-sin(x)$', ['$sin(x)$', '$cos(x)$', '$-cos(x)$']), ('$cos(-x)$', '$cos(x)$', ['$-cos(x)$', '$sin(x)$', '$-sin(x)$'])]
    for lhs, rhs, wr in ids:
        Q.append(MC(d.qid('I'), f'Which is equal to {lhs}?', [rhs] + wr, level=2, explain=f'{lhs} $=$ {rhs[1:-1] and rhs}'))
    sols = [('$sin(t) = frac{1}{2}$', '$frac{pi}{6}$ and $frac{5pi}{6}$', ['$frac{pi}{3}$ and $frac{2pi}{3}$', '$frac{pi}{6}$ only', '$frac{pi}{6}$ and $frac{7pi}{6}$']),
            ('$cos(t) = frac{1}{2}$', '$frac{pi}{3}$ and $frac{5pi}{3}$', ['$frac{pi}{6}$ and $frac{11pi}{6}$', '$frac{pi}{3}$ and $frac{2pi}{3}$', '$frac{pi}{3}$ only']),
            ('$sin(t) = 0$', '$0$, $pi$ and $2pi$', ['$frac{pi}{2}$ and $frac{3pi}{2}$', '$0$ only', '$pi$ only']),
            ('$cos(t) = 0$', '$frac{pi}{2}$ and $frac{3pi}{2}$', ['$0$ and $pi$', '$frac{pi}{2}$ only', '$pi$ and $2pi$']),
            ('$tan(t) = 1$', '$frac{pi}{4}$ and $frac{5pi}{4}$', ['$frac{pi}{4}$ and $frac{3pi}{4}$', '$frac{pi}{4}$ only', '$frac{pi}{2}$']),
            ('$sin(t) = -1$', '$frac{3pi}{2}$', ['$frac{pi}{2}$', '$pi$', '$0$ and $pi$'])]
    for eq, r_, wr in sols:
        Q.append(MC(d.qid('S'), f'Solve {eq} for $0 <= t <= 2pi$.', [r_] + wr, level=3, explain=f'{r_}'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


def deck_solvey():
    d = Deck('d-solvey', 'Algebra: Solving for y', "Review: get y (or y') alone.", 'Derivatives')
    d.keys = ["y'"]
    L = [
        MC('L1', 'To solve for $y$, undo what is done to it. In $3x + 2y = 6$, first subtract $3x$ from both sides:', ['$2y = 6 - 3x$', '$2y = 6 + 3x$', '$y = 6 - 3x$', '$3x = 6 - 2y$'],
           hint='Move the $3x$ to the other side.', explain='Then divide by 2: $y = frac{6 - 3x}{2}$.'),
        MC('L2', 'When $y$ is in **two** terms, factor it out: $xy + 2y = 5$ becomes', ['$y(x + 2) = 5$', '$y = 5 - xy - 2$', '$2xy = 5$', '$y(x + 2y) = 5$'],
           hint='Both terms on the left have a $y$.', explain='Then divide: $y = frac{5}{x + 2}$.'),
        E(d, 'L3', "The same move finishes implicit differentiation. Solve $xy' + y' = 3$ for $y'$.", '3/(x + 1)', 3 / (x + 1), label="$y'$ =", hint="Factor: $y'(x + 1) = 3$.",
          explain="$y' = frac{3}{x + 1}$"),
    ]
    d.lesson(L, optional=True)
    Q = []
    lin = [('3x + 2y = 6', '(6 - 3x)/2'), ('y - 4x = 1', '4x + 1'), ('2y + x = 8', '(8 - x)/2'), ('5x - y = 3', '5x - 3'), ('4y = 3x - 12', '(3x - 12)/4'),
           ('x + 3y = 9', '(9 - x)/3'), ('6x + 2y = 10', '5 - 3x'), ('y/2 + x = 4', '8 - 2x'), ('3(y - 1) = x', 'x/3 + 1'), ('2x - 5y = 10', '(2x - 10)/5')]
    for eq, ans in lin:
        l_, r_ = eq.split(' = ')
        sol = sp.solve(sp.Eq(S(l_), S(r_)), y)[0]
        Q.append(E(d, d.qid('A'), f'Solve for $y$: ${eq}$', ans, sol, label='$y$ =', level=1, explain=f'$y = {D(ans)}$'))
    fac = [('xy + 2y = 5', '5/(x + 2)'), ('xy - y = 4', '4/(x - 1)'), ('3y + x^2y = 7', '7/(3 + x^2)'), ('xy = 2x + 3y', '2x/(x - 3)'), ('y + xy = x', 'x/(1 + x)'),
           ('2y - xy = 1', '1/(2 - x)'), ('x^2y + y = 1', '1/(x^2 + 1)'), ('xy + 5 = 3y', '5/(3 - x)'), ('y(x + 4) = 2x', '2x/(x + 4)'), ('y/x = 3 + y', '3x/(1 - x)')]
    for eq, ans in fac:
        l_, r_ = eq.split(' = ')
        sol = sp.solve(sp.Eq(S(l_), S(r_)), y)[0]
        Q.append(E(d, d.qid('F'), f'Solve for $y$: ${eq}$', ans, sol, label='$y$ =', level=2, ranges={'x': [4.2, 6.5]}, explain=f'Factor out $y$: $y = {D(ans)}$'))
    yp_ = [("2x + 2yy' = 0", '-x/y'), ("xy' + y = 0", '-y/x'), ("3y^2y' = 2x", '2x/(3y^2)'), ("y' + xy' = 4", '4/(1 + x)'), ("2yy' - 3 = x", '(x + 3)/(2y)'),
           ("x^2y' + 2xy = 0", '-2y/x'), ("y'cos(y) + 1 = 2x", '(2x - 1)/cos(y)'), ("4y' - xy' = y", 'y/(4 - x)'), ("y'(x + y) = x", 'x/(x + y)'), ("6x + 4yy' = 2", '(2 - 6x)/(4y)'),
           ("xy' + y' = 1 - y", '(1 - y)/(x + 1)'), ("5y^4y' + y' = 3x^2", '3x^2/(5y^4 + 1)')]
    for eq, ans in yp_:
        l_, r_ = eq.split(' = ')
        sol = sp.solve(sp.Eq(S(l_), S(r_)), yp)[0]
        Q.append(E(d, d.qid('P'), f"Solve for $y'$: ${eq}$", ans, sol, ['x', 'y'], label="$y'$ =", level=3, keys=['cos('], ranges={'x': [0.3, 1.2], 'y': [0.3, 1.2]},
                   explain=f"$y' = {D(ans)}$"))
    for eq, ans in [('x^2 + y^2 = 9', 'sqrt(9 - x^2)'), ('y^2 - x = 4', 'sqrt(x + 4)'), ('x = y^3', 'x^(1/3)'), ('e^y = x', 'ln(x)'), ('ln(y) = 2x', 'e^(2x)'), ('y^2 = 4x', '2sqrt(x)')]:
        l_, r_ = eq.split(' = ')
        sols = [s_ for s_ in sp.solve(sp.Eq(S(l_), S(r_)), y) if s_.subs(x, 1.5).is_positive]
        Q.append(E(d, d.qid('R'), f'Solve for $y$ (take $y > 0$): ${eq}$', ans, sols[0], label='$y$ =', level=2, keys=['sqrt(', 'ln(', 'e^('], ranges={'x': [0.5, 2.5]},
                   explain=f'$y = {D(ans)}$'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


def deck_invfun():
    d = Deck('d-invfun', 'Inverse Functions', 'Review: what an inverse function is and how to find one.', 'Derivatives')
    d.keys = ['sqrt(', 'ln(', 'e^(']
    L = [
        MC('L1', 'An inverse function undoes $f$: if $f(2) = 7$, then $f^(-1)(7) =$', ['2', '7', '$frac{1}{7}$', '−2'], hint='$f$ sends 2 to 7. The inverse sends 7 back.', explain='$f^(-1)(7) = 2$'),
        E(d, 'L2', 'To find a formula: write $y = f(x)$, swap $x$ and $y$, and solve for $y$. Find $f^(-1)(x)$ for $f(x) = 2x + 3$.', '(x - 3)/2', (x - 3) / 2, label='$f^(-1)(x)$ =',
          hint='Swap: $x = 2y + 3$. Then solve for $y$.', explain='$frac{x - 3}{2}$'),
        MC('L3', 'The graph of $f^(-1)$ is the graph of $f$ reflected over', ['the line $y = x$', 'the $x$-axis', 'the $y$-axis', 'the origin'], hint='Swapping $x$ and $y$ swaps the axes.',
           explain='Every point $(a, b)$ on $f$ becomes $(b, a)$ on $f^(-1)$.'),
    ]
    d.lesson(L, optional=True)
    Q = []
    invs = [('2x + 3', '(x - 3)/2'), ('5x - 1', '(x + 1)/5'), ('x/4 + 2', '4(x - 2)'), ('x^3', 'x^(1/3)'), ('x^3 + 1', '(x - 1)^(1/3)'), ('sqrt(x - 2)', 'x^2 + 2'),
            ('e^x', 'ln(x)'), ('ln(x)', 'e^x'), ('1/x', '1/x'), ('3 - x', '3 - x'), ('e^(2x)', 'ln(x)/2'), ('2/(x - 1)', '2/x + 1'), ('7x', 'x/7'), ('(x + 5)/3', '3x - 5')]
    for f, ans in invs:
        lv = 1 if f in ('2x + 3', '5x - 1', '7x', '3 - x', '(x + 5)/3') else 2
        Q.append(E(d, d.qid('F'), f'Find $f^(-1)(x)$ for $f(x) = {D(f)}$.', ans, S(ans), label='$f^(-1)(x)$ =', level=lv, ranges={'x': [2.2, 3.4]},
                   explain=f'Swap $x$ and $y$ in $y = {D(f)}$ and solve: $f^(-1)(x) = {D(ans)}$.'))
    pts = [(2, 7), (0, 4), (-1, 3), (5, 1), (3, -2), (10, 0)]
    for a0, b0 in pts:
        Q.append(N(d.qid('P'), f'$f({a0}) = {b0}$. What is $f^(-1)({b0})$?', a0, label=f'$f^(-1)({b0})$ =', level=1, explain=f'The inverse sends ${b0}$ back to ${a0}$.'))
        opts = list(dict.fromkeys([f'$({b0}, {a0})$', f'$({a0}, {b0})$', f'$({-b0}, {-a0})$', f'$({a0}, {-b0})$', f'$({-a0}, {b0})$', f'$({b0 + 1}, {a0})$']))[:4]
        Q.append(MC(d.qid('G'), f'The point $({a0}, {b0})$ is on the graph of $f$. Which point is on the graph of $f^(-1)$?', opts,
                    level=2, explain='Swap the coordinates.'))
    for f, a0 in [('x^3 + x', 2), ('2x + 1', 9), ('x^5 + 2', 3), ('e^x + x', 1), ('x^3 + 2x', 3)]:
        xv = [v for v in range(-5, 6) if S(f).subs(x, v) == a0][0]
        Q.append(N(d.qid('V'), f'$f(x) = {D(f)}$. Find $f^(-1)({a0})$ by guessing a whole number.', xv, label=f'$f^(-1)({a0})$ =', level=3, explain=f'$f({xv}) = {a0}$'))
    for q_, r_, w_ in [('Which function has an inverse function on all real numbers?', '$f(x) = x^3$', ['$f(x) = x^2$', '$f(x) = |x|$', '$f(x) = cos(x)$']),
                       ('$f(f^(-1)(x))$ is always', '$x$', ['$1$', '$f(x)^2$', '$0$']),
                       ('A function has an inverse function when it passes the', 'horizontal line test', ['vertical line test', 'slope test', 'zero test']),
                       ('The domain of $f^(-1)$ is', 'the range of $f$', ['the domain of $f$', 'all real numbers', 'the $x$-intercepts of $f$']),
                       ('Is $f^(-1)(x)$ the same as $frac{1}{f(x)}$?', 'No', ['Yes', 'Only for lines', 'Only when $x > 0$'])]:
        Q.append(MC(d.qid('T'), q_, [r_] + w_, level=2, explain=r_))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


def deck_invtrigrev():
    d = Deck('d-invtrigrev', 'Inverse Trig Functions', 'Review: arcsin, arccos, arctan and their ranges.', 'Derivatives')
    d.keys = ['sqrt(', 'pi']
    L = [
        MC('L1', '$arcsin(x)$ asks: which angle has sine equal to $x$? Only angles from $-frac{pi}{2}$ to $frac{pi}{2}$ count. What is $arcsin(frac{1}{2})$?', ['$frac{pi}{6}$', '$frac{5pi}{6}$', '$frac{pi}{3}$', '$frac{1}{2}$'],
           hint='$sin(frac{pi}{6}) = frac{1}{2}$.', explain='$frac{5pi}{6}$ also has sine $frac{1}{2}$, but it is outside the range of arcsin.'),
        MATCH('L2', 'Each inverse trig function returns angles in its own range. Match them.', [['$arcsin(x)$', '$[-frac{pi}{2}, frac{pi}{2}]$'], ['$arccos(x)$', '$[0, pi]$'], ['$arctan(x)$', '$(-frac{pi}{2}, frac{pi}{2})$']],
              hint='arccos is the odd one out: it starts at 0.', explain='These ranges make each one a true function.'),
    ]
    d.lesson(L, optional=True)
    Q = []
    vals = [('arcsin', '1/2', 'pi/6'), ('arcsin', '1', 'pi/2'), ('arcsin', '0', '0'), ('arcsin', 'sqrt(2)/2', 'pi/4'), ('arcsin', 'sqrt(3)/2', 'pi/3'), ('arcsin', '-1/2', '-pi/6'),
            ('arccos', '1/2', 'pi/3'), ('arccos', '0', 'pi/2'), ('arccos', '1', '0'), ('arccos', '-1', 'pi'), ('arccos', 'sqrt(3)/2', 'pi/6'), ('arccos', '-1/2', '2pi/3'),
            ('arctan', '1', 'pi/4'), ('arctan', '0', '0'), ('arctan', 'sqrt(3)', 'pi/3'), ('arctan', '-1', '-pi/4'), ('arctan', 'sqrt(3)/3', 'pi/6'), ('arcsin', '-1', '-pi/2')]
    for fn_, arg, ans in vals:
        lv = 2 if arg.startswith('-') or fn_ == 'arccos' and arg in ('-1', '-1/2') else 1
        Q.append(E(d, d.qid('V'), f'Find the exact value of ${fn_}({D(arg)})$.', ans, S(f'{fn_}({arg})'), [], label=f'${fn_}({D(arg)})$ =', level=lv, explain=f'${fn_}({D(arg)}) = {D(ans)}$'))
    tri = [('sin(arccos(x))', '$sqrt(1 - x^2)$', ['$x$', '$frac{1}{x}$', '$sqrt(1 + x^2)$']), ('cos(arcsin(x))', '$sqrt(1 - x^2)$', ['$x$', '$frac{1}{sqrt(1 - x^2)}$', '$1 - x$']),
           ('sec(arctan(x))', '$sqrt(1 + x^2)$', ['$frac{1}{sqrt(1 + x^2)}$', '$sqrt(1 - x^2)$', '$1 + x$']), ('cos(arctan(x))', '$frac{1}{sqrt(1 + x^2)}$', ['$sqrt(1 + x^2)$', '$frac{x}{sqrt(1 + x^2)}$', '$x$']),
           ('tan(arcsin(x))', '$frac{x}{sqrt(1 - x^2)}$', ['$sqrt(1 - x^2)$', '$frac{1}{x}$', '$x sqrt(1 - x^2)$']), ('sin(arctan(x))', '$frac{x}{sqrt(1 + x^2)}$', ['$frac{1}{sqrt(1 + x^2)}$', '$x$', '$sqrt(1 + x^2)$'])]
    for e_, r_, w_ in tri:
        Q.append(MC(d.qid('T'), f'Draw a right triangle to simplify ${e_}$.', [r_] + w_, level=3, explain=f'${e_} = {r_[1:-1]}$'))
    for q_, r_, w_ in [('The range of $arcsin(x)$ is', '$[-frac{pi}{2}, frac{pi}{2}]$', ['$[0, pi]$', '$[-1, 1]$', '$(-infty, infty)$']),
                       ('The range of $arccos(x)$ is', '$[0, pi]$', ['$[-frac{pi}{2}, frac{pi}{2}]$', '$[-1, 1]$', '$[0, 2pi]$']),
                       ('The domain of $arcsin(x)$ is', '$[-1, 1]$', ['$[-frac{pi}{2}, frac{pi}{2}]$', 'all real numbers', '$[0, pi]$']),
                       ('The domain of $arctan(x)$ is', 'all real numbers', ['$[-1, 1]$', '$(-frac{pi}{2}, frac{pi}{2})$', '$[0, pi]$']),
                       ('$sin^(-1)(x)$ means', '$arcsin(x)$', ['$frac{1}{sin(x)}$', '$-sin(x)$', '$sin(-x)$']),
                       ('$arcsin(sin(frac{5pi}{6}))$ equals', '$frac{pi}{6}$', ['$frac{5pi}{6}$', '$frac{1}{2}$', '$-frac{pi}{6}$'])]:
        Q.append(MC(d.qid('R'), q_, [r_] + w_, level=2, explain=r_))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


def deck_hyper():
    d = Deck('d-hyper', 'Hyperbolic Trig', 'Optional: sinh, cosh and their derivatives.', 'Derivatives')
    d.keys = ['sinh(', 'cosh(', 'tanh(', 'e^(']
    L = [
        MC('L1', 'The **hyperbolic** functions are built from $e^x$: $sinh(x) = frac{e^x - e^(-x)}{2}$ and $cosh(x) = frac{e^x + e^(-x)}{2}$. What is $cosh(0)$?', ['1', '0', '$e$', '2'],
           hint='$e^0 = 1$.', explain='$frac{1 + 1}{2} = 1$. A hanging chain makes the shape of $cosh$!'),
        E(d, 'L2', 'Differentiate $sinh(x) = frac{e^x - e^(-x)}{2}$ term by term. What do you get?', 'cosh(x)', sp.cosh(x), label="$frac{d}{dx} sinh(x)$ =", keys=d.keys,
          hint='$frac{e^x + e^(-x)}{2}$. Which function is that?', explain='$frac{d}{dx} sinh(x) = cosh(x)$, and $frac{d}{dx} cosh(x) = sinh(x)$ with no minus sign!'),
        MC('L3', 'Like $sin^2 + cos^2 = 1$, there is an identity: $cosh^2(x) - sinh^2(x) =$', ['1', '0', '−1', '$e^(2x)$'], hint='Try $x = 0$.', explain='$cosh^2(x) - sinh^2(x) = 1$. That is why they are called hyperbolic.'),
    ]
    d.lesson(L)
    T = [
        MATCH('T1', 'Match each function to its derivative.', [['$sinh(x)$', '$cosh(x)$'], ['$cosh(x)$', '$sinh(x)$'], ['$tanh(x)$', '$sech^2(x)$']], explain='No minus sign on the derivative of cosh.'),
        TF('T2', '$frac{d}{dx} cosh(x) = -sinh(x)$', False, explain='Unlike cosine, there is no minus sign: $frac{d}{dx} cosh(x) = sinh(x)$.'),
        MC('T3', '$sinh(x) =$', ['$frac{e^x - e^(-x)}{2}$', '$frac{e^x + e^(-x)}{2}$', '$e^x - e^(-x)$', '$frac{e^x}{2}$'], explain='And cosh has the plus sign.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for f, ans in [('sinh(3x)', '3cosh(3x)'), ('cosh(x^2)', '2xsinh(x^2)'), ('5sinh(x)', '5cosh(x)'), ('cosh(2x)', '2sinh(2x)'), ('xsinh(x)', 'sinh(x) + xcosh(x)'),
                   ('sinh(x)cosh(x)', 'cosh(x)^2 + sinh(x)^2'), ('cosh(x)^2', '2cosh(x)sinh(x)'), ('sinh(e^x)', 'e^xcosh(e^x)'), ('tanh(x)', '1/cosh(x)^2'), ('ln(cosh(x))', 'sinh(x)/cosh(x)'),
                   ('sinh(x) + cosh(x)', 'cosh(x) + sinh(x)'), ('e^xcosh(x)', 'e^xcosh(x) + e^xsinh(x)'), ('cosh(4x + 1)', '4sinh(4x + 1)'), ('sinh(sqrt(x))', 'cosh(sqrt(x))/(2sqrt(x))')]:
        Q.append(E(d, d.qid('D'), f'Find the derivative of $f(x) = {D(f, False)}$.', ans, sp.diff(S(f), x), label="$f'(x)$ =", level=2, keys=d.keys + ['ln(', 'sqrt('], explain=f'${D(ans)}$'))
    for f, v in [('sinh(0)', 0), ('cosh(0)', 1), ('tanh(0)', 0), ('cosh(ln(2))', sp.Rational(5, 4)), ('sinh(ln(3))', sp.Rational(4, 3))]:
        Q.append(N(d.qid('V'), f'Find ${f}$.', v, label=f'${f}$ =', level=1, explain=f'Use the definition with $e^x$: ${frac_str(v)}$.'))
    d.drill('practice', 'Practice', Q, 'pool', setSize=10)
    d.save()


# ====================================================================== chapter review
def deck_review2():
    import json, copy, os
    d = Deck('review2', 'Chapter Review: Derivatives', 'Mixed practice from every stop, and a practice test.', 'Derivatives')
    tool = []
    cases = [('$(x^2 + 1)(3x - 5)$', 'Product rule'), ('$frac{sin(x)}{x^2 + 1}$', 'Quotient rule'), ('$(3x^2 + 1)^10$', 'Chain rule'), ('$x^x$', 'Logarithmic differentiation'),
             ('$x^2 + y^2 = 25$', 'Implicit differentiation'), ('$x^3 sin(x)$', 'Product rule'), ('$sin(x^2)$', 'Chain rule'), ('$frac{e^x}{x}$', 'Quotient rule'),
             ('$x^5 - 3x^2 + 7$', 'Power rule (term by term)'), ('$(sin(x))^x$', 'Logarithmic differentiation'), ('$xy + y^3 = 4$', 'Implicit differentiation'),
             ('$e^(x^2)$', 'Chain rule'), ('$x e^x$', 'Product rule'), ('$sqrt(1 - x^2)$', 'Chain rule'), ('$frac{3}{x^4}$', 'Power rule (term by term)'),
             ('$ln(x^2 + 1)$', 'Chain rule'), ('$x^(sin(x))$', 'Logarithmic differentiation'), ('$frac{x^2}{e^x + 1}$', 'Quotient rule'), ('$sin(y) = x^2$', 'Implicit differentiation'),
             ('$arctan(3x)$', 'Chain rule'), ('$x^2 arctan(x)$', 'Product rule'), ('$4x^3 + 2sqrt(x)$', 'Power rule (term by term)'), ('$tan(x)ln(x)$', 'Product rule'),
             ('$frac{ln(x)}{x}$', 'Quotient rule'), ('$(x^2 + 1)^x$', 'Logarithmic differentiation'), ('$cos(e^x)$', 'Chain rule'), ('$x^3 + y^3 = 3xy$', 'Implicit differentiation'),
             ('$7x - frac{1}{x}$', 'Power rule (term by term)')]
    opts = ['Power rule (term by term)', 'Product rule', 'Quotient rule', 'Chain rule', 'Implicit differentiation', 'Logarithmic differentiation']
    for k, (f, r) in enumerate(cases):
        o = [r] + [w for w in opts if w != r]
        R.shuffle(o)
        o = [r] + [w for w in o if w != r][:3]
        tool.append(MC(f'W{k + 1}', f'What is the **first** tool you need to differentiate {f}?', o, level=1 + (k % 3 == 2), topic='Which rule?',
                       explain=f'{r}.' + (' (After that, you may need other rules inside it.)' if r in ('Product rule', 'Quotient rule') else '')))
    d.drill('tool', 'Which rule?', tool, 'pool', setSize=12)
    topics = {'d-defn': 'Definition', 'd-func': 'Derivative function', 'd-rules': 'Derivative rules', 'd-trig': 'Trig derivatives', 'd-chain': 'Chain rule',
              'd-implicit': 'Implicit differentiation', 'd-exp': 'Exponentials', 'd-log': 'Logs and inverses', 'd-logdiff': 'Log. differentiation', 'd-invtrig': 'Inverse trig'}
    ex = []
    rr = random.Random(7)
    for did, top in topics.items():
        src = json.load(open(os.path.join(ROOT, 'decks', did + '.json')))
        qs = [q for q in src['drills']['practice']['questions'] if q.get('level', 1) >= 2]
        rr.shuffle(qs)
        for q in qs[:7]:
            q = copy.deepcopy(q)
            q['id'] = did[2:].upper()[:3] + q['id']
            if q['type'] == 'steps':
                for st in q['steps']:
                    st['id'] = did[2:].upper()[:3] + st['id']
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
    deck_defn()
    deck_func()
    deck_rules()
    deck_trig()
    deck_chain()
    deck_implicit()
    deck_exp()
    deck_log()
    deck_logdiff()
    deck_invtrig()
    deck_compose()
    deck_trigrev()
    deck_solvey()
    deck_invfun()
    deck_invtrigrev()
    deck_hyper()
    deck_review2()
    write_manifest('world2')
