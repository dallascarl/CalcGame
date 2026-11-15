"""World 0 (The Toolkit), part C: class days 5 and 6, and the Readiness Check.
   t-inverse Inverse Functions      t-explog Exponentials and Logs
   t-circle  The Unit Circle        t-trig   Trig Identities and Equations
   t-ready   Readiness Check (built from the other twelve decks; run it last)"""
import random, re, json, os
import sympy as sp
from lib import *
from world0a import UNIT, disp, Dsum, save_graphs

TH = sp.Symbol('theta')


# ====================================================================== 9. Inverse Functions
def deck_inverse():
    d = Deck('t-inverse', 'Inverse Functions', 'What an inverse undoes, how to find one, and what its graph looks like.', UNIT)
    d.keys = ['sqrt(', 'cbrt(', 'ln(', 'e^(']
    d.graph('mirror', {'window': [-4, 6, -4, 6], 'pieces': [{'expr': 'exp(x)', 'from': -4, 'to': 1.8}, {'expr': 'ln(x)', 'from': 0.02, 'to': 6}, {'expr': 'x', 'from': -4, 'to': 6, 'dash': True}]})
    L = [
        N('L1', 'An inverse function **undoes** $f$: it takes each output back to the input it came from.' + box('f(2) = 7') + 'So what is $f^(-1)(7)$?', 2, label='$f^(-1)(7)$ =',
          hint='$f$ sent 2 to 7. The inverse sends 7 back.', explain='$f^(-1)(7) = 2$. Inputs and outputs trade places.'),
        ORDER('L2', 'To find a formula for an inverse, undo each step in reverse order. $f(x) = 2x + 3$ doubles, then adds 3. Put the steps of $f^(-1)$ in order.',
              ['Start with $x$', 'Subtract 3', 'Divide by 2'], hint='Think of shoes and socks: the last thing you put on is the first thing you take off.',
              explain='$f$ added 3 last, so the inverse subtracts 3 first.'),
        E(d, 'L3', 'So write the formula for the inverse of $f(x) = 2x + 3$.', '(x - 3)/2', (x - 3) / 2, label='$f^(-1)(x)$ =', keys=[],
          hint='Subtract 3, then divide all of it by 2. The other way to get there: write $y = 2x + 3$, swap $x$ and $y$, and solve for $y$.',
          explain='$f^(-1)(x) = frac{x - 3}{2}$. Check: $f(1) = 5$ and $f^(-1)(5) = 1$.'),
        MC('L4', 'Because inputs and outputs trade places, the graph of $f^(-1)$ is the graph of $f$ reflected over the dashed line. Which line is it?', ['$y = x$', '$y = 0$', '$x = 0$', '$y = -x$'],
           graph='mirror', hint='A point $(a, b)$ becomes $(b, a)$.', explain='Swapping $x$ and $y$ reflects over $y = x$. The two curves here are $e^x$ and its inverse, $ln(x)$.'),
        MC('L5', 'One warning about the notation. Which statement is true?', ['$f^(-1)(x)$ is the inverse function, not $frac{1}{f(x)}$', '$f^(-1)(x)$ always equals $frac{1}{f(x)}$', '$f^(-1)(x)$ equals $-f(x)$', '$f^(-1)(x)$ equals $f(-x)$'],
           hint='For $f(x) = 2x + 3$ you just found $f^(-1)(x) = frac{x - 3}{2}$. Is that $frac{1}{2x + 3}$?', explain='The $-1$ is not an exponent here. It means "inverse". The reciprocal is written $(f(x))^(-1)$ or $frac{1}{f(x)}$.'),
    ]
    d.lesson(L)
    T = [
        MC('T1', '$f(f^(-1)(x)) =$', ['$x$', '1', '0', '$f(x)$'], explain='Doing and then undoing gets you back where you started.'),
        MC('T2', 'If $(2, 9)$ is on the graph of $f$, which point is on the graph of $f^(-1)$?', ['$(9, 2)$', '$(2, -9)$', '$(-2, 9)$', '$(2, frac{1}{9})$'], explain='Swap the coordinates.'),
        MC('T3', 'A function has an inverse function when its graph passes the', ['horizontal line test', 'vertical line test', 'diagonal line test', 'tangent line test'],
           explain='No two inputs may share an output. Otherwise there is no single input to go back to.'),
        TF('T4', '$f(x) = x^2$, on all real numbers, has an inverse function.', False, explain='$f(2) = 4$ and $f(-2) = 4$, so the inverse would not know where to send 4. It works once the domain is cut to $x >= 0$.'),
        MC('T5', 'The domain of $f^(-1)$ is', ['the range of $f$', 'the domain of $f$', 'all real numbers', 'the positive numbers'], explain='The inverse takes the outputs of $f$ as its inputs.'),
        MC('T6', 'The inverse of $f(x) = x^3$ is', ['$x^(1/3)$', '$frac{1}{x^3}$', '$x^(-3)$', '$3x$'], explain='The cube root undoes the cube. $x^(-3)$ is the reciprocal, which is a different thing.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for a0, b0 in [(2, 7), (-1, 4), (5, 0), (3, -2), (0, 6), (4, 10)]:
        Q.append(N(d.qid('P'), f'Suppose $f({a0}) = {b0}$ and $f$ has an inverse. Find $f^(-1)({b0})$.', a0, label=f'$f^(-1)({b0})$ =', level=1, explain=f'$f$ sends {a0} to {b0}, so the inverse sends {b0} back to {a0}.'))
    for a0, b0 in [(2, 5), (-1, 3), (4, -2), (0, 7), (6, 6), (-3, -8)]:
        Q.append(MC(d.qid('S'), f'If $({a0}, {b0})$ is on the graph of $f$, which point is on the graph of $f^(-1)$?',
                    pick_unique([f'$({b0}, {a0})$', f'$({-a0}, {-b0})$', f'$({a0}, {-b0})$', f'$({-b0}, {a0})$', f'$({b0}, {-a0})$', f'$({a0 + 1}, {b0})$'])[:4], level=1, explain='Swap the coordinates.'))
    for f, b0 in [('2x + 3', 11), ('x - 5', 2), ('3x', 12), ('x/2 + 1', 4), ('10 - x', 3), ('4x - 1', 7)]:
        a0 = sp.solve(S(f) - b0, x)[0]
        Q.append(N(d.qid('V'), box(f'f(x) = {Dsum(f)}') + f'Find $f^(-1)({b0})$ by asking: which input gives the output {b0}?', a0, label=f'$f^(-1)({b0})$ =', level=1,
                   explain=f'Solve ${Dsum(f)} = {b0}$: $x = {D(frac_str(a0))}$.'))
    invs = [('3x - 5', '(x + 5)/3'), ('x/2 + 1', '2(x - 1)'), ('x^3', 'cbrt(x)'), ('x^3 + 1', 'cbrt(x - 1)'), ('1/x', '1/x'), ('2/(x + 1)', '2/x - 1'), ('e^x', 'ln(x)'), ('ln(x)', 'e^x'),
            ('4 - x', '4 - x'), ('5x', 'x/5'), ('(x - 2)/3', '3x + 2'), ('e^(2x)', 'ln(x)/2'), ('8x^3', 'cbrt(x)/2'), ('x + 9', 'x - 9')]
    xp = sp.Symbol('x', positive=True)
    for f, ans in invs:
        assert sp.simplify(sp.powdenest(sp.expand_log(S(f).subs(x, S(ans).subs(x, xp)), force=True), force=True) - xp) == 0, (f, ans)
        Q.append(E(d, d.qid('I'), box(f'f(x) = {Dsum(f)}') + 'Find a formula for the inverse.', ans, S(ans), label='$f^(-1)(x)$ =', level=2, ranges={'x': [0.6, 2.4]},
                   explain=f'Write $y = {Dsum(f)}$, swap $x$ and $y$, and solve for $y$: $f^(-1)(x) = {D(ans)}$.'))
    for f, g in [('3x - 5', '(x + 5)/3'), ('x^3 + 1', 'cbrt(x - 1)'), ('2x + 8', 'x/2 - 4'), ('e^(2x)', 'ln(x)/2')]:
        Q.append(E(d, d.qid('K'), box(f'f(x) = {Dsum(f)},    g(x) = {Dsum(g)}') + 'Work out $f(g(x))$ and simplify. What does the answer tell you?', 'x', x, label='$f(g(x))$ =', level=3, keys=[],
                   ranges={'x': [1.2, 2.4]}, explain='$f(g(x)) = x$: each function undoes the other, so they are inverses.'))
    for f, b0, a0 in [('x^3 + x', 2, 1), ('x^3 + x', 10, 2), ('e^x + x', 1, 0), ('x^5 + 2x', 3, 1), ('2x + ln(x)', 2, 1)]:
        assert sp.simplify(S(f).subs(x, a0) - b0) == 0
        Q.append(N(d.qid('G'), box(f'f(x) = {D(f)}') + f'You cannot solve for a formula here. Find $f^(-1)({b0})$ anyway, by trying small whole numbers as inputs.', a0, label=f'$f^(-1)({b0})$ =', level=3,
                   explain=f'$f({a0}) = {b0}$, so $f^(-1)({b0}) = {a0}$. You only need the one input that works.'))
    for txt, right, wrong, ex in [('$f(x) = x^2$ with domain $x >= 0$', '$sqrt(x)$', ['$-sqrt(x)$', '$x^2$', '$frac{1}{x^2}$'], 'With only $x >= 0$ allowed, the positive root undoes the square.'),
                                  ('$f(x) = x^2$ with domain $x <= 0$', '$-sqrt(x)$', ['$sqrt(x)$', '$-x^2$', '$sqrt(-x)$'], 'The inputs were negative, so the inverse must give negative answers.'),
                                  ('$f(x) = (x - 1)^2$ with domain $x >= 1$', '$sqrt(x) + 1$', ['$sqrt(x) - 1$', '$sqrt(x - 1)$', '$sqrt(x + 1)$'], 'Undo the square, then undo the "minus 1".')]:
        Q.append(MC(d.qid('R'), f'The inverse of {txt} is', [right] + wrong, level=3, explain=ex))
    d.drill('practice', 'Practice', Q, 'pool', setSize=10)
    save_graphs(d)


# ====================================================================== 10. Exponentials and Logs
def deck_explog():
    d = Deck('t-explog', 'Exponentials and Logs', 'e and ln, the log rules, and solving equations with them.', UNIT)
    d.keys = ['ln(', 'e^(']
    L = [
        N('L1', '$ln(x)$ asks one question: **$e$ to what power gives $x$?**' + box('ln(e^3) = ?') + 'Answer the question.', 3, label='$ln(e^3)$ =',
          hint='$e$ to what power gives $e^3$?', explain='$ln(e^3) = 3$. The logarithm **is** the exponent.'),
        MATCH('L2', 'That makes $ln$ and $e^x$ inverses: each one undoes the other. Match each expression to its value.', [['$ln(e^5)$', '5'], ['$e^(ln(7))$', '7'], ['$ln(1)$', '0'], ['$ln(e)$', '1']],
              hint='$e^0 = 1$ and $e^1 = e$.', explain='$ln(e^x) = x$ and $e^(ln(x)) = x$. And $ln(1) = 0$ because $e^0 = 1$.'),
        MC('L3', 'There are three log rules, and each one is an exponent rule in disguise. The first: a log turns a **product** into a **sum**.' + box('ln(ab) = ln(a) + ln(b)') + 'So $ln(2x) =$',
           ['$ln(2) + ln(x)$', '$ln(2) · ln(x)$', '$2ln(x)$', '$ln(2 + x)$'], hint='$2x$ is a product: 2 times $x$.', explain='Products become sums. (And quotients become differences: $ln(frac{a}{b}) = ln(a) - ln(b)$.)'),
        MC('L4', 'The one you will use most: an exponent inside a log comes down in front.' + box('ln(a^n) = n · ln(a)') + 'So $ln(x^5) =$', ['$5ln(x)$', '$(ln(x))^5$', '$ln(5x)$', '$ln(x) + 5$'],
           hint='The 5 comes down and multiplies.', explain='$ln(x^5) = 5ln(x)$. This is how logs pull a variable out of an exponent.'),
        E(d, 'L5', 'Which is exactly what you need to solve this.' + box('e^(2x) = 7') + 'Take $ln$ of both sides, then solve for $x$.', 'ln(7)/2', sp.log(7) / 2, [], label='$x$ =',
          hint='$ln(e^(2x)) = 2x$, so $2x = ln(7)$.', explain='$2x = ln(7)$, so $x = frac{ln(7)}{2}$. Leave it exact: no decimals needed.'),
        MC('L6', 'One last pair. Two combinations of $e^x$ and $e^(-x)$ come up often enough to have names, the **hyperbolic** sine and cosine:' + box('sinh(x) = frac{e^x - e^(-x)}{2}') + box('cosh(x) = frac{e^x + e^(-x)}{2}') +
           'What is $cosh(0)$?', ['1', '0', '$e$', '2'], hint='$e^0 = 1$, twice.', explain='$cosh(0) = frac{1 + 1}{2} = 1$, and $sinh(0) = 0$. We will meet their derivatives later; for now, just know what they are.'),
    ]
    d.lesson(L)
    T = [
        TF('T1', '$ln(a + b) = ln(a) + ln(b)$', False, explain='The rule is for a product: $ln(ab) = ln(a) + ln(b)$. The log of a sum does not simplify.'),
        MC('T2', '$ln(1) =$', ['0', '1', '$e$', 'undefined'], explain='$e^0 = 1$, so the exponent that gives 1 is 0.'),
        MC('T3', '$ln(frac{a}{b}) =$', ['$ln(a) - ln(b)$', '$frac{ln(a)}{ln(b)}$', '$ln(a - b)$', '$ln(a) + ln(b)$'], explain='Quotients become differences.'),
        MC('T4', 'For every real number $x$, $e^x$ is', ['positive', 'at least 1', 'negative when $x < 0$', 'zero when $x = 0$'], explain='$e^x$ is never zero and never negative. $e^(-5)$ is small, but still positive.'),
        MC('T5', 'The domain of $ln(x)$ is', ['$(0, ∞)$', '$[0, ∞)$', 'all real numbers', '$(1, ∞)$'], explain='No power of $e$ gives 0 or a negative, so $ln$ only accepts positive inputs. This is the third "refused input" rule.'),
        TF('T6', '$(ln(x))^2 = 2ln(x)$', False, explain='The exponent rule is for a power **inside** the log: $ln(x^2) = 2ln(x)$. $(ln(x))^2$ does not simplify.'),
        MC('T7', '$cosh(x)$ is defined as', ['$frac{e^x + e^(-x)}{2}$', '$frac{e^x - e^(-x)}{2}$', '$cos(e^x)$', '$frac{1}{cos(x)}$'], explain='Plus for $cosh$, minus for $sinh$. They are built from $e^x$, not from the unit circle.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for show, app, v in [('ln(e^4)', 'ln(e^4)', 4), ('ln(1)', 'ln(1)', 0), ('ln(e)', 'ln(e)', 1), ('e^(ln(5))', 'e^(ln(5))', 5), ('ln(frac{1}{e})', 'ln(1/e)', -1), ('ln(sqrt(e))', 'ln(sqrt(e))', sp.Rational(1, 2)),
                         ('e^0', 'e^0', 1), ('ln(e^(-2))', 'ln(e^(-2))', -2), ('e^(2ln(3))', 'e^(2*ln(3))', 9), ('ln(e^2) + ln(e^3)', 'ln(e^2)+ln(e^3)', 5), ('sinh(0)', 'sinh(0)', 0), ('cosh(0)', 'cosh(0)', 1),
                         ('e^(ln(2) + ln(3))', 'e^(ln(2)+ln(3))', 6), ('ln(e^3 · e^4)', 'ln(e^3*e^4)', 7)]:
        assert sp.simplify(S(app) - v) == 0, app
        Q.append(N(d.qid('V'), box(show) + 'Find the exact value.', v, label='value =', level=1, explain=f'${show} = {D(frac_str(v))}$'))
    for eq, right, wrong in [('e^x = 5', 'x = ln(5)', ['x = e^5', 'x = frac{5}{e}', 'x = ln(e^5)']), ('ln(x) = 2', 'x = e^2', ['x = ln(2)', 'x = 2e', 'x = 2^e']),
                             ('e^x = frac{1}{2}', 'x = ln(frac{1}{2})', ['x = e^(1/2)', 'x = frac{1}{2e}', 'no solution']), ('ln(x) = 0', 'x = 1', ['x = 0', 'x = e', 'no solution'])]:
        Q.append(MC(d.qid('M'), f'${eq}$ says the same thing as', ['$' + right + '$'] + ['$' + w + '$' for w in wrong], level=1, explain='$ln$ and $e^x$ undo each other: $e^x = b$ means $x = ln(b)$, and $ln(x) = b$ means $x = e^b$.'))
    ex = [('ln(3x)', 'ln(3) + ln(x)', ['ln(3) · ln(x)', '3ln(x)', 'ln(3 + x)']), ('ln(x^4)', '4ln(x)', ['(ln(x))^4', 'ln(4x)', 'ln(x) + 4']), ('ln(frac{x}{5})', 'ln(x) - ln(5)', ['frac{ln(x)}{ln(5)}', 'ln(x - 5)', 'frac{1}{5}ln(x)']),
          ('ln(x^2 y)', '2ln(x) + ln(y)', ['2ln(x) · ln(y)', '2ln(xy)', 'ln(2x) + ln(y)']), ('ln(sqrt(x))', 'frac{1}{2}ln(x)', ['sqrt(ln(x))', '2ln(x)', 'ln(frac{x}{2})']),
          ('ln(frac{1}{x})', '-ln(x)', ['frac{1}{ln(x)}', 'ln(-x)', '1 - ln(x)']), ('ln(frac{x^3}{y})', '3ln(x) - ln(y)', ['frac{3ln(x)}{ln(y)}', '3ln(x - y)', 'ln(3x) - ln(y)']),
          ('ln(5x^2)', 'ln(5) + 2ln(x)', ['2ln(5x)', '10ln(x)', 'ln(5) · 2ln(x)']), ('ln(e x)', '1 + ln(x)', ['e · ln(x)', 'ln(x)', 'e + ln(x)']), ('ln((x + 1)^3)', '3ln(x + 1)', ['3ln(x) + 3', 'ln(3x + 3)', '(ln(x + 1))^3'])]
    for show, right, wrong in ex:
        Q.append(MC(d.qid('X'), f'Use the log rules to expand ${show}$.', ['$' + right + '$'] + ['$' + w + '$' for w in wrong], level=2, explain=f'Products become sums, quotients become differences, exponents come down: ${right}$.'))
    for eq, lhs, rhs, ans in [('e^x = 5', 'e^x', '5', 'ln(5)'), ('e^(2x) = 7', 'e^(2x)', '7', 'ln(7)/2'), ('ln(x) = 3', 'ln(x)', '3', 'e^3'), ('ln(x) = -1', 'ln(x)', '-1', ['e^(-1)', '1/e']),
                              ('e^(x + 1) = 4', 'e^(x + 1)', '4', 'ln(4) - 1'), ('2e^x = 10', '2e^x', '10', 'ln(5)'), ('ln(2x) = 0', 'ln(2x)', '0', '1/2'), ('e^(3x) = 1', 'e^(3x)', '1', '0'),
                              ('ln(x - 1) = 2', 'ln(x - 1)', '2', 'e^2 + 1'), ('5e^(2x) = 20', '5e^(2x)', '20', 'ln(4)/2'), ('ln(x) + ln(2) = ln(10)', 'ln(x) + ln(2)', 'ln(10)', '5'), ('e^(-x) = 3', 'e^(-x)', '3', '-ln(3)')]:
        sol = [v for v in sp.solve(S(lhs) - S(rhs), x) if v.is_real]
        assert len(sol) == 1, (eq, sol)
        a0 = ans if isinstance(ans, str) else ans[0]
        assert sp.simplify(sol[0] - S(a0)) == 0, (eq, sol)
        Q.append(E(d, d.qid('S'), 'Solve for $x$. Give the exact answer.' + box(eq), ans, sol[0], [], label='$x$ =', level=2, explain=f'Use $ln$ to undo $e$, or $e$ to undo $ln$: $x = {D(a0)}$.'))
    for orig, keys in [('ln(x) + ln(3)', 'ln(3x)'), ('ln(x) - ln(2)', 'ln(x/2)'), ('ln(x + 1) + ln(x - 1)', ['ln(x^2 - 1)', 'ln((x + 1)(x - 1))']), ('ln(6) - ln(2)', 'ln(3)'),
                       ('ln(x) + ln(x + 2)', ['ln(x^2 + 2x)', 'ln(x(x + 2))']), ('ln(5) + ln(x) - ln(10)', 'ln(x/2)')]:
        k0 = keys if isinstance(keys, str) else keys[0]
        kmax = max(cx(a_) for a_ in ([keys] if isinstance(keys, str) else keys))
        q = ES(d, d.qid('C'), 'Combine into a single logarithm.' + box(orig), keys, sp.logcombine(S(orig), force=True), original=orig, slack=min(1, cx(orig) - kmax - 1), label='single log =', level=3,
               ranges={'x': [1.4, 2.6]}, explain=f'Read the rules right to left: a sum of logs is the log of a product. ${D(k0)}$')
        q['longText'] = 'That is equal, but write it as **one** logarithm.'
        Q.append(q)
    for show, orig, key in [('e^(ln(x) + ln(2))', 'e^(ln(x) + ln(2))', '2x'), ('ln(e^(x^2))', 'ln(e^(x^2))', 'x^2'), ('e^(2ln(x))', 'e^(2ln(x))', 'x^2'), ('ln(e^x · e^3)', 'ln(e^x*e^3)', 'x + 3'),
                            ('e^(-ln(x))', 'e^(-ln(x))', '1/x'), ('ln(sqrt(e^x))', 'ln((e^x)^(1/2))', 'x/2')]:
        assert sp.simplify(sp.expand_log(S(orig).subs(x, sp.Symbol('x', positive=True)), force=True) - S(key).subs(x, sp.Symbol('x', positive=True))) == 0, orig
        Q.append(ES(d, d.qid('Z'), 'Simplify. No $e$ and no $ln$ should be left.' + box(show), key, S(key), original=orig, slack=1, label='simplified =', level=3, ranges={'x': [0.5, 1.8]},
                    explain=f'$ln$ and $e$ undo each other once the inside is in the right form: ${D(key)}$.'))
    d.drill('practice', 'Practice', Q, 'pool', setSize=10)
    d.save()


# ====================================================================== 11. The Unit Circle
def exact(v):
    """a standard trig value in app syntax: sqrt(3)/2, -1/2, 0, 1"""
    v = sp.nsimplify(v)
    return sp_app(v)


def deck_circle():
    d = Deck('t-circle', 'The Unit Circle', 'Radians, and sine and cosine as coordinates on the unit circle.', UNIT)
    d.keys = ['sqrt(', 'pi']
    L = [
        MC('L1', 'Calculus measures angles in **radians**. A full turn is $2pi$, so half a turn is $pi$, which is 180°. How many degrees is $frac{pi}{2}$?', ['90°', '45°', '180°', '60°'], fixed=True,
           hint='Half of a half turn.', explain='$frac{pi}{2}$ is a quarter turn, 90°. To convert, remember one fact: $pi$ = 180°.'),
        UCIRCLE('L2', 'Here is the unit circle: radius 1, centered at the origin. At every angle, **cosine is the x-coordinate and sine is the y-coordinate** of the point. Tap these three angles and watch both.',
                'explore', need=[1, 2, 3], labels=True, after='Only three numbers ever show up: $frac{1}{2}$, $frac{sqrt2}{2}$ and $frac{sqrt3}{2}$, smallest to largest. Sine climbs through them while cosine comes down.'),
        MC('L3', 'From what you just saw, $sin(frac{pi}{6}) =$', ['$frac{1}{2}$', '$frac{sqrt3}{2}$', '$frac{sqrt2}{2}$', '1'], hint='$frac{pi}{6}$ is 30°: a low point, so its height is the small number.',
           explain='At $frac{pi}{6}$ the point is far to the right and not very high: $(frac{sqrt3}{2}, frac{1}{2})$.'),
        UCIRCLE('L4', 'The other three quadrants reuse the same values. Only the **signs** change. Tap these and watch the signs.', 'explore', need=[7, 9, 15], labels=True,
                after='Left of the $y$-axis, cosine is negative. Below the $x$-axis, sine is negative. That is all there is to it.'),
        UCIRCLE('L5', 'Now with no labels. Tap the point at $theta = frac{2pi}{3}$.', 'angle', answer=5, hint='$frac{pi}{3}$ is 60°, so $frac{2pi}{3}$ is 120°: a little past straight up.',
                explain='Angles start on the positive $x$-axis and go counterclockwise. 120° lands in the second quadrant.'),
        MC('L6', '$cos(pi) =$', ['−1', '0', '1', '$pi$'], hint='$pi$ is half a turn. Where is the point?', explain='Half a turn puts the point at $(-1, 0)$, and cosine is the $x$-coordinate.'),
    ]
    d.lesson(L)
    T = [
        MC('T1', 'On the unit circle, the point at angle $theta$ is', ['$(cos(theta), sin(theta))$', '$(sin(theta), cos(theta))$', '$(theta, sin(theta))$', '$(tan(theta), 1)$'], explain='Cosine is across, sine is up. Alphabetical, like $x$ and $y$.'),
        MC('T2', '$pi$ radians is', ['180°', '360°', '90°', '3.14°'], fixed=True, explain='Half a turn. Everything else follows from this.'),
        MC('T3', 'In which quadrant are sine and cosine **both** negative?', ['III', 'I', 'II', 'IV'], explain='Left of the $y$-axis and below the $x$-axis: the third quadrant.'),
        TF('T4', '$sin(frac{pi}{2}) = 1$', True, explain='A quarter turn puts the point at the top of the circle, $(0, 1)$.'),
        MC('T5', 'Because the point is on a circle of radius 1, $sin^2(theta) + cos^2(theta) =$', ['1', '0', '$theta$', '2'], explain='It is the Pythagorean theorem for the triangle inside the circle.'),
        MC('T6', '$cos(0) =$', ['1', '0', '−1', 'undefined'], explain='At angle 0 the point is $(1, 0)$.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for deg in [30, 45, 60, 90, 120, 135, 150, 180, 270, 360]:
        th = sp.Rational(deg, 180) * sp.pi
        Q.append(E(d, d.qid('D'), f'Convert {deg}° to radians.', ang_app(th), th, [], label=f'{deg}° =', level=1, explain=f'Multiply by $frac{{pi}}{{180}}$: ${ang(th)}$.'))
    for th in [sp.pi / 6, sp.pi / 4, sp.pi / 3, sp.pi / 2, 2 * sp.pi / 3, sp.pi, 3 * sp.pi / 2, 5 * sp.pi / 4]:
        Q.append(N(d.qid('R'), f'Convert ${ang(th)}$ radians to degrees.', sp.nsimplify(th * 180 / sp.pi), label='degrees =', level=1, explain=f'Replace $pi$ with 180°: {sp.nsimplify(th * 180 / sp.pi)}°.'))
    for i in [1, 3, 5, 6, 7, 9, 10, 11, 13, 14, 15, 4, 12, 8]:
        Q.append(UCIRCLE(d.qid('A'), f'Tap the point at $theta = {ang(UC_ANGLES[i])}$.', 'angle', answer=i, level=1,
                         explain=f'${ang(UC_ANGLES[i])}$ is {sp.nsimplify(UC_ANGLES[i] * 180 / sp.pi)}°, counted counterclockwise from the positive $x$-axis.'))
    first = [0, 1, 2, 3, 4]
    for fn_, nm in [(sp.sin, 'sin'), (sp.cos, 'cos')]:
        for i in first + [8, 12]:
            th = UC_ANGLES[i]
            v = fn_(th)
            Q.append(E(d, d.qid('F'), f'Find the exact value of ${nm}({ang(th)})$.', exact(v), v, [], label=f'${nm}({ang(th)})$ =', level=2,
                       explain=f'The point at ${ang(th)}$ is $({D(exact(sp.cos(th)))}, {D(exact(sp.sin(th)))})$. ' + ('Sine is the $y$-coordinate.' if nm == 'sin' else 'Cosine is the $x$-coordinate.')))
    for fn_, nm in [(sp.sin, 'sin'), (sp.cos, 'cos')]:
        for i in [5, 6, 7, 9, 10, 11, 13, 14, 15]:
            th = UC_ANGLES[i]
            v = fn_(th)
            if (nm == 'sin' and i in (6, 13)) or (nm == 'cos' and i in (5, 10, 14)):
                continue
            Q.append(E(d, d.qid('G'), f'Find the exact value of ${nm}({ang(th)})$.', exact(v), v, [], label=f'${nm}({ang(th)})$ =', level=3,
                       explain=f'The point at ${ang(th)}$ is $({D(exact(sp.cos(th)))}, {D(exact(sp.sin(th)))})$. Same sizes as the first quadrant; the quadrant sets the signs.'))
    for nm, fn_, v in [('sin', sp.sin, sp.Rational(1, 2)), ('cos', sp.cos, sp.Rational(1, 2)), ('sin', sp.sin, -sp.sqrt(2) / 2), ('cos', sp.cos, -sp.sqrt(3) / 2), ('sin', sp.sin, 0), ('cos', sp.cos, 0),
                       ('sin', sp.sin, sp.sqrt(3) / 2), ('cos', sp.cos, sp.sqrt(2) / 2), ('sin', sp.sin, -1), ('cos', sp.cos, -sp.Rational(1, 2))]:
        idx = [i for i, th in enumerate(UC_ANGLES) if sp.simplify(fn_(th) - v) == 0]
        Q.append(UCIRCLE(d.qid('W'), f'Tap **every** point where ${nm}(theta) = {D(exact(v))}$.', 'where', answers=idx, level=3,
                         explain=('Sine is the height of the point' if nm == 'sin' else 'Cosine is how far right or left the point is') + f', so look for every point at that level: {len(idx)} of them.'))
    d.drill('practice', 'Practice', Q, 'pool', setSize=10)
    d.save()


# ====================================================================== 12. Trig Identities and Equations
def deck_trig():
    d = Deck('t-trig', 'Trig Identities and Equations', 'The other four trig functions, the identities worth knowing, and solving trig equations.', UNIT)
    d.keys = ['sqrt(', 'pi', 'sin(', 'cos(', 'tan(']
    L = [
        MATCH('L1', 'The other four trig functions are all built from sine and cosine. Match each one.', [['$tan(x)$', '$frac{sin(x)}{cos(x)}$'], ['$sec(x)$', '$frac{1}{cos(x)}$'], ['$csc(x)$', '$frac{1}{sin(x)}$'], ['$cot(x)$', '$frac{cos(x)}{sin(x)}$']],
              hint='Secant goes with cosine, cosecant goes with sine. Each pair has exactly one "co".', explain='So if you know sine and cosine on the unit circle, you know all six.'),
        N('L2', 'For example:' + box('tan(frac{pi}{4}) = frac{sin(frac{pi}{4})}{cos(frac{pi}{4})}') + 'At $frac{pi}{4}$, sine and cosine are both $frac{sqrt2}{2}$. So what is $tan(frac{pi}{4})$?', 1, label='$tan(frac{pi}{4})$ =',
          hint='Anything divided by itself.', explain='$tan(frac{pi}{4}) = 1$'),
        MC('L3', 'The point $(cos(theta), sin(theta))$ is on a circle of radius 1, so the Pythagorean theorem gives the most-used identity of all:' + box('sin^2(theta) + cos^2(theta) = 1') +
           'If $sin(theta) = frac{3}{5}$ and $theta$ is in the first quadrant, what is $cos(theta)$?', ['$frac{4}{5}$', '$frac{2}{5}$', '$frac{3}{4}$', '$frac{5}{3}$'],
           hint='$cos^2(theta) = 1 - frac{9}{25}$', explain='$cos^2(theta) = frac{16}{25}$, and cosine is positive in the first quadrant, so $cos(theta) = frac{4}{5}$.'),
        UCIRCLE('L4', 'Solving a trig equation means finding points on the circle. Tap **every** angle from 0 to $2pi$ where $sin(theta) = frac{1}{2}$.', 'where', answers=[1, 7],
                hint='Sine is the height of the point. Which points are at height $frac{1}{2}$?', explain='Two answers: $frac{pi}{6}$ and $frac{5pi}{6}$. A trig equation almost always has more than one solution.'),
        MC('L5', 'Last, a notation trap. $sin^2(x)$ means', ['$(sin(x))^2$', '$sin(x^2)$', '$sin(sin(x))$', '$2sin(x)$'], hint='It is how people avoid writing an extra pair of parentheses.',
           explain='$sin^2(x) = (sin(x))^2$: take the sine, then square. But $sin^(-1)(x)$ is the exception: that one means the inverse function, arcsine.'),
    ]
    d.lesson(L)
    T = [
        MC('T1', '$sec(x) =$', ['$frac{1}{cos(x)}$', '$frac{1}{sin(x)}$', '$frac{cos(x)}{sin(x)}$', '$cos(frac{1}{x})$'], explain='Secant is the reciprocal of cosine.'),
        MC('T2', '$1 + tan^2(x) =$', ['$sec^2(x)$', '$csc^2(x)$', '$cos^2(x)$', '1'], explain='Divide $sin^2(x) + cos^2(x) = 1$ by $cos^2(x)$.'),
        TF('T3', '$sin(2x) = 2sin(x)$', False, explain='A 2 inside the function does not come out. The true identity is $sin(2x) = 2sin(x)cos(x)$.'),
        MC('T4', '$sin(-x) =$', ['$-sin(x)$', '$sin(x)$', '$cos(x)$', '$-cos(x)$'], explain='Going clockwise instead flips the height: sine is an odd function.'),
        MC('T5', '$cos(-x) =$', ['$cos(x)$', '$-cos(x)$', '$sin(x)$', '$-sin(x)$'], explain='Going clockwise instead leaves the $x$-coordinate alone: cosine is an even function.'),
        TF('T6', '$sin^(-1)(x)$ means $frac{1}{sin(x)}$.', False, explain='$sin^(-1)(x)$ is the inverse function, arcsine. $frac{1}{sin(x)}$ is $csc(x)$.'),
        MC('T7', '$tan(frac{pi}{2})$ is', ['undefined, because $cos(frac{pi}{2}) = 0$', '0', '1', '$∞$, a very large number'], explain='$tan = frac{sin}{cos}$, and you cannot divide by 0. That is where the graph of tangent has its vertical asymptotes.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for nm, fn_, th in [('tan', sp.tan, sp.pi / 4), ('tan', sp.tan, sp.pi / 3), ('tan', sp.tan, sp.pi / 6), ('tan', sp.tan, 0), ('sec', sp.sec, 0), ('sec', sp.sec, sp.pi / 3), ('csc', sp.csc, sp.pi / 6),
                        ('csc', sp.csc, sp.pi / 2), ('cot', sp.cot, sp.pi / 4), ('sec', sp.sec, sp.pi), ('tan', sp.tan, 3 * sp.pi / 4), ('sec', sp.sec, sp.pi / 4)]:
        v = sp.nsimplify(fn_(th))
        Q.append(E(d, d.qid('V'), f'Find the exact value of ${nm}({ang(th)})$.', exact(v), v, [], label=f'${nm}({ang(th)})$ =', level=1, keys=['sqrt('],
                   explain=f'Here $sin = {D(exact(sp.sin(th)))}$ and $cos = {D(exact(sp.cos(th)))}$, so ${nm}({ang(th)}) = {D(exact(v))}$.'))
    for left, right, wrong in [('tan(x)', 'frac{sin(x)}{cos(x)}', ['frac{cos(x)}{sin(x)}', 'frac{1}{sin(x)}', 'frac{1}{cos(x)}']), ('sec(x)', 'frac{1}{cos(x)}', ['frac{1}{sin(x)}', 'frac{sin(x)}{cos(x)}', 'cos(frac{1}{x})']),
                               ('csc(x)', 'frac{1}{sin(x)}', ['frac{1}{cos(x)}', 'frac{cos(x)}{sin(x)}', 'sin(frac{1}{x})']), ('cot(x)', 'frac{cos(x)}{sin(x)}', ['frac{sin(x)}{cos(x)}', 'frac{1}{cos(x)}', 'frac{1}{sin(x)}']),
                               ('tan(x)cos(x)', 'sin(x)', ['cos(x)', '1', 'sec(x)']), ('frac{1}{sec(x)}', 'cos(x)', ['sin(x)', 'csc(x)', 'tan(x)'])]:
        Q.append(MC(d.qid('W'), f'Rewrite ${left}$ using sine and cosine.', ['$' + right + '$'] + ['$' + w + '$' for w in wrong], level=1, explain=f'${left} = {right}$'))
    ids = [('sin^2(x) + cos^2(x)', '1', ['0', 'sin(2x)', 'tan^2(x)']), ('1 + tan^2(x)', 'sec^2(x)', ['csc^2(x)', 'cos^2(x)', 'sin^2(x)']), ('1 - cos^2(x)', 'sin^2(x)', ['-sin^2(x)', 'tan^2(x)', 'cos^2(x)']),
           ('1 - sin^2(x)', 'cos^2(x)', ['-cos^2(x)', 'sin^2(x)', 'sec^2(x)']), ('sin(2x)', '2sin(x)cos(x)', ['2sin(x)', 'sin^2(x)', '2cos(x)']), ('sec^2(x) - 1', 'tan^2(x)', ['cot^2(x)', 'sin^2(x)', '1']),
           ('sin(-x)', '-sin(x)', ['sin(x)', 'cos(x)', '-cos(x)']), ('cos(-x)', 'cos(x)', ['-cos(x)', 'sin(x)', '-sin(x)']), ('sin(x + 2pi)', 'sin(x)', ['-sin(x)', 'cos(x)', 'sin(x) + 2pi']),
           ('frac{sin(x)}{cos(x)}', 'tan(x)', ['cot(x)', 'sec(x)', 'csc(x)'])]
    for left, right, wrong in ids:
        Q.append(MC(d.qid('I'), f'${left} =$', ['$' + right + '$'] + ['$' + w + '$' for w in wrong], level=2, explain=f'${left} = {right}$'))
    for given, gv, want, quad, v in [('sin', '3/5', 'cos', 'first', sp.Rational(4, 5)), ('cos', '5/13', 'sin', 'first', sp.Rational(12, 13)), ('sin', '4/5', 'cos', 'second', -sp.Rational(3, 5)),
                                     ('cos', '-3/5', 'sin', 'second', sp.Rational(4, 5)), ('sin', '-5/13', 'cos', 'fourth', sp.Rational(12, 13)), ('cos', '8/17', 'sin', 'first', sp.Rational(15, 17))]:
        assert S(gv) ** 2 + v ** 2 == 1
        Q.append(N(d.qid('P'), f'If ${given}(theta) = {D(gv)}$ and $theta$ is in the {quad} quadrant, find ${want}(theta)$.', v, label=f'${want}(theta)$ =', level=2,
                   explain=f'Use $sin^2 + cos^2 = 1$ for the size, and the quadrant for the sign: ${D(frac_str(v))}$.'))
    eqs = [('sin(theta) = frac{sqrt3}{2}', sp.sin(TH) - sp.sqrt(3) / 2), ('cos(theta) = -frac{1}{2}', sp.cos(TH) + sp.Rational(1, 2)), ('tan(theta) = 1', None), ('sin(theta) = 0', sp.sin(TH)),
           ('cos(theta) = 0', sp.cos(TH)), ('2sin(theta) - 1 = 0', 2 * sp.sin(TH) - 1), ('sin(theta) = -1', sp.sin(TH) + 1), ('cos(theta) = 1', sp.cos(TH) - 1), ('sin^2(theta) = frac{1}{4}', sp.sin(TH) ** 2 - sp.Rational(1, 4)),
           ('2cos(theta) + sqrt3 = 0', 2 * sp.cos(TH) + sp.sqrt(3)), ('tan(theta) = -1', None), ('cos^2(theta) = 1', sp.cos(TH) ** 2 - 1)]
    for show, e_ in eqs:
        if e_ is None:
            tv = 1 if '= 1' in show else -1
            idx = [i for i, th in enumerate(UC_ANGLES) if sp.cos(th) != 0 and sp.simplify(sp.tan(th) - tv) == 0]
        else:
            idx = [i for i, th in enumerate(UC_ANGLES) if sp.simplify(e_.subs(TH, th)) == 0]
        assert idx, show
        Q.append(UCIRCLE(d.qid('S'), f'Solve ${show}$ on the unit circle: tap **every** angle from 0 to $2pi$ that works.', 'where', answers=idx, level=3,
                         explain='The solutions are $theta = ' + '$, $'.join(ang(UC_ANGLES[i]) for i in idx) + '$.'))
    for show, orig, key in [('tan(x)cos(x)', 'tan(x)cos(x)', 'sin(x)'), ('sec(x)cos(x)', 'cos(x)/cos(x)', '1'), ('frac{1 - cos^2(x)}{sin(x)}', '(1 - cos(x)^2)/sin(x)', 'sin(x)'),
                            ('frac{sin(x)}{tan(x)}', 'sin(x)/tan(x)', 'cos(x)'), ('frac{sin^2(x) + cos^2(x)}{cos(x)} · cos(x)', '(sin(x)^2 + cos(x)^2)/cos(x)*cos(x)', '1'),
                            ('(1 - sin(x))(1 + sin(x))', '(1 - sin(x))(1 + sin(x))', 'cos(x)^2')]:
        Q.append(ES(d, d.qid('Z'), 'Simplify to a single trig function or a number.' + box(show), key, S(key), original=orig, slack=min(1, cx(orig) - cx(key) - 1), label='simplified =', level=3,
                    ranges={'x': [0.3, 1.2]}, explain=f'Rewrite everything with sine and cosine, then cancel or use $sin^2 + cos^2 = 1$: ${D(key)}$.'))
    for show, v in [('arcsin(frac{1}{2})', sp.pi / 6), ('arccos(0)', sp.pi / 2), ('arctan(1)', sp.pi / 4), ('arcsin(1)', sp.pi / 2), ('arccos(frac{1}{2})', sp.pi / 3), ('arctan(0)', sp.Integer(0))]:
        Q.append(E(d, d.qid('N'), f'${show}$ asks: which angle has that sine (or cosine, or tangent)? Give the angle in radians.', ang_app(v), v, [], label=f'${show}$ =', level=3, keys=['pi'],
                   explain=f'The angle is ${ang(v)}$. Inverse trig functions hand back an **angle**.'))
    d.drill('practice', 'Practice', Q, 'pool', setSize=10)
    d.save()


# ====================================================================== Readiness Check
def deck_ready():
    """a practice test drawn from the twelve Toolkit decks: level 2 and 3 questions, no feedback until the end"""
    d = Deck('t-ready', 'Readiness Check', 'A practice run for the in-class Algebra Readiness Check.', UNIT)
    R = random.Random(2027)
    src = [('t-notation', 'Function notation', 'n', 5), ('t-domain', 'Domain and piecewise', 'd', 5), ('t-factor', 'Factoring', 'f', 6), ('t-rational', 'Rational expressions', 'r', 6),
           ('t-exponents', 'Exponent rules', 'e', 6), ('t-radicals', 'Radicals and conjugates', 'k', 5), ('t-graphs', 'Graphs and shifts', 'g', 5), ('t-compose', 'Composition', 'c', 5),
           ('t-inverse', 'Inverse functions', 'i', 4), ('t-explog', 'Exponentials and logs', 'l', 6), ('t-circle', 'The unit circle', 'u', 6), ('t-trig', 'Trig identities and equations', 't', 5)]
    Q = []
    for deck_id, topic, pre, n_ in src:
        D0 = json.load(open(os.path.join(ROOT, 'decks', deck_id + '.json')))
        pool = [q for q in D0['drills']['practice']['questions'] if q.get('level', 1) >= 2 and q['type'] != 'steps']
        byt = {}
        for q in pool:
            byt.setdefault(q['id'][0], []).append(q)
        picks, groups = [], sorted(byt)
        while len(picks) < n_ and any(byt.values()):
            for g in groups:
                if byt[g] and len(picks) < n_:
                    picks.append(byt[g].pop(R.randrange(len(byt[g]))))
        for q in picks:
            q = json.loads(json.dumps(q))
            q['id'] = pre + q['id']
            q['topic'] = topic
            q.pop('level', None)
            if q.get('graph'):
                d.graph(pre + q['graph'], D0['graphs'][q['graph']])
                q['graph'] = pre + q['graph']
            Q.append(q)
    d.drill('exam', 'Readiness Check', Q, None, exam=True, setSize=20)
    del d.d['drills']['exam']['mode']
    d.save()


DECKS = {'t-inverse': deck_inverse, 't-explog': deck_explog, 't-circle': deck_circle, 't-trig': deck_trig, 't-ready': deck_ready}
