"""World 0 (The Toolkit), part B: class days 3 and 4.
   t-exponents Exponent Rules        t-radicals Radicals and Conjugates
   t-graphs    Graphs and Shifts     t-compose  Composition"""
import random, re
import sympy as sp
from lib import *
from world0a import UNIT, disp, Dsum, save_graphs, sub_in

XP = sp.Symbol('x', positive=True)


def power_of(app):
    """the n with app-expression = x^n (for x > 0)"""
    e = S(app).subs(x, XP)
    n_ = sp.simplify(sp.expand_log(sp.log(sp.powsimp(sp.powdenest(e, force=True), force=True)), force=True) / sp.log(XP))
    assert n_.is_number, (app, n_)
    return sp.nsimplify(n_)


def slack_for(orig, keys):
    k = max(cx(a_) for a_ in ([keys] if isinstance(keys, str) else keys))
    s_ = min(2, cx(orig) - k - 1)
    assert s_ >= 0, ('no room to tell the simplified answer from the original', orig, keys)
    return s_


# ====================================================================== 5. Exponent Rules
def deck_exponents():
    d = Deck('t-exponents', 'Exponent Rules', 'Negative and fractional exponents, and rewriting roots and fractions as powers.', UNIT)
    ONE = 'That is equal, but write it as $x$ to a **single** power.'
    L = [
        MATCH('L1', 'Three rules do most of the work. Match each one to what it equals.', [['$x^a · x^b$', '$x^(a + b)$'], ['$frac{x^a}{x^b}$', '$x^(a - b)$'], ['$(x^a)^b$', '$x^(ab)$']],
              hint='Try them with small numbers: $x^2 · x^3$ is five $x$’s multiplied together.', explain='Multiply: add the exponents. Divide: subtract. A power of a power: multiply.'),
        N('L2', 'A **negative** exponent means "one over".' + box('x^(-n) = frac{1}{x^n}') + 'So $frac{1}{x^3} = x^n$. What is $n$?', -3, label='$n$ =',
          hint='Moving a power from the bottom to the top flips the sign of its exponent.', explain='$frac{1}{x^3} = x^(-3)$. Nothing became negative: the exponent just says "bottom".'),
        N('L3', 'A **fractional** exponent is a root.' + box('x^(1/2) = sqrt(x)') + 'The cube root works the same way: $cbrt(x) = x^n$. What is $n$? Use the fraction key.', sp.Rational(1, 3), label='$n$ =',
          hint='Square root is the $frac{1}{2}$ power. Cube root is the …', explain='$cbrt(x) = x^(1/3)$. The root goes on the bottom of the fraction.'),
        N('L4', 'Both ideas at once.' + box('frac{1}{sqrt(x)} = x^n') + 'What is $n$?', sp.Rational(-1, 2), label='$n$ =',
          hint='$sqrt(x) = x^(1/2)$, and it sits on the bottom.', explain='$frac{1}{sqrt(x)} = x^(-1/2)$'),
        ES(d, 'L5', 'This is why it matters: a messy term becomes one clean power, and one clean power is easy to work with.' + box('frac{x^2}{sqrt(x)}') + 'Write it as $x$ to a single power.',
           'x^(3/2)', x ** sp.Rational(3, 2), original='x^2/x^(1/2)', label='$frac{x^2}{sqrt(x)}$ =', hint='$frac{x^2}{x^(1/2)}$: dividing means subtract the exponents, $2 - frac{1}{2}$.',
           explain='$x^(2 - 1/2) = x^(3/2)$. In February every derivative of a root starts with this rewrite.'),
    ]
    L[4]['longText'] = ONE
    d.lesson(L)
    T = [
        TF('T1', '$x^2 · x^3 = x^6$', False, explain='Multiplying adds the exponents: $x^2 · x^3 = x^5$. (It is $(x^2)^3$ that equals $x^6$.)'),
        TF('T2', '$(x^2)^3 = x^6$', True, explain='A power of a power multiplies: $2 · 3 = 6$.'),
        MC('T3', 'For $x ≠ 0$, $x^0 =$', ['1', '0', '$x$', 'undefined'], explain='$frac{x^3}{x^3} = x^(3 - 3) = x^0$, and anything divided by itself is 1.'),
        MC('T4', '$x^(-2)$ means', ['$frac{1}{x^2}$', '$-x^2$', '$-2x$', '$frac{1}{2x}$'], explain='A negative exponent never makes the number negative. It sends the power to the bottom.'),
        MC('T5', '$(2x)^3 =$', ['$8x^3$', '$2x^3$', '$6x^3$', '$8x$'], explain='The exponent applies to everything in the parentheses: $2^3 · x^3$.'),
        MC('T6', '$frac{1}{2x^3}$ written with a power of $x$ is', ['$frac{1}{2}x^(-3)$', '$2x^(-3)$', '$(2x)^(-3)$', '$frac{1}{2}x^3$'],
           explain='Only the $x^3$ moves up and becomes $x^(-3)$. The 2 stays on the bottom, as $frac{1}{2}$.'),
        MC('T7', '$sqrt(x^2 + 9)$ simplifies to', ['It does not simplify', '$x + 3$', '$x + 9$', '$3x$'], explain='Roots (and powers) do not split over a sum. Try $x = 4$: $sqrt(25) = 5$, not 7.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    one = [('frac{1}{x^3}', '1/x^3'), ('sqrt(x)', 'x^(1/2)'), ('frac{1}{x}', '1/x'), ('x^2 · x^5', 'x^2*x^5'), ('frac{x^7}{x^3}', 'x^7/x^3'), ('(x^3)^4', '(x^3)^4'), ('frac{1}{x^5}', '1/x^5'),
           ('x · x^4', 'x*x^4'), ('frac{x^2}{x^6}', 'x^2/x^6'), ('(x^2)^(-3)', '(x^2)^(-3)'), ('frac{1}{sqrt(x)}', '1/x^(1/2)'), ('x^3 · x^(-5)', 'x^3*x^(-5)'), ('sqrt(x) · sqrt(x)', 'x^(1/2)*x^(1/2)'),
           ('(x^(1/2))^6', '(x^(1/2))^6'), ('cbrt(x)', 'x^(1/3)'), ('cbrt(x^2)', 'x^(2/3)'), ('frac{1}{cbrt(x)}', '1/x^(1/3)')]
    for show, app in one:
        n_ = power_of(app)
        Q.append(N(d.qid('N'), box(show + ' = x^n') + 'What is $n$?' + ('' if n_.is_Integer else ' Use the fraction key.'), n_, label='$n$ =', level=1, explain=f'${show} = x^({frac_str(n_)})$'))
    for app, v in [('8^(2/3)', 4), ('16^(1/2)', 4), ('27^(1/3)', 3), ('4^(-1)', sp.Rational(1, 4)), ('9^(3/2)', 27), ('2^(-3)', sp.Rational(1, 8)), ('25^(-1/2)', sp.Rational(1, 5)),
                   ('(1/2)^(-2)', 4), ('16^(3/4)', 8), ('5^0', 1), ('32^(2/5)', 4), ('100^(-1/2)', sp.Rational(1, 10))]:
        assert sp.nsimplify(S(app)) == v, app
        show = app.replace('(1/2)^', '(frac{1}{2})^')
        Q.append(N(d.qid('V'), box(show) + 'Find the value: a whole number or a fraction.', v, label='value =', level=2,
                   explain=f'Root first, then the power, and a negative exponent means "one over": ${show} = {D(frac_str(v))}$.'))
    for show, right, wrong in [('frac{1}{2x^3}', 'frac{1}{2}x^(-3)', ['2x^(-3)', '(2x)^(-3)', 'frac{1}{2}x^3']), ('frac{3}{x^2}', '3x^(-2)', ['frac{1}{3}x^(-2)', '(3x)^(-2)', '3x^2']),
                               ('frac{5}{sqrt(x)}', '5x^(-1/2)', ['5x^(1/2)', 'frac{1}{5}x^(-1/2)', '(5x)^(-1/2)']), ('frac{1}{4x}', 'frac{1}{4}x^(-1)', ['4x^(-1)', '(4x)^(-1) · 4', 'frac{1}{4}x']),
                               ('frac{2}{3x^4}', 'frac{2}{3}x^(-4)', ['frac{3}{2}x^(-4)', '6x^(-4)', 'frac{2}{3}x^4'])]:
        Q.append(MC(d.qid('M'), f'Which is ${show}$ written with a power of $x$ and no $x$ on the bottom?', ['$' + right + '$'] + ['$' + w + '$' for w in wrong], level=2,
                    explain=f'Only the power of $x$ moves up. The numbers stay where they are: ${show} = {right}$.'))
    for show, orig, key in [('frac{x^2}{sqrt(x)}', 'x^2/x^(1/2)', 'x^(3/2)'), ('x · sqrt(x)', 'x*x^(1/2)', 'x^(3/2)'), ('frac{x}{x^3}', 'x/x^3', 'x^(-2)'), ('frac{sqrt(x)}{x}', 'x^(1/2)/x', 'x^(-1/2)'),
                            ('(x^2)^3 · x', '(x^2)^3*x', 'x^7'), ('frac{x^5 · x}{x^2}', 'x^5*x/x^2', 'x^4'), ('frac{1}{x^2 · x^3}', '1/(x^2*x^3)', 'x^(-5)'), ('(sqrt(x))^3', '(x^(1/2))^3', 'x^(3/2)'),
                            ('frac{x^3}{x^(-2)}', 'x^3/x^(-2)', 'x^5'), ('sqrt(x^3)', '(x^3)^(1/2)', 'x^(3/2)'), ('frac{x^(1/2)}{x^(3/2)}', 'x^(1/2)/x^(3/2)', 'x^(-1)'), ('cbrt(x) · x^2', 'x^(1/3)*x^2', 'x^(7/3)')]:
        q = ES(d, d.qid('S'), box(show) + 'Write it as $x$ to a single power.', key, S(orig), original=orig, slack=slack_for(orig, key), label='$x$ to a power =', level=3,
               explain=f'${show} = {D(key, False)}$')
        q['longText'] = ONE
        Q.append(q)
    for orig, keys in [('(x^3 + 2x)/x', 'x^2 + 2'), ('(4x^5 - 6x^2)/(2x)', '2x^4 - 3x'), ('(x^2 + 1)/x', ['x + 1/x', 'x + x^(-1)']), ('(x^4 - x)/x^2', ['x^2 - 1/x', 'x^2 - x^(-1)']),
                       ('(6x^3 + 9x^2)/(3x)', '2x^2 + 3x'), ('(x^5 + x^3)/x^3', 'x^2 + 1')]:
        k0 = keys if isinstance(keys, str) else keys[0]
        Q.append(ES(d, d.qid('D'), 'A sum on **top** splits up. Divide each term by the bottom and simplify.' + box(D(orig)), keys, sp.expand(S(orig)), original=orig, slack=slack_for(orig, keys),
                    label='simplified =', level=3, explain=f'Each term on top gets divided separately: ${D(k0, False)}$.'))
    d.drill('practice', 'Practice', Q, 'pool', setSize=10)
    d.save()


# ====================================================================== 6. Radicals and Conjugates
def deck_radicals():
    d = Deck('t-radicals', 'Radicals and Conjugates', 'Simplifying square roots, and the conjugate trick that clears them.', UNIT)
    d.keys = ['sqrt(']
    L = [
        MC('L1', 'Square roots split over **multiplication**:' + box('sqrt(ab) = sqrt(a) · sqrt(b)') + 'So $sqrt(50) = sqrt(25 · 2)$ is', ['$5sqrt(2)$', '$25sqrt(2)$', '$2sqrt(5)$', '10'],
           hint='$sqrt(25) = 5$, and the $sqrt(2)$ stays.', explain='Pull out the perfect square: $sqrt(25) · sqrt(2) = 5sqrt(2)$.'),
        TF('L2', 'They do **not** split over addition. True or false: $sqrt(9 + 16) = sqrt(9) + sqrt(16)$', False, hint='Work out both sides.',
           explain='$sqrt(25) = 5$, but $3 + 4 = 7$. This is the most common algebra mistake in calculus. A root of a sum stays as it is.'),
        ES(d, 'L3', 'So how do you get rid of a root that is stuck in a sum? With the difference of squares.' + box('(a - b)(a + b) = a^2 - b^2') + 'Multiply out $(sqrt(x) - 3)(sqrt(x) + 3)$.',
           'x - 9', x - 9, original='(sqrt(x) - 3)(sqrt(x) + 3)', label='product =', hint='Here $a = sqrt(x)$ and $b = 3$, and $(sqrt(x))^2 = x$.',
           explain='The root is gone. $sqrt(x) + 3$ is called the **conjugate** of $sqrt(x) - 3$: same two terms, opposite sign in the middle.'),
        MC('L4', 'What is the conjugate of $sqrt(x + 1) - 2$?', ['$sqrt(x + 1) + 2$', '$sqrt(x - 1) - 2$', '$-sqrt(x + 1) - 2$', '$sqrt(x + 1) - 2$'],
           hint='Only the sign between the two terms changes.', explain='Nothing inside the root changes. Only the middle sign flips.'),
        STEPS('L5', 'Here is the payoff. At $x = 9$ this fraction is $frac{0}{0}$. Multiply the top and the bottom by the conjugate of the top.' + box('frac{sqrt(x) - 3}{x - 9}'), [
            ES(d, 'L5.1', 'The new top is $(sqrt(x) - 3)(sqrt(x) + 3)$. Multiply it out.', 'x - 9', x - 9, original='(sqrt(x) - 3)(sqrt(x) + 3)', label='top =', hint='$a^2 - b^2$', work='top $= x - 9$'),
            MC('L5.2', 'So the fraction is now $frac{x - 9}{(x - 9)(sqrt(x) + 3)}$. Cancel.', ['$frac{1}{sqrt(x) + 3}$', '$sqrt(x) + 3$', '$frac{1}{sqrt(x) - 3}$', '$frac{x - 9}{sqrt(x) + 3}$'],
               hint='$x - 9$ is a factor of the top and of the bottom.', work='$= frac{1}{sqrt(x) + 3}$'),
            N('L5.3', 'Now $x = 9$ causes no trouble. Plug it in.', sp.Rational(1, 6), label='value =', hint='$frac{1}{sqrt(9) + 3}$', work='at $x = 9$: $frac{1}{6}$'),
        ]),
    ]
    d.lesson(L)
    T = [
        TF('T1', '$sqrt(x^2 + 16) = x + 4$', False, explain='A root does not split over a sum. Try $x = 3$: $sqrt(25) = 5$, not 7.'),
        TF('T2', 'For $x >= 0$, $sqrt(4x) = 2sqrt(x)$', True, explain='A root does split over a product: $sqrt(4) · sqrt(x)$.'),
        MC('T3', 'For $x >= 0$, $(sqrt(x))^2 =$', ['$x$', '$x^2$', '$sqrt(x)$', '$2x$'], explain='Squaring undoes the square root.'),
        MC('T4', 'For **any** real number $x$, $sqrt(x^2) =$', ['$|x|$', '$x$', '$-x$', '$x^2$'], explain='Try $x = -3$: $sqrt(9) = 3$, which is $|-3|$. A square root is never negative.'),
        MC('T5', 'The conjugate of $3 + sqrt(x)$ is', ['$3 - sqrt(x)$', '$-3 + sqrt(x)$', '$3 + sqrt(x)$', '$sqrt(x) - 3$'], fixed=False, explain='Keep the two terms in place and flip the sign between them.'),
        MC('T6', 'Multiplying $sqrt(a) - sqrt(b)$ by its conjugate gives', ['$a - b$', '$a + b$', '$a - 2sqrt(ab) + b$', '$sqrt(a - b)$'], explain='$(sqrt(a))^2 - (sqrt(b))^2 = a - b$. The cross terms cancel, and that is the whole point.'),
    ]
    T[4]['options'] = ['$3 - sqrt(x)$', '$-3 - sqrt(x)$', '$3 + sqrt(x)$', '$frac{1}{3 + sqrt(x)}$']
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for n_, r_, a_ in [(50, 2, 5), (12, 3, 2), (18, 2, 3), (75, 3, 5), (8, 2, 2), (45, 5, 3), (72, 2, 6), (48, 3, 4), (200, 2, 10), (27, 3, 3)]:
        assert a_ * a_ * r_ == n_
        Q.append(N(d.qid('A'), box(f'sqrt({n_}) = a sqrt({r_})') + 'What is $a$?', a_, label='$a$ =', level=1, explain=f'${n_} = {a_ * a_} · {r_}$, and $sqrt({a_ * a_}) = {a_}$.'))
    for show, app, v in [('sqrt(49)', 'sqrt(49)', 7), ('sqrt(frac{1}{4})', 'sqrt(1/4)', sp.Rational(1, 2)), ('sqrt(16) · sqrt(9)', 'sqrt(16)*sqrt(9)', 12), ('sqrt(3) · sqrt(12)', 'sqrt(3)*sqrt(12)', 6),
                         ('frac{sqrt(50)}{sqrt(2)}', 'sqrt(50)/sqrt(2)', 5), ('(sqrt(7))^2', 'sqrt(7)^2', 7), ('sqrt(5^2 + 12^2)', 'sqrt(5^2+12^2)', 13), ('sqrt(9 + 16)', 'sqrt(9+16)', 5),
                         ('sqrt(100 - 36)', 'sqrt(100-36)', 8), ('sqrt(2) · sqrt(8)', 'sqrt(2)*sqrt(8)', 4)]:
        assert sp.simplify(S(app) - v) == 0, app
        Q.append(N(d.qid('V'), box(show) + 'Find the value.', v, label='value =', level=1, explain=f'${show} = {D(frac_str(v))}$'))
    for orig, key in [('(sqrt(x) - 3)(sqrt(x) + 3)', 'x - 9'), ('(sqrt(x) + 5)(sqrt(x) - 5)', 'x - 25'), ('(sqrt(x + 1) - 2)(sqrt(x + 1) + 2)', 'x - 3'), ('(3 - sqrt(x))(3 + sqrt(x))', '9 - x'),
                      ('(sqrt(x + h) - sqrt(x))(sqrt(x + h) + sqrt(x))', 'h'), ('(sqrt(x + 4) - 2)(sqrt(x + 4) + 2)', 'x'), ('(sqrt(2x) - 1)(sqrt(2x) + 1)', '2x - 1'),
                      ('(sqrt(x^2 + 9) - 3)(sqrt(x^2 + 9) + 3)', 'x^2'), ('(1 - sqrt(x))(1 + sqrt(x))', '1 - x'), ('(sqrt(x) - sqrt(2))(sqrt(x) + sqrt(2))', 'x - 2')]:
        vars_ = ['x', 'h'] if 'h' in orig else ['x']
        Q.append(ES(d, d.qid('C'), 'Multiply out. The roots should disappear.' + box(D(orig, False)), key, sp.expand(S(orig)), original=orig, vars_=vars_, label='product =', level=2,
                    explain=f'$a^2 - b^2$ with the root as $a$: ${D(key)}$.'))
    for e_, right, wrong in [('sqrt(x) - 4', 'sqrt(x) + 4', ['sqrt(x) - 4', '-sqrt(x) - 4', 'sqrt(x + 4)']), ('sqrt(x + 2) + 1', 'sqrt(x + 2) - 1', ['sqrt(x - 2) + 1', 'sqrt(x + 2) + 1', 'sqrt(x - 2) - 1']),
                             ('5 - sqrt(x)', '5 + sqrt(x)', ['-5 - sqrt(x)', '5 - sqrt(x)', 'sqrt(x) - 5']), ('sqrt(x + h) - sqrt(x)', 'sqrt(x + h) + sqrt(x)', ['sqrt(x - h) - sqrt(x)', 'sqrt(x + h) - sqrt(x)', 'sqrt(x) - sqrt(x + h)']),
                             ('sqrt(x^2 + 1) - x', 'sqrt(x^2 + 1) + x', ['sqrt(x^2 - 1) - x', 'sqrt(x^2 + 1) - x', 'x - sqrt(x^2 + 1)'])]:
        Q.append(MC(d.qid('J'), f'What is the conjugate of ${e_}$?', ['$' + right + '$'] + ['$' + w + '$' for w in wrong], level=2, explain='Same two terms, with the sign between them flipped.'))
    for show, right, wrong in [('frac{1}{sqrt(2)}', 'frac{sqrt(2)}{2}', ['sqrt(2)', 'frac{1}{2}', '2sqrt(2)']), ('frac{3}{sqrt(3)}', 'sqrt(3)', ['3sqrt(3)', 'frac{sqrt(3)}{9}', '1']),
                               ('frac{6}{sqrt(2)}', '3sqrt(2)', ['6sqrt(2)', 'frac{3}{sqrt(2)}', '3']), ('frac{1}{sqrt(5)}', 'frac{sqrt(5)}{5}', ['sqrt(5)', 'frac{1}{5}', '5sqrt(5)']),
                               ('frac{10}{sqrt(5)}', '2sqrt(5)', ['10sqrt(5)', '2', 'frac{sqrt(5)}{2}'])]:
        Q.append(MC(d.qid('R'), f'Which is equal to ${show}$, with no root on the bottom?', ['$' + right + '$'] + ['$' + w + '$' for w in wrong], level=2,
                    explain=f'Multiply the top and the bottom by the root: ${show} = {right}$.'))
    for top, bot, a0, c in [('sqrt(x) - 3', 'x - 9', 9, 1), ('sqrt(x) - 2', 'x - 4', 4, 1), ('sqrt(x + 1) - 2', 'x - 3', 3, 1), ('sqrt(x + 4) - 2', 'x', 0, 1), ('sqrt(x) - 5', 'x - 25', 25, 1),
                            ('sqrt(x + 5) - 3', 'x - 4', 4, 1), ('sqrt(2x + 1) - 3', 'x - 4', 4, 2)]:
        conj = top.replace(' - ', ' + ')
        newtop = sp.expand(S(top) * S(conj))
        after = f'{c}/({conj})'
        assert sp.simplify(S(top) / S(bot) - S(after)) == 0, top
        val = sp.limit(S(top) / S(bot), x, a0)
        nt = sp_app(newtop)
        qid = d.qid('X')
        st = [ES(d, qid + '.1', f'Multiply the top by its conjugate, ${D(conj)}$. What is the new top?', nt, newtop, original=f'({top})({conj})', label='new top =', work=f'top $= {D(nt)}$'),
              ES(d, qid + '.2', f'The bottom is now $({D(bot)})({D(conj)})$. Cancel, and write what is left.', after, S(after), original=f'({top})/({bot})', slack=0, soft=True, label='simplified =',
                 ranges={'x': [a0 + 1.5, a0 + 4]}, work=f'$= {D(after)}$'),
              N(qid + '.3', f'Now plug in $x = {a0}$.', val, label='value =', work=f'at $x = {a0}$: ${D(frac_str(val))}$')]
        Q.append(STEPS(qid, f'At $x = {a0}$ this fraction is $frac{{0}}{{0}}$. Use the conjugate to find what it is heading toward.' + box(f'frac{{{top}}}{{{bot}}}'), st, level=3,
                       explain=f'After the conjugate, the fraction is ${D(after)}$, which is ${D(frac_str(val))}$ at $x = {a0}$.'))
    qid = d.qid('X')
    st = [ES(d, qid + '.1', 'Multiply the top by its conjugate, $sqrt(x + h) + sqrt(x)$. What is the new top?', 'h', h, original='(sqrt(x + h) - sqrt(x))(sqrt(x + h) + sqrt(x))', vars_=['x', 'h'], label='new top =',
             work='top $= h$'),
          ES(d, qid + '.2', 'The $h$ on top cancels the $h$ on the bottom. Write what is left.', '1/(sqrt(x + h) + sqrt(x))', 1 / (sp.sqrt(x + h) + sp.sqrt(x)), original='(sqrt(x + h) - sqrt(x))/h', slack=0, soft=True,
             vars_=['x', 'h'], label='simplified =', work='$= frac{1}{sqrt(x + h) + sqrt(x)}$'),
          E(d, qid + '.3', 'Now let $h = 0$.', '1/(2sqrt(x))', 1 / (2 * sp.sqrt(x)), label='at $h = 0$:', work='$= frac{1}{2sqrt(x)}$')]
    Q.append(STEPS(qid, 'This is the difference quotient for $f(x) = sqrt(x)$. At $h = 0$ it is $frac{0}{0}$. Clear the roots with the conjugate.' + box('frac{sqrt(x + h) - sqrt(x)}{h}'), st, level=3,
                   explain='You just found the derivative of $sqrt(x)$: it is $frac{1}{2sqrt(x)}$.'))
    d.drill('practice', 'Practice', Q, 'pool', setSize=10)
    d.save()


# ====================================================================== 7. Graphs and Shifts
BASES = {'x^2': ([-6, 6, -6, 6], 'x^2'), 'abs(x)': ([-6, 6, -6, 6], '|x|'), 'sqrt(x)': ([-6, 6, -5, 5], 'sqrt(x)'), 'x^3': ([-5, 5, -6, 6], 'x^3')}


def shifted(base, h_, k_, a_=1):
    """the formula of a·f(x - h) + k for a named base, in app syntax"""
    inner = 'x' if h_ == 0 else f'x {"-" if h_ > 0 else "+"} {abs(h_)}'
    core = {'x^2': f'({inner})^2' if h_ else 'x^2', 'abs(x)': f'abs({inner})', 'sqrt(x)': f'sqrt({inner})', 'x^3': f'({inner})^3' if h_ else 'x^3'}[base]
    A = {1: '', -1: '-', 2: '2', -2: '-2'}[a_]
    return A + core + ('' if k_ == 0 else f' {"+" if k_ > 0 else "-"} {abs(k_)}')


def move_words(h_, k_, a_=1):
    parts = (['flipped over the $x$-axis'] if a_ < 0 else []) + ([f'{"right" if h_ > 0 else "left"} {abs(h_)}'] if h_ else []) + ([f'{"up" if k_ > 0 else "down"} {abs(k_)}'] if k_ else [])
    return ', '.join(parts[:-1]) + (' and ' if len(parts) > 1 else '') + parts[-1] if parts else 'not moved'


def deck_graphs():
    d = Deck('t-graphs', 'Graphs and Shifts', 'The basic graphs by sight, and what shifting, flipping and stretching do to them.', UNIT)
    d.keys = ['sqrt(', 'abs(']
    R = random.Random(707)
    par = {'sq': ('x^2', [-4, 4, -2, 8], -2.8, 2.8, '$x^2$'), 'cube': ('x^3', [-3, 3, -6, 6], -1.8, 1.8, '$x^3$'), 'root': ('sqrt(x)', [-2, 8, -2, 4], 0, 8, '$sqrt(x)$'),
           'abs': ('abs(x)', [-5, 5, -2, 6], -5, 5, '$|x|$'), 'line': ('x', [-5, 5, -5, 5], -5, 5, '$x$')}
    for k, (e_, w_, a_, b_, _) in par.items():
        d.graph(k, {'window': w_, 'pieces': [{'expr': e_, 'from': a_, 'to': b_}]})
    d.graph('recip', {'window': [-5, 5, -5, 5], 'pieces': [{'expr': '1/x', 'from': -5, 'to': -0.2}, {'expr': '1/x', 'from': 0.2, 'to': 5}]})
    names = {k: v[4] for k, v in par.items()}
    names['recip'] = '$frac{1}{x}$'
    L = [
        MC('L1', 'A handful of graphs come up all year. You should know each one on sight. Which function is this?', ['$sqrt(x)$', '$x^2$', '$|x|$', '$frac{1}{x}$'], graph='root',
           hint='It starts at the origin and only exists for $x >= 0$.', explain='$sqrt(x)$: it starts at $(0, 0)$, rises quickly, then flattens out.'),
        TRANSFORM('L2', 'The dashed curve is $f(x) = x^2$ moved **up 3**. Move your graph onto it, and watch the formula change as you go.', 'x^2', [-6, 6, -6, 6], {'h': 0, 'k': 3}, controls=['k'],
                  hint='Tap ↑ until your curve sits on the dashed one.', explain='Adding 3 **outside** the function raises every output by 3: $y = f(x) + 3$.'),
        TRANSFORM('L3', 'Now the dashed curve is $f(x) = x^2$ moved **right 2**. Move yours, and look closely at the sign in the formula.', 'x^2', [-6, 6, -6, 6], {'h': 2, 'k': 0}, controls=['h'],
                  hint='Tap → twice.', explain='Right 2 is $f(x - 2)$, with a **minus**. A change inside the parentheses acts on $x$, and it acts backwards.'),
        MC('L4', 'So the graph of $y = (x + 4)^2$ is the graph of $y = x^2$ moved', ['left 4', 'right 4', 'up 4', 'down 4'], fixed=True,
           hint='It is inside the parentheses, so it is sideways, and backwards.', explain='$(x + 4)^2$ is zero when $x = -4$, so the bottom of the parabola moved to $x = -4$: left 4.'),
        TRANSFORM('L5', 'A minus sign in front flips the graph over the $x$-axis. This target has been flipped **and** moved. Match it.', 'x^2', [-6, 6, -6, 6], {'h': 1, 'k': 4, 'a': -1},
                  controls=['h', 'k', 'flip'], hint='Flip first. Then find where the top of the dashed curve is.', explain='$y = -f(x - 1) + 4$: flipped, right 1, up 4.'),
        MC('L6', 'Now read it straight from a formula. $y = -sqrt(x - 3) + 1$ is the graph of $y = sqrt(x)$', ['flipped, moved right 3 and up 1', 'flipped, moved left 3 and up 1', 'moved right 3 and down 1', 'flipped, moved right 1 and up 3'],
           hint='Inside the root: sideways and backwards. Outside: up and down. In front: flip.', explain='$-$ in front: flipped. $x - 3$ inside: right 3. $+ 1$ outside: up 1.'),
    ]
    d.lesson(L)
    T = [
        MATCH('T1', 'Match each description to its function.', [['a U shape (a parabola)', '$x^2$'], ['a V shape', '$|x|$'], ['starts at the origin, rises, then flattens', '$sqrt(x)$'],
                                                               ['two separate branches that never touch the axes', '$frac{1}{x}$'], ['an S shape through the origin', '$x^3$']],
              explain='These five, plus straight lines, are the starting point for most graphs in this course.'),
        MC('T2', '$y = f(x) - 5$ moves the graph of $f$', ['down 5', 'up 5', 'left 5', 'right 5'], fixed=True, explain='Outside the function: it changes the outputs, so it is vertical, and it does what it says.'),
        MC('T3', '$y = f(x + 1)$ moves the graph of $f$', ['left 1', 'right 1', 'up 1', 'down 1'], fixed=True, explain='Inside the function: sideways, and backwards from what the sign suggests.'),
        MC('T4', '$y = -f(x)$', ['flips the graph over the $x$-axis', 'flips the graph over the $y$-axis', 'moves the graph down', 'does not change the graph'], explain='Every height becomes its opposite, so the picture turns upside down.'),
        MC('T5', '$y = 2f(x)$', ['doubles every height (a vertical stretch)', 'moves the graph up 2', 'moves the graph right 2', 'makes the graph twice as wide'], explain='Each output is multiplied by 2. Points on the $x$-axis stay put.'),
        TF('T6', 'The lowest point of $y = (x - 3)^2 + 2$ is at $(3, 2)$.', True, explain='$y = x^2$ has its lowest point at $(0, 0)$. Right 3 and up 2 moves it to $(3, 2)$.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for k in ['sq', 'cube', 'root', 'abs', 'line', 'recip']:
        others = [names[j] for j in names if j != k]
        Q.append(MC(d.qid('P'), 'Which function is this?', [names[k]] + R.sample(others, 3), graph=k, level=1, explain=f'This is the graph of {names[k]}.'))
    combos = [('x^2', 2, 3), ('x^2', -1, -4), ('abs(x)', 3, 0), ('sqrt(x)', -2, 1), ('x^3', 0, -2), ('x^2', -3, 2), ('abs(x)', -2, -3), ('sqrt(x)', 4, 0), ('x^3', 1, 1), ('abs(x)', 0, 4)]
    for base, h_, k_ in combos:
        right = move_words(h_, k_)
        wrong = pick_unique([move_words(-h_, k_) if h_ else move_words(k_, 0), move_words(k_, h_) if (h_ and k_ and abs(h_) != abs(k_)) else move_words(h_, -k_) if k_ else move_words(0, h_),
                             move_words(-h_, -k_) if (h_ and k_) else move_words(0, -h_) if h_ else move_words(-k_, 0), move_words(h_ + 1, k_), move_words(h_, k_ + 1)])
        wrong = [w for w in wrong if w != right][:3]
        Q.append(MC(d.qid('W'), f'The graph of $y = {disp(shifted(base, h_, k_))}$ is the graph of $y = {BASES[base][1]}$ moved', [right] + wrong, level=1,
                    explain='Inside the function: sideways and backwards. Outside: up or down, as written.'))
    tf = [('x^2', 2, 3), ('x^2', -3, -2), ('abs(x)', 1, -3), ('abs(x)', -2, 2), ('sqrt(x)', -3, 1), ('sqrt(x)', 2, -2), ('x^3', 1, 2), ('x^3', -2, -1), ('x^2', 0, -4), ('abs(x)', 3, 0),
          ('sqrt(x)', -4, -3), ('x^2', 4, 1), ('x^3', 0, 3), ('abs(x)', -3, -1), ('x^2', -2, 4), ('sqrt(x)', 1, 2)]
    for base, h_, k_ in tf:
        Q.append(TRANSFORM(d.qid('T'), f'Here $f(x) = {BASES[base][1]}$. Move your graph onto the dashed target.', base, BASES[base][0], {'h': h_, 'k': k_}, level=2,
                           explain=f'The target is $y = {disp(shifted(base, h_, k_))}$: {move_words(h_, k_)}.'))
    for n_, (base, h_, k_) in enumerate([('x^2', 2, 1), ('x^2', -1, -3), ('abs(x)', 2, -2), ('sqrt(x)', -3, 0), ('abs(x)', -1, 2), ('sqrt(x)', 1, 1)]):
        w_ = BASES[base][0]
        f = shifted(base, h_, k_)
        gname = f'S{n_ + 1}'
        lo = max(w_[0], h_) if base == 'sqrt(x)' else w_[0]
        d.graph(gname, {'window': w_, 'pieces': [{'expr': f.replace('abs', 'abs').replace(')^2', ')^2'), 'from': lo, 'to': w_[1]}]})
        q = E(d, d.qid('F'), f'This is the graph of $y = {BASES[base][1]}$, moved. Write its formula.', f, S(f), label='$y$ =', level=2, ranges={'x': [max(h_, 0) + 0.5, max(h_, 0) + 3]},
              explain=f'It was moved {move_words(h_, k_)}: $y = {disp(f)}$.')
        q['graph'] = gname
        Q.append(q)
    hard = [('x^2', 1, 4, -1), ('x^2', -2, 3, -1), ('abs(x)', 2, 3, -1), ('sqrt(x)', -3, 2, -1), ('x^2', 0, -4, 2), ('abs(x)', -1, -3, 2), ('x^3', 1, 0, -1), ('x^2', 2, 5, -2)]
    for base, h_, k_, a_ in hard:
        ctl = ['h', 'k'] + (['flip'] if a_ < 0 else []) + (['stretch'] if abs(a_) != 1 else [])
        Q.append(TRANSFORM(d.qid('H'), f'Here $f(x) = {BASES[base][1]}$. This target has been ' + ('flipped' if a_ < 0 else '') + (' and ' if a_ < 0 and abs(a_) != 1 else '') + ('stretched' if abs(a_) != 1 else '') +
                           ' as well as moved. Match it.', base, BASES[base][0], {'h': h_, 'k': k_, 'a': a_}, controls=ctl, level=3,
                           explain=f'The target is $y = {disp(shifted(base, h_, k_, a_))}$.'))
    for f, pt, wr, what in [('(x + 1)^2 - 4', '(-1, -4)', ['(1, -4)', '(-1, 4)', '(-4, -1)'], 'lowest point'), ('(x - 5)^2 + 2', '(5, 2)', ['(-5, 2)', '(5, -2)', '(2, 5)'], 'lowest point'),
                            ('-(x - 2)^2 + 6', '(2, 6)', ['(-2, 6)', '(2, -6)', '(6, 2)'], 'highest point'), ('sqrt(x - 3) + 1', '(3, 1)', ['(-3, 1)', '(3, -1)', '(1, 3)'], 'starting point'),
                            ('abs(x + 4)', '(-4, 0)', ['(4, 0)', '(0, -4)', '(0, 4)'], 'corner'), ('sqrt(x + 2) - 5', '(-2, -5)', ['(2, -5)', '(-2, 5)', '(-5, -2)'], 'starting point')]:
        Q.append(MC(d.qid('V'), f'Without graphing: where is the {what} of $y = {disp(f)}$?', [f'${pt}$'] + [f'${w}$' for w in wr], level=3,
                    explain=f'The basic graph has that point at the origin. The shifts move it to ${pt}$.'))
    d.drill('practice', 'Practice', Q, 'pool', setSize=10)
    save_graphs(d)


# ====================================================================== 8. Composition
def deck_compose():
    d = Deck('t-compose', 'Composition', 'Functions inside functions: building them and taking them apart.', UNIT)
    d.keys = ['sqrt(', 'sin(', 'cos(', 'e^(', 'ln(']
    q2 = E(d, 'L2', box('f(x) = x^2,    g(x) = x + 3') + 'As a formula, $f(g(x))$ puts **all** of $g(x)$ into the blank of $f$. Type what goes in the blank.', 'x + 3', x + 3, label='In the blank:', keys=[],
           hint='The blank gets the whole formula for $g(x)$.', explain='$f(g(x)) = (x + 3)^2$')
    q2['template'] = 'f(g(x)) = ([])^2'
    L = [
        N('L1', '$f(g(x))$ means: do $g$ first, then put its answer into $f$.' + box('g(2) = 5,    f(5) = 11') + 'What is $f(g(2))$?', 11, label='$f(g(2))$ =',
          hint='Inside first: $g(2) = 5$. Then $f(5)$.', explain='$f(g(2)) = f(5) = 11$. Always work from the inside out.'),
        q2,
        MC('L3', 'Order matters. With the same $f(x) = x^2$ and $g(x) = x + 3$, what is $g(f(x))$?', ['$x^2 + 3$', '$(x + 3)^2$', '$x^2 + 6x + 9$', '$3x^2$'],
           hint='Now $f(x)$ goes into the blank of $g$.', explain='$g(f(x)) = x^2 + 3$, which is not $(x + 3)^2$. Swapping the order changes the function.'),
        MC('L4', 'Now run it backwards, which is what the chain rule will ask of you.' + box('h(x) = sqrt(x^2 + 1)') + 'If you plugged in a number, what would you compute **first**? That part is the inside function.',
           ['$x^2 + 1$', '$sqrt(x)$', '$x^2$', '$x + 1$'], hint='You cannot take the square root until you know what is under it.', explain='Inside: $x^2 + 1$. It gets computed first, then handed to the square root.'),
        E(d, 'L5', 'The outside function is what you do **last**. Call the inside $u = x^2 + 1$. Write the outside as a function of $u$.', 'sqrt(u)', sp.sqrt(u), ['u'], label='$f(u)$ =', keys=['sqrt('],
          hint='Once you have $u$, all that is left is to take its square root.', explain='$h(x) = f(g(x))$ with inside $g(x) = x^2 + 1$ and outside $f(u) = sqrt(u)$. Seeing these two layers is the whole chain rule.'),
    ]
    d.lesson(L)
    T = [
        TF('T1', '$f(g(x))$ and $g(f(x))$ are always the same function.', False, explain='With $f(x) = x^2$ and $g(x) = x + 3$: $(x + 3)^2$ and $x^2 + 3$ are different.'),
        TF('T2', '$f(g(x))$ means $f(x) · g(x)$.', False, explain='It is not multiplication. $g(x)$ is the **input** of $f$.'),
        MC('T3', 'The inside function of $(3x - 1)^5$ is', ['$3x - 1$', '$x^5$', '$3x$', '$5x$'], explain='You compute $3x - 1$ first, then raise it to the 5th power.'),
        MC('T4', 'The inside function of $e^(x^2)$ is', ['$x^2$', '$e^x$', '$e^2$', '$2x$'], explain='You square $x$ first, then use it as the exponent.'),
        MC('T5', '$sin^2(x)$ means $(sin(x))^2$. Its inside function is', ['$sin(x)$', '$x^2$', '$2x$', '$sin(x^2)$'], explain='Take the sine first, then square the result. The outside is $u^2$.'),
        MC('T6', 'The **outside** function of $ln(4x + 1)$ is', ['$ln(u)$', '$4u + 1$', '$4x$', '$u^4$'], explain='The last thing you do is take the logarithm.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    pairs = [('x^2', 'x + 3'), ('2x + 1', 'x^2'), ('sqrt(x)', 'x + 7'), ('x^3', 'x - 1'), ('1/x', 'x + 2'), ('x^2 - 1', '3x')]
    for f, g in pairs:
        for a0, order in [(2, 'fg'), (1, 'gf')]:
            fo, gi = (f, g) if order == 'fg' else (g, f)
            inner = S(gi).subs(x, a0)
            v = S(fo).subs(x, inner)
            nm = ('f', 'g') if order == 'fg' else ('g', 'f')
            Q.append(N(d.qid('N'), box(f'f(x) = {disp(f)},    g(x) = {disp(g)}') + f'Find ${nm[0]}({nm[1]}({a0}))$.', v, label=f'${nm[0]}({nm[1]}({a0}))$ =', level=1,
                       explain=f'Inside first: ${nm[1]}({a0}) = {D(frac_str(inner))}$. Then ${nm[0]}({D(frac_str(inner))}) = {D(frac_str(v))}$.'))
    hs = [('(3x^2 + 1)^10', '3x^2 + 1', 'u^10', '(3x^2 + 1)^10'), ('sin(x^2)', 'x^2', 'sin(u)', 'sin(x^2)'), ('sqrt(1 - x^2)', '1 - x^2', 'sqrt(u)', 'sqrt(1 - x^2)'), ('e^(5x)', '5x', 'e^u', 'e^(5x)'),
          ('ln(x^2 + 4)', 'x^2 + 4', 'ln(u)', 'ln(x^2 + 4)'), ('cos(x)^3', 'cos(x)', 'u^3', 'cos^3(x)'), ('1/(2x + 7)', '2x + 7', '1/u', 'frac{1}{2x + 7}'), ('(x^3 - x)^4', 'x^3 - x', 'u^4', '(x^3 - x)^4'),
          ('sin(3x)', '3x', 'sin(u)', 'sin(3x)'), ('sqrt(sin(x))', 'sin(x)', 'sqrt(u)', 'sqrt(sin(x))'), ('e^(sin(x))', 'sin(x)', 'e^u', 'e^(sin(x))'), ('(1 + sqrt(x))^6', '1 + sqrt(x)', 'u^6', '(1 + sqrt(x))^6')]
    for app, ins, out, show in hs:
        assert sp.simplify(S(out).subs(u, S(ins)) - S(app)) == 0, app
        Q.append(E(d, d.qid('I'), box(f'h(x) = {show}') + 'What is the **inside** function, the part you would compute first?', ins, S(ins), label='inside =', level=1, ranges={'x': [0.3, 0.9]},
                   explain=f'You compute ${D(ins)}$ first. The outside is ${D(out)}$.'))
    for f, g in [('x^2', 'x + 3'), ('sqrt(x)', 'x^2 + 1'), ('2x + 1', 'x^2'), ('1/x', 'x - 4'), ('x^3', '2x'), ('sin(x)', '3x'), ('e^x', 'x^2'), ('x^2 + x', 'x - 1')]:
        for order in ('fg', 'gf'):
            fo, gi = (f, g) if order == 'fg' else (g, f)
            nm = ('f', 'g') if order == 'fg' else ('g', 'f')
            truth = S(fo).subs(x, S(gi))
            ans = sp_app(truth)
            Q.append(E(d, d.qid('C'), box(f'f(x) = {disp(f)},    g(x) = {disp(g)}') + f'Write a formula for ${nm[0]}({nm[1]}(x))$.', ans, truth, label=f'${nm[0]}({nm[1]}(x))$ =', level=2,
                       ranges={'x': [4.3, 5.6]}, explain=f'Put ${D(gi)}$ into every blank of ${nm[0]}$: ${D(ans)}$.'))
    for app, ins, out, show in hs[:8]:
        Q.append(E(d, d.qid('O'), box(f'h(x) = {show}') + f'The inside is $u = {D(ins)}$. Write the **outside** function in terms of $u$.', out, S(out), ['u'], label='$f(u)$ =', level=2,
                   ranges={'u': [0.3, 0.9]}, explain=f'Once you have $u$, the last step is ${D(out)}$.'))
    two = [('sqrt(x^2 + 9)', 'x^2 + 9', 'sqrt(u)', 'sqrt(x^2 + 9)'), ('(5x - 2)^7', '5x - 2', 'u^7', '(5x - 2)^7'), ('cos(x^3)', 'x^3', 'cos(u)', 'cos(x^3)'), ('e^(-x^2)', '-x^2', 'e^u', 'e^(-x^2)'),
           ('ln(sin(x))', 'sin(x)', 'ln(u)', 'ln(sin(x))'), ('sin(x)^4', 'sin(x)', 'u^4', 'sin^4(x)'), ('1/(x^2 + 1)^3', 'x^2 + 1', '1/u^3', 'frac{1}{(x^2 + 1)^3}'), ('sqrt(e^x + 1)', 'e^x + 1', 'sqrt(u)', 'sqrt(e^x + 1)')]
    for app, ins, out, show in two:
        assert sp.simplify(S(out).subs(u, S(ins)) - S(app)) == 0, app
        qid = d.qid('D')
        st = [E(d, qid + '.1', 'The inside: what gets computed first?', ins, S(ins), label='$u$ =', ranges={'x': [0.3, 0.9]}, work=f'inside: $u = {D(ins)}$'),
              E(d, qid + '.2', 'The outside: what is done to $u$ last?', out, S(out), ['u'], label='$f(u)$ =', ranges={'u': [0.3, 0.9]}, work=f'outside: $f(u) = {D(out)}$')]
        Q.append(STEPS(qid, 'Take this function apart into an inside and an outside.' + box(f'h(x) = {show}'), st, level=3, explain=f'Inside $u = {D(ins)}$, outside $f(u) = {D(out)}$.'))
    for show, layers, ex in [('sin((2x + 1)^3)', 3, '$2x + 1$, then cube it, then take the sine.'), ('sqrt(1 + e^(2x))', 3, '$2x$, then $e$ to that power (plus 1), then the square root.'),
                             ('(x^2 + 1)^5', 2, '$x^2 + 1$, then the 5th power.'), ('ln(cos(x^2))', 3, '$x^2$, then cosine, then the logarithm.')]:
        Q.append(MC(d.qid('L'), box(f'h(x) = {show}') + 'How many layers does this function have? Count the steps you would do in order.', [str(layers)] + [str(v) for v in (1, 2, 3, 4) if v != layers], level=3,
                    explain='In order: ' + ex))
    d.drill('practice', 'Practice', Q, 'pool', setSize=10)
    d.save()


DECKS = {'t-exponents': deck_exponents, 't-radicals': deck_radicals, 't-graphs': deck_graphs, 't-compose': deck_compose}
