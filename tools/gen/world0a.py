"""World 0 (The Toolkit), part A: the stops for class days 1 to 3.
   t-notation  Function Notation          t-domain   Domain and Piecewise Functions
   t-factor    Factoring                  t-rational Rational Expressions
   t-exponents Exponent Rules             t-radicals Radicals and Conjugates
Run from world0.py. See lib.py before re-running: it overwrites decks."""
import random, re, json, os, subprocess
import sympy as sp
from lib import *

UNIT = 'The Toolkit'


def disp(f):
    """app syntax -> math markup, with |x| for abs()"""
    return re.sub(r'abs\(([^()]*)\)', r'|\1|', D(f))


def Dsum(s):
    """like D(), but every term of a sum gets its own stacked fraction: 1/x - 1/3"""
    idx = [i for i in _top0(s) if i > 0]
    if not idx:
        return D(s)
    out, last = [], 0
    for i in idx:
        out.append(D(s[last:i].strip()))
        out.append(s[i])
        last = i + 1
    out.append(D(s[last:].strip()))
    return ' '.join(out)


def _top0(s):
    d, out = 0, []
    for i, c in enumerate(s):
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
        elif d == 0 and c in '+-' and i > 0 and s[i - 1] == ' ':
            out.append(i)
    return out


def xh(e):
    """a polynomial in x and h in app syntax, highest total degree first: x^2 + 2xh + h^2 - 3x - 3h"""
    P_ = sp.Poly(sp.expand(e), x, h)
    terms = sorted(P_.terms(), key=lambda t_: (-(t_[0][0] + t_[0][1]), -t_[0][0]))
    out = ''
    for (i, j), c in terms:
        c = sp.nsimplify(c)
        body = ('x' if i == 1 else f'x^{i}' if i else '') + ('h' if j == 1 else f'h^{j}' if j else '')
        a_ = abs(c)
        cs = '' if (a_ == 1 and body) else frac_str(a_)
        out += (' - ' if c < 0 else ' + ') + cs + body
    out = out.strip()
    return ('-' + out[2:]) if out.startswith('- ') else out[2:] if out.startswith('+ ') else out or '0'


def sub_in(f, a0):
    """f with every x replaced by (a0), for showing the substitution"""
    return re.sub(r'(?<![a-z])x(?![a-z])', f'({a0})', f)


def graphtruth(deck_id):
    subprocess.run(['node', os.path.join(ROOT, 'tools', 'gen', 'graphtruth.js'), os.path.join(ROOT, 'decks', deck_id + '.json')], check=True)


def save_graphs(d):
    d.save()
    graphtruth(d.id)


# ====================================================================== 1. Function Notation
def deck_notation():
    d = Deck('t-notation', 'Function Notation', 'What f( ) means, and how to put anything inside it.', UNIT)
    tmpl = 'f([]) = ([])^2 - 3([])'
    q1 = E(d, 'L1', box('f(x) = x^2 - 3x') + 'A function is a rule with blanks in it. Whatever you put inside $f( )$ goes into **every** blank.\nPut 5 in and watch.',
           '5', sp.Integer(5), [], label='Input:', hint='Type 5.', explain='$f(5) = (5)^2 - 3(5) = 10$. One input, and it lands in every blank.')
    q1['template'] = tmpl
    q3 = E(d, 'L3', box('f(x) = x^2 - 3x') + 'The input does not have to be a number. Put $x + h$ into the blanks.',
           'x + h', x + h, ['x', 'h'], label='Input:', hint='Type x + h. The rule does not change, only what sits in the blanks.',
           explain='$f(x + h) = (x + h)^2 - 3(x + h)$. Nothing else about the rule changed.')
    q3['template'] = tmpl
    L = [
        q1,
        N('L2', 'A negative input needs its parentheses.' + box('f(-2) = (-2)^2 - 3(-2)') + 'What number is that?', 10, label='$f(-2)$ =',
          hint='$(-2)^2 = 4$ and $-3(-2) = +6$.', explain='$4 + 6 = 10$. Without the parentheses, $-2^2$ would have been $-4$.'),
        q3,
        MC('L4', 'To finish, you have to multiply out $(x + h)^2$. Which is it?', ['$x^2 + 2xh + h^2$', '$x^2 + h^2$', '$x^2 + xh + h^2$', '$2x + 2h$'],
           hint='Write it as $(x + h)(x + h)$ and multiply all four pairs.', explain='$(x + h)(x + h) = x^2 + xh + hx + h^2$. The middle term $2xh$ is the one that goes missing.'),
        E(d, 'L5', 'Now multiply out the whole thing.' + box('f(x + h) = (x + h)^2 - 3(x + h)'), 'x^2 + 2xh + h^2 - 3x - 3h', sp.expand((x + h) ** 2 - 3 * (x + h)), ['x', 'h'],
          label='$f(x + h)$ =', hint='$(x + h)^2 = x^2 + 2xh + h^2$, and $-3(x + h) = -3x - 3h$.',
          explain='This is the first move of every derivative you will compute in this course.'),
    ]
    d.lesson(L)
    T = [
        MC('T1', '$f(3) = 7$ means', ['the input 3 gives the output 7', '$f$ times 3 equals 7', 'the input 7 gives the output 3', '$x$ is both 3 and 7'],
           explain='$f(3)$ is read "f of 3". It is the output when the input is 3. It is never multiplication.'),
        MC('T2', box('f(x) = x^2') + 'What is $f(-3)$?', ['9', '−9', '6', '−6'], explain='$f(-3) = (-3)^2 = 9$. The parentheses make the minus sign part of what gets squared.'),
        MC('T3', box('f(x) = 2x + 1') + 'Which is $f(x + h)$?', ['$2(x + h) + 1$', '$2x + h + 1$', '$2x + 1 + h$', '$(2x + 1)(x + h)$'],
           explain='Replace the $x$ with $(x + h)$, parentheses and all: $2(x + h) + 1 = 2x + 2h + 1$.'),
        TF('T4', 'For every function, $f(x + h) = f(x) + f(h)$.', False, explain='Try $f(x) = x^2$: $(x + h)^2 = x^2 + 2xh + h^2$, which is not $x^2 + h^2$. A function does not "distribute".'),
        MC('T5', box('f(x) = x^2') + 'What is $f(2x)$?', ['$4x^2$', '$2x^2$', '$2x$', '$x^4$'], explain='$f(2x) = (2x)^2 = 4x^2$. The 2 is inside the blank, so it gets squared too.'),
        TF('T6', '$f(x) = 5$ is a constant function. So $f(x + h) = 5 + h$.', False, explain='The rule has no blank to fill: every input gives 5. So $f(x + h) = 5$.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for f, a0 in [('x^2 - 3x', -2), ('2x^2 + x', -3), ('5 - x^2', -3), ('x^3 - x', -2), ('-x^2', 4), ('(x - 1)(x + 5)', 3), ('x^2 + 4x + 4', -2), ('3x^4', -1),
                  ('4x - x^3', -2), ('7', 100), ('x^2 - x', -1), ('1 - 2x', -5)]:
        v = S(f).subs(x, a0)
        Q.append(N(d.qid('P'), box(f'f(x) = {disp(f)}') + f'Find $f({a0})$.', v, label=f'$f({a0})$ =', level=1,
                   explain=(f'$f({a0}) = {disp(sub_in(f, a0))} = {frac_str(v)}$' if 'x' in f else f'Every input gives {frac_str(v)}.')))
    for f, a0 in [('(x + 1)/(x - 2)', 4), ('x^2/(x + 3)', -1), ('sqrt(x + 7)', 9), ('1/x + x', 2), ('sqrt(25 - x^2)', 3), ('(2x - 1)/(x^2 + 1)', 1), ('abs(x - 5)', 2)]:
        v = S(f).subs(x, a0)
        Q.append(N(d.qid('R'), box(f'f(x) = {disp(f) if "+ x" not in f else Dsum(f)}') + f'Find $f({a0})$.', v, label=f'$f({a0})$ =', level=1, explain=f'$f({a0}) = {D(frac_str(v))}$'))
    pw = [(('x + 1', 'x < 2', 'x^2', 'x >= 2'), sp.Piecewise((x + 1, x < 2), (x ** 2, True)), [2, 1, -3]),
          (('3 - x', 'x < 0', '2x', 'x >= 0'), sp.Piecewise((3 - x, x < 0), (2 * x, True)), [0, -4, 3]),
          (('x^2', 'x < 3', '10 - x', 'x >= 3'), sp.Piecewise((x ** 2, x < 3), (10 - x, True)), [3, 5])]
    for rows, fx, pts in pw:
        for a0 in pts:
            v = fx.subs(x, a0)
            k = 0 if sp.sympify(rows[1].replace('x', str(a0)).replace('>=', '>=')) == True else 2  # noqa: E712
            Q.append(N(d.qid('W'), box('f(x) = ' + cases(*rows)) + f'Find $f({a0})$.', v, label=f'$f({a0})$ =', level=1,
                       explain=f'${rows[k + 1].replace("x", str(a0))}$ is true, so use ${rows[k]}$: {frac_str(v)}.'))
    comp = [('x^2', '2x', '4x^2'), ('x^2', 'x + 1', 'x^2 + 2x + 1'), ('3x - 2', 'x + 4', '3x + 10'), ('x^2 + x', '-x', 'x^2 - x'), ('2x + 5', 'a', '2a + 5'),
            ('x^2 - 1', 'x^2', 'x^4 - 1'), ('1/x', 'x + h', '1/(x + h)'), ('sqrt(x)', 'x + h', 'sqrt(x + h)'), ('5', 'x + h', '5'), ('x^3', '2x', '8x^3'),
            ('x^2 + 3', 'x - 1', 'x^2 - 2x + 4'), ('4 - x', 'x + h', '4 - x - h'), ('x^2', '-x', 'x^2'), ('2x^2', '3x', '18x^2')]
    for f, inp, ans in comp:
        vars_ = sorted({c for c in inp + ans if c in 'xha'}, key='xha'.index) or ['x']
        truth = S(f).subs(x, S(inp))
        Q.append(E(d, d.qid('C'), box(f'f(x) = {disp(f)}') + f'Find $f({D(inp)})$. Simplify if you can.', ans, truth, vars_, label=f'$f({D(inp)})$ =', level=2,
                   explain=f'Put $({D(inp)})$ in every blank: $f({D(inp)}) = {D(ans)}$.'))
    for f in ['x^2', '3x + 2', 'x^2 + x', '2x^2', 'x^2 - 4x', '1 - x^2', 'x^2 + 2x + 1', '5x']:
        truth = sp.expand(S(f).subs(x, x + h))
        Q.append(E(d, d.qid('H'), box(f'f(x) = {disp(f)}') + 'Find $f(x + h)$ and multiply it out.', xh(truth), truth, ['x', 'h'], label='$f(x + h)$ =', level=2,
                   explain=f'$f(x + h) = {D(sub_in(f, "x + h"))} = {D(xh(truth))}$'))
    for f in ['x^2', '3x + 2', 'x^2 + x', '2x^2', 'x^2 - 4x', '1 - x^2', '5x - 1', 'x^2 + 3']:
        f0 = S(f)
        a1 = sp.expand(f0.subs(x, x + h))
        a2 = sp.expand(a1 - f0)
        a3 = sp.expand(a2 / h)
        qid = d.qid('Q')
        st = [E(d, qid + '.1', 'First $f(x + h)$, multiplied out.', xh(a1), a1, ['x', 'h'], label='$f(x + h)$ =', work=f'$f(x + h) = {D(xh(a1))}$'),
              ES(d, qid + '.2', 'Subtract $f(x)$. A lot should cancel.', xh(a2), a2, original=xh(a1) + ' - (' + f + ')', vars_=['x', 'h'], label='$f(x + h) - f(x)$ =',
                 work=f'$f(x + h) - f(x) = {D(xh(a2))}$', explain='Every term without an $h$ cancels. That always happens.'),
              ES(d, qid + '.3', 'Divide by $h$.', xh(a3), a3, original='(' + xh(a2) + ')/h', slack=1 if cx(xh(a2)) - cx(xh(a3)) < 4 else 2, vars_=['x', 'h'],
                 label='$frac{f(x + h) - f(x)}{h}$ =', work=f'$frac{{f(x + h) - f(x)}}{{h}} = {D(xh(a3))}$', explain='Every term had an $h$, so the $h$ divides out.')]
        Q.append(STEPS(qid, box(f'f(x) = {disp(f)}') + 'Build the **difference quotient** $frac{f(x + h) - f(x)}{h}$ one piece at a time.', st, level=3,
                       explain=f'$frac{{f(x + h) - f(x)}}{{h}} = {D(xh(a3))}$'))
    d.drill('practice', 'Practice', Q, 'pool', setSize=10)
    d.save()


# ====================================================================== 2. Domain and Piecewise Functions
def deck_domain():
    d = Deck('t-domain', 'Domain and Piecewise Functions', 'Which inputs a function accepts, and functions with more than one rule.', UNIT)
    d.graph('pw', {'window': [-4, 5, -2, 6], 'pieces': [{'expr': 'x+3', 'from': -4, 'to': 1}, {'expr': '5-x', 'from': 1, 'to': 5}], 'holes': [[1, 4]], 'dots': [[1, 2]]})
    d.graph('pw2', {'window': [-4, 4, -3, 5], 'pieces': [{'expr': '1-x', 'from': -4, 'to': -1}, {'expr': 'x^2-1', 'from': -1, 'to': 2}, {'expr': '4', 'from': 2, 'to': 4}],
                    'holes': [[-1, 2], [2, 3]], 'dots': [[-1, 0], [2, 4]]})
    L = [
        MC('L1', 'The **domain** of a function is every input it accepts. A formula refuses an input when it would have to divide by zero.' + box('f(x) = frac{1}{x - 4}') + 'Which input does this one refuse?',
           ['4', '0', '−4', '1'], hint='Which $x$ makes the bottom equal 0?', explain='At $x = 4$ the bottom is 0, so $f(4)$ is undefined. Every other number is fine.'),
        INTERVAL('L2', 'So the domain of $frac{1}{x - 4}$ is every number except 4. Write that in interval notation.', '(-inf,4)U(4,inf)',
                 hint='Everything below 4, joined to everything above 4: $(-∞, 4) ∪ (4, ∞)$.', explain='Round brackets, because 4 itself is left out.'),
        MC('L3', 'The other thing a formula refuses: the square root of a negative number.' + box('g(x) = sqrt(x - 3)') + 'Which inputs are allowed?',
           ['$x >= 3$', '$x > 3$', '$x <= 3$', 'every number'], hint='The inside, $x - 3$, must be 0 or more.', explain='$x - 3 >= 0$ means $x >= 3$. Zero inside a square root is fine: $sqrt(0) = 0$.'),
        INTERVAL('L4', 'Write the domain of $sqrt(x - 3)$ in interval notation.', '[3,inf)', hint='It starts at 3, and 3 is included, so use a square bracket: $[3, ∞)$.',
                 explain='A square bracket means the endpoint is included. Infinity always gets a round bracket.'),
        N('L5', 'A **piecewise** function has more than one rule. The condition on the right says which rule to use.' + box('f(x) = ' + cases('x + 1', 'x < 2', 'x^2', 'x >= 2')) + 'Find $f(2)$.',
          4, label='$f(2)$ =', hint='Is $2 < 2$, or is $2 >= 2$?', explain='$2 >= 2$ is the true one, so use $x^2$: $f(2) = 4$. Only one rule ever applies.'),
        GRAPHQ('L6', 'pw', 'value', 1, text='On a graph, a filled dot is the value and an open circle is a gap. Find $f(1)$.',
               hint='Two things happen at $x = 1$. Only the filled dot counts.', explain='The filled dot is at height 2, so $f(1) = 2$. The open circle at height 4 is where the graph was heading.'),
    ]
    d.lesson(L)
    T = [
        PICK('T1', 'Which of these can make an input illegal? Select all that apply.', ['dividing by zero', 'the square root of a negative number', 'squaring a negative number', 'multiplying by zero'], [0, 1],
             explain='For now those are the only two. (Logarithms add a third one later: the log of zero or a negative.)'),
        MC('T2', 'What is the domain of $frac{1}{x^2 + 1}$?', ['every real number', 'every number except 1', 'every number except −1', '$x > 0$'],
           explain='$x^2 + 1$ is at least 1, so the bottom is never 0. Nothing is refused.'),
        TF('T3', '0 is in the domain of $sqrt(x)$.', True, explain='$sqrt(0) = 0$. Only negatives are refused.'),
        MC('T4', box('f(x) = ' + cases('3 - x', 'x < 0', '2x', 'x >= 0')) + 'Which rule gives $f(0)$?', ['$2x$', '$3 - x$', 'both', 'neither'], fixed=True,
           explain='$0 >= 0$ is true and $0 < 0$ is false, so the second rule: $f(0) = 0$.'),
        MC('T5', 'In interval notation, $x >= 3$ is', ['$[3, ∞)$', '$(3, ∞)$', '$(-∞, 3]$', '$[3, ∞]$'], explain='The square bracket includes 3. Infinity is not a number, so it never gets a square bracket.'),
        MC('T6', 'What is the domain of $frac{sqrt(x)}{x - 5}$?', ['$[0, 5) ∪ (5, ∞)$', '$[0, ∞)$', '$(-∞, 5) ∪ (5, ∞)$', '$(5, ∞)$'],
           explain='Both rules at once: $x >= 0$ for the square root, and $x ≠ 5$ for the bottom.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for f in ['1/(x - 4)', '3/(x + 2)', 'x/(x^2 - 9)', '1/(x(x - 5))', '(x + 1)/(x^2 + 1)', '2/(x^2 - 5x + 6)', '5/(2x - 1)', '(x - 1)/(x^2 + 4x)']:
        den = sp.denom(sp.together(S(f)))
        zs = sorted(sp.solveset(den, x, sp.S.Reals))
        Q.append(CRIT(d.qid('Z'), box(f'f(x) = {D(f)}') + 'Which inputs make the bottom zero? List every one.', zs, 'bottom is 0 at $x$ =', noneText='The bottom is never 0', level=1,
                      explain=('The bottom is 0 at $x = ' + '$ and $x = '.join(frac_str(z) for z in zs) + '$.' if zs else 'The bottom is always positive, so no input is refused.')))
    for ineq, iv in [('x >= 3', '[3,inf)'), ('x > -2', '(-2,inf)'), ('x < 5', '(-inf,5)'), ('x <= 0', '(-inf,0]'), ('x != 4', '(-inf,4)U(4,inf)'), ('-1 < x <= 2', '(-1,2]')]:
        Q.append(INTERVAL(d.qid('I'), f'Write ${ineq}$ in interval notation.', iv, label='Interval:', level=1, explain='Square bracket = included. Round bracket = left out. Infinity is always round.'))
    why = {'/': 'The bottom cannot be 0.', 's': 'The inside of the square root must be 0 or more.', 'b': 'The inside of the root must be positive: 0 or more for the root, and not 0 because it is on the bottom.',
           'n': 'Nothing is refused: no division and no roots.', 'p': 'The bottom is never 0, so nothing is refused.'}
    for f, k in [('1/(x - 4)', '/'), ('3/(x + 2)', '/'), ('1/(x^2 - 9)', '/'), ('1/(x(x - 5))', '/'), ('sqrt(x - 3)', 's'), ('sqrt(x + 5)', 's'), ('sqrt(4 - x)', 's'), ('sqrt(2x - 6)', 's'),
                 ('1/sqrt(x - 1)', 'b'), ('x^2 - 3x', 'n'), ('(x + 1)/(x^2 + 1)', 'p'), ('2/(x^2 - 5x + 6)', '/'), ('sqrt(10 - 2x)', 's'), ('5/(2x - 1)', '/'), ('1/sqrt(x + 2)', 'b')]:
        Q.append(INTERVAL(d.qid('D'), f'Find the domain of $f(x) = {D(f)}$.', domain_of(S(f)), level=2, explain=why[k]))
    pw = [(('x + 1', 'x < 2', 'x^2', 'x >= 2'), sp.Piecewise((x + 1, x < 2), (x ** 2, True)), [2, 0, 5]),
          (('-x', 'x <= -1', 'x + 4', 'x > -1'), sp.Piecewise((-x, x <= -1), (x + 4, True)), [-1, 0, -3]),
          (('2', 'x < 0', 'x + 2', '0 <= x < 3', 'x^2 - 4', 'x >= 3'), sp.Piecewise((2, x < 0), (x + 2, x < 3), (x ** 2 - 4, True)), [-5, 0, 3, 2])]
    for rows, fx, pts in pw:
        for a0 in pts:
            v = fx.subs(x, a0)
            Q.append(N(d.qid('W'), box('f(x) = ' + cases(*rows)) + f'Find $f({a0})$.', v, label=f'$f({a0})$ =', level=2, explain=f'Check each condition with $x = {a0}$. Only one is true, and its rule gives {frac_str(v)}.'))
    for g, pts in [('pw', [-2, 0, 1, 3]), ('pw2', [-1, 2, 0, -3, 3])]:
        for a0 in pts:
            Q.append(GRAPHQ(d.qid('G'), g, 'value', a0, level=2, explain='Read the height of the graph at that $x$. Where there is a filled dot, the dot is the value.'))
    for f, ex in [('sqrt(x)/(x - 5)', 'Two rules at once: $x >= 0$ and $x ≠ 5$.'), ('1/(sqrt(x) - 2)', '$x >= 0$ for the root, and $sqrt(x) ≠ 2$ means $x ≠ 4$.'),
                  ('sqrt(x^2 - 4)', '$x^2 - 4 >= 0$ when $x <= -2$ or $x >= 2$.'), ('sqrt(9 - x^2)', '$9 - x^2 >= 0$ when $x$ is between −3 and 3.'),
                  ('sqrt(x + 3)/(x - 1)', 'Two rules at once: $x >= -3$ and $x ≠ 1$.'), ('1/(x^2 - 4x)', 'The bottom is $x(x - 4)$, which is 0 at 0 and at 4.'),
                  ('sqrt(x - 1)/(x^2 - 9)', '$x >= 1$ for the root. Of $x = 3$ and $x = -3$, only 3 is left to throw out.'), ('x/sqrt(6 - 2x)', 'On the bottom and inside a root: $6 - 2x > 0$, so $x < 3$.')]:
        Q.append(INTERVAL(d.qid('X'), f'Find the domain of $f(x) = {D(f)}$.', domain_of(S(f)), level=3, explain=ex))
    d.drill('practice', 'Practice', Q, 'pool', setSize=10)
    save_graphs(d)


# ====================================================================== 3. Factoring
def lin_f(r_, a_=1):
    """(ax - r) written with its sign: (x + 3), (2x - 1)"""
    r_ = sp.nsimplify(r_)
    return f'({"" if a_ == 1 else a_}x {"-" if r_ > 0 else "+"} {abs(r_)})'


def deck_factor():
    d = Deck('t-factor', 'Factoring', 'Turning a sum into a product: common factors, differences of squares, trinomials.', UNIT)
    L = [
        MC('L1', 'Factoring rewrites a **sum** as a **product**. Always look for a common factor first.' + box('6x^2 + 9x') + 'Both terms are divisible by $3x$. Pull it out.',
           ['$3x(2x + 3)$', '$6x(x + 9)$', '$3x(2x + 9)$', '$x(6x^2 + 9)$'], hint='$6x^2 = 3x · 2x$ and $9x = 3x · 3$.', explain='Check by multiplying back: $3x · 2x + 3x · 3 = 6x^2 + 9x$.'),
        CRIT('L2', box('x^2 + 7x + 12') + 'For a trinomial like this, find two numbers that **multiply to 12** and **add to 7**. Enter both.', [3, 4], 'number =', var='n', noneText='No such numbers',
             hint='List the pairs that multiply to 12: 1 and 12, 2 and 6, 3 and 4. Which pair adds to 7?', explain='$3 · 4 = 12$ and $3 + 4 = 7$, so $x^2 + 7x + 12 = (x + 3)(x + 4)$.'),
        EF(d, 'L3', 'Your turn. Factor it:' + box('x^2 - x - 6'), '(x - 3)(x + 2)', x ** 2 - x - 6, label='$x^2 - x - 6$ =',
           hint='Two numbers that multiply to −6 and add to −1: try −3 and 2.', explain='$(x - 3)(x + 2)$. A negative product means the two numbers have opposite signs.'),
        MC('L4', 'One pattern is worth knowing on sight, the **difference of squares**:' + box('a^2 - b^2 = (a - b)(a + b)') + 'Factor $x^2 - 25$.',
           ['$(x - 5)(x + 5)$', '$(x - 5)^2$', '$(x + 5)^2$', 'It does not factor'], hint='$25 = 5^2$.', explain='$(x - 5)(x + 5) = x^2 + 5x - 5x - 25$. The middle terms cancel.'),
        TF('L5', '$x^2 + 25$ factors as $(x + 5)(x + 5)$.', False, hint='Multiply $(x + 5)(x + 5)$ out and count the terms.',
           explain='$(x + 5)^2 = x^2 + 10x + 25$. A **sum** of squares does not factor at all.'),
        EF(d, 'L6', 'Put it together: common factor first, then look again.' + box('2x^2 - 18'), '2(x - 3)(x + 3)', 2 * x ** 2 - 18, label='$2x^2 - 18$ =',
           hint='Pull out the 2: $2(x^2 - 9)$. Now what is $x^2 - 9$?', explain='$2(x^2 - 9) = 2(x - 3)(x + 3)$. Factored completely means nothing inside can be factored again.'),
    ]
    d.lesson(L)
    T = [
        MATCH('T1', 'Match each expression to its factored form.', [['$x^2 - 9$', '$(x - 3)(x + 3)$'], ['$x^2 - 6x + 9$', '$(x - 3)^2$'], ['$x^2 - 3x$', '$x(x - 3)$'], ['$x^2 + 6x + 9$', '$(x + 3)^2$']],
              explain='Multiply each one back out to check it.'),
        TF('T2', '$(x + 3)^2 = x^2 + 9$', False, explain='$(x + 3)^2 = (x + 3)(x + 3) = x^2 + 6x + 9$. The middle term is easy to forget and it is never zero.'),
        MC('T3', 'What is the first step in factoring $4x^3 - 8x^2$?', ['Pull out $4x^2$', 'Find two numbers that multiply to −8', 'Use the difference of squares', 'Divide by $x$'],
           explain='Common factor first, always: $4x^2(x - 2)$.'),
        MC('T4', 'To factor $x^2 - 5x + 6$, the two numbers are', ['−2 and −3', '2 and 3', '−1 and −6', '1 and 6'],
           explain='They multiply to $+6$ (same sign) and add to $-5$ (so both negative): $(x - 2)(x - 3)$.'),
        MC('T5', 'Which one is factored **completely**?', ['$x(x - 2)(x + 2)$', '$x(x^2 - 4)$', '$(x^2 - 2x)(x + 2)$', '$x^3 - 4x$'],
           explain='$x^2 - 4$ and $x^2 - 2x$ can each still be factored. The first choice cannot.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for e_, g_, ins in [('6x^2 + 9x', '3x', '2x + 3'), ('4x^3 - 8x^2', '4x^2', 'x - 2'), ('5x^2 + 10x', '5x', 'x + 2'), ('x^3 + x^2', 'x^2', 'x + 1'), ('12x - 18', '6', '2x - 3'),
                        ('3x^2 - 3x', '3x', 'x - 1'), ('2x^3 + 6x', '2x', 'x^2 + 3'), ('7x^2 - 14', '7', 'x^2 - 2'), ('8x^2 + 4x', '4x', '2x + 1'), ('9x^3 - 6x^2', '3x^2', '3x - 2')]:
        assert sp.expand(S(g_) * S(ins) - S(e_)) == 0
        Q.append(E(d, d.qid('G'), 'Pull out the common factor. What is left inside the parentheses?', ins, S(ins), label=f'${D(e_)} = {D(g_)}($', post='$)$', level=1,
                   explain=f'${D(e_)} = {D(g_)}({D(ins)})$'))
    for p_, q_ in [(3, 4), (2, 3), (-2, -3), (3, -2), (-4, 3), (3, 5), (-2, -5), (4, -2), (-5, 2), (4, 5)]:
        b0, c0 = p_ + q_, p_ * q_
        tri = poly_str([1, b0, c0])
        Q.append(CRIT(d.qid('N'), box(tri) + f'Find the two numbers that multiply to ${c0}$ and add to ${b0}$.', [p_, q_], 'number =', var='n', noneText='No such numbers', level=1,
                      explain=f'The numbers are {p_} and {q_}, so ${tri} = {lin_f(-p_)}{lin_f(-q_)}$.'))
    for a_, b_ in [(1, 3), (1, 5), (1, 1), (2, 3), (1, 7), (3, 1), (1, 10), (5, 2)]:
        e_ = poly_str([a_ * a_, 0, -b_ * b_])
        A = '' if a_ == 1 else str(a_)
        ans = f'({A}x - {b_})({A}x + {b_})'
        Q.append(EF(d, d.qid('S'), 'Factor the difference of squares:' + box(e_), ans, S(e_), label=f'${D(e_)}$ =', level=1, explain=f'${D(e_)} = {ans}$'))
    Q.append(EF(d, d.qid('S'), 'Factor the difference of squares:' + box('16 - x^2'), '(4 - x)(4 + x)', 16 - x ** 2, label='$16 - x^2$ =', level=1, explain='$16 - x^2 = (4 - x)(4 + x)$'))
    for r1, r2 in [(-3, -4), (-2, -3), (2, 3), (3, -2), (4, -3), (-3, -5), (2, 5), (-4, 2), (5, -2), (-4, -5), (1, 6), (-1, 7), (6, -2), (-6, -1)]:
        e_ = sp.expand((x - r1) * (x - r2))
        tri = poly_str([e_.coeff(x, 2), e_.coeff(x, 1), e_.coeff(x, 0)])
        ans = lin_f(r1) + lin_f(r2)
        Q.append(EF(d, d.qid('T'), 'Factor:' + box(tri), ans, e_, label=f'${D(tri)}$ =', level=2,
                    explain=f'Two numbers that multiply to ${e_.coeff(x, 0)}$ and add to ${e_.coeff(x, 1)}$: ${D(tri)} = {ans}$.'))
    for e_, ans in [('x^2 + 6x + 9', '(x + 3)^2'), ('x^2 - 10x + 25', '(x - 5)^2'), ('x^2 + 2x + 1', '(x + 1)^2'), ('x^2 - 8x + 16', '(x - 4)^2'), ('4x^2 + 4x + 1', '(2x + 1)^2')]:
        Q.append(EF(d, d.qid('Q'), 'Factor:' + box(e_), ans, S(e_), label=f'${D(e_)}$ =', level=2, explain=f'The same factor twice: ${D(e_)} = {D(ans)}$.'))
    for e_, ans in [('2x^2 + 10x + 12', '2(x + 2)(x + 3)'), ('3x^2 - 12', '3(x - 2)(x + 2)'), ('x^3 - 4x', 'x(x - 2)(x + 2)'), ('x^3 + 5x^2 + 6x', 'x(x + 2)(x + 3)'), ('5x^2 - 5', '5(x - 1)(x + 1)'),
                    ('4x^2 - 16x + 16', '4(x - 2)^2'), ('x^3 - x', 'x(x - 1)(x + 1)'), ('3x^2 + 3x - 18', '3(x + 3)(x - 2)')]:
        Q.append(EF(d, d.qid('C'), 'Factor completely:' + box(e_), ans, S(e_), label=f'${D(e_)}$ =', level=2, explain=f'Common factor first, then factor what is left: ${D(ans)}$.'))
    for e_, ans in [('2x^2 + 7x + 3', '(2x + 1)(x + 3)'), ('3x^2 + 5x + 2', '(3x + 2)(x + 1)'), ('2x^2 - 5x - 3', '(2x + 1)(x - 3)'), ('2x^2 + x - 6', '(2x - 3)(x + 2)'),
                    ('3x^2 - 10x + 3', '(3x - 1)(x - 3)'), ('4x^2 - 4x - 3', '(2x + 1)(2x - 3)'), ('6x^2 + x - 1', '(3x - 1)(2x + 1)'), ('5x^2 + 9x - 2', '(5x - 1)(x + 2)')]:
        Q.append(EF(d, d.qid('A'), 'Factor:' + box(e_), ans, S(e_), label=f'${D(e_)}$ =', level=3, explain=f'${D(e_)} = {D(ans)}$. Multiply it back out to check the middle term.'))
    for e_, ans in [('x^3 + 2x^2 + 3x + 6', '(x^2 + 3)(x + 2)'), ('x^3 - x^2 + 4x - 4', '(x^2 + 4)(x - 1)'), ('x^3 + 3x^2 - 4x - 12', '(x - 2)(x + 2)(x + 3)'), ('2x^3 + x^2 + 8x + 4', '(x^2 + 4)(2x + 1)')]:
        Q.append(EF(d, d.qid('B'), 'Factor by grouping:' + box(e_), ans, S(e_), label='factored =', level=3, explain=f'Group the first two terms and the last two, and pull a common factor from each: ${D(ans)}$.'))
    for e_ in ['x^2 - 5x + 6', 'x^2 + 3x - 10', 'x^2 - 16', 'x^2 - 7x', '2x^2 - 8x + 6', 'x^3 - 9x']:
        zs = sorted(sp.solveset(S(e_), x, sp.S.Reals))
        Q.append(CRIT(d.qid('Z'), f'Solve by factoring. List every solution.' + box(e_ + ' = 0'), zs, '$x$ =', noneText='There are no solutions', level=3,
                      explain=f'${D(e_)} = {D(sp_app(sp.factor(S(e_))))}$, and a product is 0 only when one of its factors is 0.'))
    d.drill('practice', 'Practice', Q, 'pool', setSize=10)
    d.save()


# ====================================================================== 4. Rational Expressions
def checked_cancel(qid, text, top, bot, **kw):
    """a cancel item, with the result the app will show checked against sympy"""
    t = cancel_truth(top, bot)
    n_, d_ = sp.fraction(sp.cancel(t))
    if top[0] == '*' and bot[0] == '*':
        used, pairs = set(), []
        for i, p in enumerate(top[1]):
            for j, q in enumerate(bot[1]):
                if q == p and j not in used:
                    used.add(j)
                    pairs.append((i, j))
                    break
        rt = sp.Mul(*[S(p) for i, p in enumerate(top[1]) if i not in {a_ for a_, _ in pairs}])
        rb = sp.Mul(*[S(p) for j, p in enumerate(bot[1]) if j not in {b_ for _, b_ in pairs}])
        assert sp.simplify(rt / rb - t) == 0
        assert sp.gcd(rt, rb) == 1, (qid, 'more would cancel')
    else:
        N0, D0 = sp.fraction(sp.together(t))
        assert sp.gcd(N0, D0) == 1, (qid, 'this fraction really does reduce; do not use it as a "nothing cancels" item', top, bot)
    return CANCEL(qid, text, top, bot, **kw)


def deck_rational():
    d = Deck('t-rational', 'Rational Expressions', 'What is allowed to cancel, how to add fractions, and fractions inside fractions.', UNIT)
    CT = 'Cancel every common factor. If nothing is allowed to cancel, say so.'
    L = [
        checked_cancel('L1', 'Cancelling means dividing the top and the bottom by the same **factor**. Here both are products, so go ahead: cancel what they share.',
                       ('*', ['3', 'x', '(x + 2)']), ('*', ['x', '(x - 5)']), hint='Find a piece that multiplies the whole top and also the whole bottom.',
                       explain='$x$ multiplies everything on top and everything on the bottom, so it divides out.'),
        checked_cancel('L2', 'Now the top is a **sum**. Can the $x$’s cancel?', ('+', ['x', '+ 3']), ('*', ['x']),
                       hint='Try $x = 3$. The fraction is $frac{3 + 3}{3} = 2$. Crossing out the $x$’s would leave 3.',
                       explain='Test it with $x = 3$: the fraction is $frac{6}{3} = 2$, but crossing out the $x$’s leaves 3. On top, $x$ is a **term**, not a factor of the whole top.'),
        STEPS('L3', 'So when you see a sum, **factor first**. Then cancel.' + box('frac{x^2 + 3x}{x^2 - 9}'), [
            EF(d, 'L3.1', 'Factor the top.', 'x(x + 3)', x ** 2 + 3 * x, label='$x^2 + 3x$ =', hint='Common factor.', work='top $= x(x + 3)$'),
            EF(d, 'L3.2', 'Factor the bottom.', '(x - 3)(x + 3)', x ** 2 - 9, label='$x^2 - 9$ =', hint='Difference of squares.', work='bottom $= (x - 3)(x + 3)$'),
            checked_cancel('L3.3', 'Now both are products. Cancel.', ('*', ['x', '(x + 3)']), ('*', ['(x - 3)', '(x + 3)']), work='$= frac{x}{x - 3}$'),
        ]),
        MC('L4', 'Adding fractions needs a common denominator. Multiply each fraction by what it is missing.' + box('frac{1}{x} + frac{1}{3}') + 'As one fraction, this is',
           ['$frac{3 + x}{3x}$', '$frac{2}{x + 3}$', '$frac{1}{3x}$', '$frac{2}{3x}$'], hint='$frac{1}{x} = frac{3}{3x}$ and $frac{1}{3} = frac{x}{3x}$.',
           explain='$frac{3}{3x} + frac{x}{3x} = frac{3 + x}{3x}$. You never add the bottoms.'),
        STEPS('L5', 'A **complex fraction** has fractions inside a fraction. Tidy the top first, then deal with the bottom.' + box('frac{frac{1}{x} - frac{1}{3}}{x - 3}'), [
            MC('L5.1', 'Combine the top into one fraction.', ['$frac{3 - x}{3x}$', '$frac{x - 3}{3x}$', '$frac{1}{x - 3}$', '$frac{-2}{3x}$'],
               hint='$frac{1}{x} - frac{1}{3} = frac{3}{3x} - frac{x}{3x}$', work='top $= frac{3 - x}{3x}$'),
            MC('L5.2', 'Dividing by $x - 3$ is multiplying by $frac{1}{x - 3}$. And $3 - x = -(x - 3)$. What is left after cancelling?', ['$-frac{1}{3x}$', '$frac{1}{3x}$', '$-frac{1}{x - 3}$', '$frac{3 - x}{3x}$'],
               hint='$frac{-(x - 3)}{3x} · frac{1}{x - 3}$', work='$= -frac{1}{3x}$'),
        ]),
    ]
    d.lesson(L)
    T = [
        TF('T1', '$frac{x + 6}{x}$ simplifies to 6.', False, explain='The top is a sum, so $x$ is a term there, not a factor. Try $x = 2$: $frac{8}{2} = 4$, not 6.'),
        MC('T2', '$frac{x^2 - 9}{x - 3}$ simplifies to', ['$x + 3$', '$x - 3$', '$x^2 - 3$', '3'], explain='Factor first: $frac{(x - 3)(x + 3)}{x - 3} = x + 3$.'),
        MC('T3', '$frac{1}{a} + frac{1}{b} =$', ['$frac{a + b}{ab}$', '$frac{2}{a + b}$', '$frac{1}{a + b}$', '$frac{1}{ab}$'], explain='Common denominator $ab$: $frac{b}{ab} + frac{a}{ab}$.'),
        PICK('T4', 'Which of these can be reduced exactly as written? Select all that apply.', ['$frac{3x}{3y}$', '$frac{x + 3}{y + 3}$', '$frac{x(x + 1)}{2(x + 1)}$', '$frac{x^2 + 1}{x^2}$'], [0, 2],
             explain='Only the ones where the top and the bottom are both products with a factor in common.'),
        TF('T5', '$frac{a + b}{c} = frac{a}{c} + frac{b}{c}$', True, explain='A sum on **top** splits up. This is just adding fractions, read backwards.'),
        TF('T6', '$frac{c}{a + b} = frac{c}{a} + frac{c}{b}$', False, explain='A sum on the **bottom** does not split. Try $a = b = c = 1$: $frac{1}{2}$ is not $1 + 1$.'),
        MC('T7', 'Dividing by a fraction means multiplying by its flip. So $frac{a}{b/c} =$', ['$frac{ac}{b}$', '$frac{ab}{c}$', '$frac{a}{bc}$', '$abc$'], explain='$a ÷ frac{b}{c} = a · frac{c}{b}$'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for top, bot in [(('*', ['3', 'x']), ('*', ['x', '(x + 2)'])), (('*', ['x', '(x - 1)']), ('*', ['(x - 1)', '(x + 4)'])), (('+', ['x', '+ 5']), ('*', ['x', '(x - 2)'])),
                     (('*', ['2', '(x + 3)']), ('*', ['(x + 3)', '(x - 3)'])), (('+', ['x^2', '+ 1']), ('+', ['x^2', '+ 4'])), (('*', ['x', '(x + 1)', '(x - 2)']), ('*', ['(x - 2)', '(x + 1)'])),
                     (('*', ['5', 'x']), ('+', ['x', '+ 5'])), (('*', ['(x + 2)', '(x - 2)']), ('*', ['(x - 2)'])), (('+', ['2x', '+ 7']), ('*', ['2', 'x'])),
                     (('*', ['4', 'x^2']), ('*', ['x^2', '(x + 1)'])), (('+', ['x', '- 3']), ('+', ['x', '+ 3'])), (('*', ['(x + 5)']), ('*', ['x', '(x + 5)'])),
                     (('*', ['x', '(x + 4)']), ('+', ['x^2', '+ 4'])), (('*', ['7', '(x - 1)']), ('*', ['7', '(x + 1)'])), (('*', ['x', '(2x + 1)']), ('*', ['x', 'x', '(x + 1)'])),
                     (('+', ['x^2', '+ x', '+ 1']), ('*', ['x', '(x + 2)']))]:
        Q.append(checked_cancel(d.qid('K'), CT, top, bot, level=1))
    red = [('(x^2 + 3x)/(x^2 - 9)', 'x/(x - 3)'), ('(x^2 - 4)/(x - 2)', 'x + 2'), ('(x^2 - 1)/(x^2 + x)', '(x - 1)/x'), ('(2x + 6)/(x^2 + 3x)', '2/x'), ('(x^2 + 5x + 6)/(x + 2)', 'x + 3'),
           ('(x^2 - x - 6)/(x^2 - 9)', '(x + 2)/(x + 3)'), ('(x^2 - 25)/(x^2 + 5x)', '(x - 5)/x'), ('(3x^2 - 3x)/(x - 1)', '3x'), ('(x^2 + 2x + 1)/(x^2 - 1)', '(x + 1)/(x - 1)'),
           ('(x^2 - 16)/(x^2 - 4x)', '(x + 4)/x'), ('(x^3 - x)/(x^2 - x)', 'x + 1'), ('(x^2 - 6x + 9)/(x - 3)', 'x - 3')]
    for o, ans in red:
        Q.append(ES(d, d.qid('F'), 'Factor, then cancel:' + box(D(o)), ans, sp.cancel(S(o)), original=o, label='simplified =', level=2, ranges={'x': [4.2, 6.5]},
                    explain=f'Factor the top and the bottom, then cancel the factor they share: ${D(ans)}$.'))
    add = [('1/x + 1/3', '(x + 3)/(3x)'), ('2/x - 1/2', '(4 - x)/(2x)'), ('1/(x + 1) + 1', '(x + 2)/(x + 1)'), ('3/x + 2/x^2', '(3x + 2)/x^2'), ('1/x - 1/(x + 1)', '1/(x(x + 1))'),
           ('x/2 + 1/x', '(x^2 + 2)/(2x)'), ('2 - 1/x', '(2x - 1)/x'), ('1/(x - 1) + 1/(x + 1)', '2x/((x - 1)(x + 1))'), ('1/3 - 1/x', '(x - 3)/(3x)'), ('1/(x + h) - 1/x', '-h/(x(x + h))')]
    for o, ans in add:
        vars_ = ['x', 'h'] if 'h' in o else ['x']
        q = E(d, d.qid('A'), 'Write as one fraction:' + box(Dsum(o)), ans, sp.together(S(o)), vars_, label='one fraction =', level=2, ranges={'x': [4.2, 6.5], 'h': [0.3, 1.2]},
              explain=f'Give both fractions the same bottom, then combine the tops: ${D(ans)}$.')
        q['form'] = 'single'
        Q.append(q)
    cf = [('1/x - 1/3', 'x - 3', '(3 - x)/(3x)', '-1/(3x)'), ('1/x - 1/2', 'x - 2', '(2 - x)/(2x)', '-1/(2x)'), ('1/(x + 1) - 1/3', 'x - 2', '(2 - x)/(3(x + 1))', '-1/(3(x + 1))'),
          ('1 - 1/x', 'x - 1', '(x - 1)/x', '1/x'), ('1/x + 1/4', 'x + 4', '(x + 4)/(4x)', '1/(4x)'), ('1/(x + h) - 1/x', 'h', '-h/(x(x + h))', '-1/(x(x + h))'),
          ('1/(x + 2) - 1/2', 'x', '-x/(2(x + 2))', '-1/(2(x + 2))'), ('2/x - 2/5', 'x - 5', '(10 - 2x)/(5x)', '-2/(5x)')]
    for tp, bt, mid, ans in cf:
        vars_ = ['x', 'h'] if 'h' in tp else ['x']
        rg = {'x': [6.2, 8.5], 'h': [0.3, 1.2]}
        qid = d.qid('X')
        s1 = E(d, qid + '.1', 'Combine the top into one fraction.', mid, sp.together(S(tp)), vars_, label='top =', ranges=rg, work=f'top $= {D(mid)}$')
        s1['form'] = 'single'
        s2 = ES(d, qid + '.2', f'Now divide by ${D(bt)}$ and cancel.', ans, sp.cancel(sp.together(S(tp)) / S(bt)), original=f'({mid})/({bt})', slack=1, vars_=vars_, label='simplified =',
                ranges=rg, work=f'$= {D(ans)}$', explain=f'Dividing by ${D(bt)}$ puts it on the bottom, where it cancels with the top.')
        Q.append(STEPS(qid, 'Simplify the complex fraction:' + box(f'frac{{{Dsum(tp)}}}{{{bt}}}'), [s1, s2], level=3, explain=f'${D(ans)}$'))
    d.drill('practice', 'Practice', Q, 'pool', setSize=10)
    d.save()
