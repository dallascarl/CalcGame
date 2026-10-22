"""World 1 (Limits): short lesson, theory set (all required) and a practice pool for each stop.
limits-intro is rebuilt from tools/gen/src/limits-intro.orig.json (the pilot deck), keeping its graphs and questions.
See lib.py before re-running: it overwrites decks."""
import random, re, json, copy, os, subprocess
import sympy as sp
from lib import *

R = random.Random(1111)


def L_(a0, side=''):
    """lim[x->a] markup"""
    return f'lim[x->{a0}{side}]'


def LIMQ(fx, a0, side=''):
    return f'${L_(a0, side)} {fx}$'


def graphtruth(path):
    subprocess.run(['node', os.path.join(ROOT, 'tools', 'gen', 'graphtruth.js'), path], check=True)


# ====================================================================== 1. Limits (the pilot deck, made short)
def deck_limits():
    src = json.load(open(os.path.join(ROOT, 'tools', 'gen', 'src', 'limits-intro.orig.json')))
    d = copy.deepcopy(src)
    S_ = {s['id']: s for s in src['lesson']['slides']}
    s03 = dict(S_['s03'], explain='The heights close in on 3. That height is the **limit**: $lim[x->2] f(x) = 3$.')
    s07 = dict(S_['s07'], explain='Still 3. **A limit is where the graph is heading. It does not matter what happens at the point itself.**')
    s12 = S_['s12']
    s16 = dict(S_['s16'], text='Coming from the left ($x -> 2^-$) the graph heads to 1. From the right ($x -> 2^+$) it heads to 3. What is the two-sided limit $lim[x->2] f(x)$?',
               explain='The sides disagree, so the limit does not exist (DNE). The one-sided limits still exist: $lim[x->2^-] f(x) = 1$ and $lim[x->2^+] f(x) = 3$.')
    d['lesson'] = {'slides': [S_['s01'], S_['s02'], s03, S_['s06'], s07, s12, s16]}
    T = {q['id']: q for q in src['drills']['theory']['questions']}
    d['drills'] = {}
    d['drills']['theory'] = {'title': 'Theory', 'mode': 'all', 'questions': [T[k] for k in ['t01', 't02', 't03', 't05', 't06', 't07', 't08', 't11']]}
    Q = copy.deepcopy(src['drills']['calc']['questions'])
    G = d['graphs']
    G['D6'] = {'window': [-4, 4, -2, 5], 'pieces': [{'expr': 'x+3', 'from': -4, 'to': -1}, {'expr': '2', 'from': -1, 'to': 2}, {'expr': '6-2*x', 'from': 2, 'to': 4}],
               'holes': [[-1, 2], [2, 2]], 'dots': [[-1, 4], [2, -1]]}
    G['D7'] = {'window': [-3, 4, -1, 6], 'pieces': [{'expr': 'x^2/2', 'from': -3, 'to': 1}, {'expr': 'x+2', 'from': 1, 'to': 4}], 'holes': [[1, 0.5]], 'dots': [[1, 3]]}
    G['D8'] = {'window': [-3, 3, -2, 4], 'pieces': [{'expr': '3-x^2/2', 'from': -3, 'to': 3}], 'holes': [[0, 3]]}
    G['D9'] = {'window': [-4, 3, -3, 6], 'pieces': [{'expr': '1-x', 'from': -4, 'to': 0}, {'expr': 'x^2-2', 'from': 0, 'to': 3}], 'holes': [[0, 1], [0, -2]]}
    G['D10'] = {'window': [-2, 4, -2, 5], 'pieces': [{'expr': '2*x-1', 'from': -2, 'to': 1}, {'expr': '4-x', 'from': 1, 'to': 4}], 'holes': [[1, 3]], 'dots': [[1, 1]]}
    asks = {'D6': [(-1, 'value', None), (-1, 'limit', 'both'), (2, 'value', None), (2, 'limit', 'left'), (2, 'limit', 'right'), (2, 'limit', 'both'), (0, 'limit', 'both'), (3, 'limit', 'both')],
            'D7': [(1, 'limit', 'left'), (1, 'limit', 'right'), (1, 'limit', 'both'), (1, 'value', None), (-2, 'limit', 'both'), (3, 'limit', 'both')],
            'D8': [(0, 'value', None), (0, 'limit', 'both'), (2, 'limit', 'both'), (0, 'limit', 'left'), (-2, 'value', None)],
            'D9': [(0, 'limit', 'left'), (0, 'limit', 'right'), (0, 'limit', 'both'), (0, 'value', None), (2, 'limit', 'both'), (-2, 'limit', 'both')],
            'D10': [(1, 'limit', 'left'), (1, 'limit', 'right'), (1, 'value', None), (1, 'limit', 'both'), (3, 'limit', 'both'), (0, 'value', None)]}
    k = 0
    for g, lst in asks.items():
        for at, ask, side in lst:
            k += 1
            q = {'id': f'c{24 + k:02d}', 'type': 'graph', 'graph': g, 'ask': ask, 'at': at, 'answer': None}
            if side:
                q['side'] = side
            q['explain'] = ('Read the height of the filled point (or the curve) right at $x = ' + str(at) + '$. An open circle alone means undefined.') if ask == 'value' else \
                ('Follow the graph toward $x = ' + str(at) + '$ from ' + {'left': 'the left only.', 'right': 'the right only.', 'both': 'both sides. If they disagree, the limit is DNE.'}[side])
            Q.append(q)
    tables = [([1.9, 1.99, 1.999, 2.001, 2.01, 2.1], lambda v: v ** 2, 2, 4), ([0.9, 0.99, 0.999, 1.001, 1.01, 1.1], lambda v: (v - 1) / (v * v + v - 2), 1, sp.Rational(1, 3)),
              ([-0.1, -0.01, -0.001, 0.001, 0.01, 0.1], lambda v: sp.sin(v) / v, 0, 1), ([2.9, 2.99, 2.999, 3.001, 3.01, 3.1], lambda v: (v * v - 9) / (v - 3), 3, 6)]
    for xs, f, a0, Lv in tables:
        k += 1
        tab = ' · '.join(f'$f({v}) ≈ {float(sp.N(f(sp.Float(v)))):.4f}$' for v in xs)
        Q.append(N(f'c{24 + k:02d}', f'A table of values: {tab}. Guess $lim[x->{a0}] f(x)$.', Lv, label=f'$lim[x->{a0}] f(x)$ =', tol=0.01,
                   explain=f'From both sides the values close in on {frac_str(Lv)}.'))
    for q in Q:
        if q['type'] == 'num':
            q['level'] = 1
        elif q['ask'] == 'value':
            q['level'] = 1
        elif q.get('side') in ('left', 'right'):
            q['level'] = 2
        else:
            q['level'] = 2 if q['answer'] is None or q['answer'] != 'DNE' else 3
    d['drills']['practice'] = {'title': 'Practice', 'mode': 'pool', 'questions': Q}
    d['version'] = 2
    used = {q.get('graph') for q in d['lesson']['slides'] + Q}
    d['graphs'] = {k: v for k, v in G.items() if k in used}
    p = os.path.join(ROOT, 'decks', 'limits-intro.json')
    json.dump(d, open(p, 'w'), indent=1, ensure_ascii=False)
    graphtruth(p)
    d = json.load(open(p))
    for q in d['drills']['practice']['questions']:
        if q['type'] == 'graph' and q['answer'] == 'DNE':
            q['level'] = 3
    json.dump(d, open(p, 'w'), indent=1, ensure_ascii=False)


# ====================================================================== 2. Infinite limits
def sign_word(v):
    return 'positive' if v > 0 else 'negative'


def deck_infinite():
    d = Deck('l-infinite', 'Infinite Limits', 'When a function grows without bound.', 'Limits')
    L = []
    L.append(MC('L1', 'As $x -> 0$, $f(x) = frac{1}{x^2}$ gives 100, then 10,000, then 1,000,000… It **increases without bound**. We describe that by writing',
                ['$lim[x->0] frac{1}{x^2} = infty$', '$lim[x->0] frac{1}{x^2} = 0$', '$lim[x->0] frac{1}{x^2} = 1$', '$lim[x->0] frac{1}{x^2} = -infty$'],
                hint='The values keep getting bigger.', explain='$= infty$ tells HOW the limit fails to be a number: the function blows up.'))
    L.append(LIM('L2', 'Use the $infty$ button. As $x -> 0^+$ ($x$ small and positive), $frac{1}{x}$ is a big positive number. Find $lim[x->0^+] frac{1}{x}$.', 'inf', label='$lim[x->0^+] frac{1}{x}$ =',
                 hint='1 divided by a tiny positive number is a huge positive number.', explain='$infty$'))
    L.append(LIM('L3', 'From the left, $x$ is small and **negative**. Find $lim[x->0^-] frac{1}{x}$.', '-inf', label='$lim[x->0^-] frac{1}{x}$ =',
                 hint='1 divided by a tiny negative number is a huge negative number.', explain='$-infty$'))
    L.append(LIM('L4', 'So what is the two-sided limit $lim[x->0] frac{1}{x}$?', 'DNE', label='$lim[x->0] frac{1}{x}$ =', hint='The two sides go opposite ways.',
                 explain='One side goes to $infty$ and the other to $-infty$, so the two-sided limit does not exist.'))
    L.append(STEPS('L5', 'The trick: plug in. If you get $frac{a}{0}$ with $a ≠ 0$, the answer is $infty$, $-infty$ or DNE, and **signs** decide which. Find $lim[x->3^-] frac{5 - 2x}{x - 3}$.', [
        N('L5.1', 'Plug $x = 3$ into the top.', -1, label='top =', hint='$5 - 6$', work='top → −1'),
        MC('L5.2', 'For $x$ a little less than 3 (like 2.99), the bottom $x - 3$ is', ['a tiny negative number', 'a tiny positive number', 'exactly 0', 'a big number'], hint='$2.99 - 3$',
           work='bottom → tiny negative'),
        LIM('L5.3', '$frac{negative}{tiny negative}$ is…', 'inf', label=f'{L_(3, "^-")} = ', hint='Negative over negative is positive, and dividing by something tiny makes it huge.', work='limit $= infty$'),
    ]))
    d.lesson(L)

    T = [
        MC('T1', '$lim[x->a] f(x) = infty$ means', ['$f(x)$ grows without bound as $x -> a$', '$f(a) = infty$', 'the limit is a very large number', '$f$ is undefined at $a$'],
           explain='It describes the behavior; the limit is still not a number.'),
        MC('T2', 'You plug in $x = a$ and get $frac{4}{0}$. The limit is', ['$infty$, $-infty$, or DNE (check the signs)', '0', '4', 'always $infty$'], explain='A nonzero number over 0 blows up. Signs on each side decide.'),
        TF('T3', 'If $lim[x->a^+] f(x) = infty$ and $lim[x->a^-] f(x) = -infty$, then $lim[x->a] f(x)$ does not exist.', True, explain='The two sides must agree.'),
        MC('T4', 'An infinite limit at $x = a$ shows up on the graph as', ['a vertical asymptote at $x = a$', 'a horizontal asymptote', 'a hole', 'a jump'], explain='The graph shoots up or down along $x = a$.'),
        MC('T5', 'For $frac{1}{(x - a)^2}$, the bottom is', ['positive on both sides of $a$, so the limit is $infty$', 'negative on both sides', 'positive on one side and negative on the other', 'always 0'],
           explain='A square is never negative, so both sides blow up to $infty$.'),
        LIM('T6', 'Find $lim[x->pi/2^-] tan(x)$.', 'inf', label='limit =', explain='Just left of $frac{pi}{2}$, $sin$ is near 1 and $cos$ is a tiny positive number.'),
        TF('T7', '$lim[x->0] frac{1}{x}$ = $infty$.', False, explain='From the left it goes to $-infty$, so the two-sided limit is DNE.'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    forms = []
    for a0 in [1, 2, 3, -1, -2, 4]:
        for top, pw_ in [('1', 1), ('x + 2', 1), ('5 - 2x', 1), ('3', 2), ('x', 2), ('-2', 1), ('x^2 + 1', 1), ('-1', 2)]:
            forms.append((top, a0, pw_))
    R.shuffle(forms)
    plug = [('frac{x^2 + 2}{x - 1}', 1, 'a nonzero number over 0'), ('frac{x^2 - 4}{x - 2}', 2, '0 over 0'), ('frac{x + 5}{x + 1}', 3, 'just a number'), ('frac{3x}{(x - 2)^2}', 2, 'a nonzero number over 0'),
            ('frac{x - 3}{x^2 - 9}', 3, '0 over 0'), ('frac{x^2 + 1}{x}', 0, 'a nonzero number over 0'), ('frac{x^2}{x + 4}', 1, 'just a number'), ('frac{2x - 2}{x - 1}', 1, '0 over 0'),
            ('frac{cos(x)}{x}', 0, 'a nonzero number over 0'), ('frac{x - 1}{x + 1}', 1, 'just a number')]
    opts = ['just a number', 'a nonzero number over 0', '0 over 0']
    for f, a0, kind in plug:
        Q.append(MC(d.qid('P'), f'Plug $x = {a0}$ into ${f}$. What do you get?', opts, opts.index(kind), fixed=True, level=1,
                    explain={'just a number': 'Then that number is the limit.', 'a nonzero number over 0': 'The limit is $infty$, $-infty$ or DNE.', '0 over 0': 'Indeterminate: more algebra needed (later stops).'}[kind]))
    for top, a0, pw_ in forms[:10]:
        side = R.choice(['^+', '^-'])
        bot = f'(x - {a0})' if a0 > 0 else f'(x + {-a0})'
        bexpr = S(bot) ** pw_
        near = a0 + (0.01 if side == '^+' else -0.01)
        sgn = float(bexpr.subs(x, near))
        Q.append(MC(d.qid('B'), f'As $x -> {a0}{side}$, is the bottom ${D(bot if pw_ == 1 else bot + "^2")}$ a tiny positive or a tiny negative number?', ['tiny positive', 'tiny negative'],
                    0 if sgn > 0 else 1, fixed=True, level=2, explain=f'Try $x = {near:g}$: the bottom is ' + ('positive.' if sgn > 0 else 'negative.')))
    for top, a0, pw_ in forms:
        bot = f'(x - {a0})' if a0 > 0 else f'(x + {-a0})'
        e = S(top) / S(bot) ** pw_
        tv = S(top).subs(x, a0)
        if tv == 0:
            continue
        fdisp = f'frac{{{top}}}{{{bot[1:-1] if pw_ == 1 else bot + "^2"}}}'
        for side in ['^+', '^-', '']:
            ans = lim_of(e, a0, {'^+': '+', '^-': '-', '': '+-'}[side])
            lv = 3 if side == '' else 2
            Q.append(LIM(d.qid('L'), f'Find ${L_(a0, side)} {fdisp}$.', ans, label='limit =', level=lv,
                         explain=f'The top goes to {num(tv)} and the bottom goes to 0 ' + ('from the same side both ways (squared), ' if pw_ == 2 else '') +
                         {'inf': 'so it blows up to $infty$.', '-inf': 'so it blows up to $-infty$.', 'DNE': 'with opposite signs on the two sides, so the limit does not exist.'}.get(ans, '')))
            if len(Q) > 70:
                break
        if len(Q) > 70:
            break
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 3. Limit laws
def deck_laws():
    d = Deck('l-laws', 'Limit Laws', 'Break a limit into pieces you already know.', 'Limits')
    L = []
    L.append(MATCH('L1', 'If $lim[x->a] f(x)$ and $lim[x->a] g(x)$ both **exist**, limits split apart. Match each limit to what it equals.',
                   [['$lim(f + g)$', '$lim f + lim g$'], ['$lim(cf)$', '$c lim f$'], ['$lim(f·g)$', '$(lim f)(lim g)$'], ['$lim(frac{f}{g})$', '$frac{lim f}{lim g}$ if $lim g ≠ 0$']],
                   hint='Limits pass right through sums, constants, products and quotients.', explain='Plus: powers and roots pass through too.'))
    L.append(N('L2', '$lim[x->5] f(x) = 1$ and $lim[x->5] g(x) = 3$. Find $lim[x->5] f(x)(g(x) + 2f(x))$.', 5, label='limit =', hint='$1·(3 + 2·1)$', explain='$1(3 + 2) = 5$'))
    L.append(N('L3', 'Same $f$ and $g$. Find $lim[x->5] frac{f(x)}{g(x)}$.', sp.Rational(1, 3), label='limit =', hint='$frac{1}{3}$ (the bottom is not 0, so the quotient law works)', explain='$frac{1}{3}$'))
    L.append(N('L4', 'For a **polynomial**, the laws say: just plug in. Find $lim[x->2] (x^3 - 2x + 1)$.', 5, label='limit =', hint='$8 - 4 + 1$', explain='$lim[x->a] p(x) = p(a)$ for any polynomial.'))
    L.append(MC('L5', 'What if you plug in and get $frac{0}{0}$, like $lim[x->1] frac{x^2 - 1}{x - 1}$?', ['It is indeterminate: you need algebra first (factor, conjugate, combine…)', 'The limit is 0', 'The limit is 1', 'The limit does not exist'],
                hint='$frac{0}{0}$ could turn out to be anything.', explain='The next stops are all about tricks for $frac{0}{0}$.'))
    d.lesson(L)

    T = [
        MC('T1', 'The limit laws need', ['both $lim f$ and $lim g$ to exist', 'nothing at all', '$f$ and $g$ to be polynomials', '$f(a)$ and $g(a)$ to be defined'], explain='If either limit does not exist, the laws do not apply.'),
        MC('T2', 'The quotient law $lim frac{f}{g} = frac{lim f}{lim g}$ needs', ['$lim g ≠ 0$', '$lim f ≠ 0$', '$lim f = lim g$', 'nothing extra'], explain='You cannot divide by 0.'),
        TF('T3', 'If $p$ is a polynomial, then $lim[x->a] p(x) = p(a)$.', True, explain='Direct substitution works for every polynomial.'),
        TF('T4', 'If $lim[x->2] f(x) = 0$ and $lim[x->2] g(x) = 0$, then $lim[x->2] frac{f(x)}{g(x)}$ does not exist.', False, explain='$frac{0}{0}$ is indeterminate. The limit might be any number, or not exist.'),
        MC('T5', '$lim[x->a] sqrt(f(x)) =$', ['$sqrt(lim[x->a] f(x))$', '$lim[x->a] f(x)$', '$frac{1}{2}lim[x->a] f(x)$', 'it does not exist'], explain='Roots pass through limits (when the inside limit makes sense).'),
        MC('T6', 'For a rational function $frac{p(x)}{q(x)}$, direct substitution works when', ['$q(a) ≠ 0$', '$p(a) ≠ 0$', '$p(a) = q(a)$', 'always'], explain='Only a zero bottom causes trouble.'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    for k in range(18):
        Fv, Gv = R.choice([1, 2, -3, 4, 5, -2]), R.choice([3, -1, 2, 6, -4, 1])
        forms = [(f'$lim (f(x) + g(x))$', Fv + Gv), (f'$lim (3f(x) - g(x))$', 3 * Fv - Gv), (f'$lim f(x)g(x)$', Fv * Gv), (f'$lim frac{{f(x)}}{{g(x)}}$', sp.Rational(Fv, Gv)),
                 (f'$lim (f(x))^2$', Fv ** 2), (f'$lim f(x)(g(x) + 2f(x))$', Fv * (Gv + 2 * Fv)), (f'$lim (2f(x) + 5)$', 2 * Fv + 5), (f'$lim frac{{f(x) + g(x)}}{{2}}$', sp.Rational(Fv + Gv, 2))]
        ask, val = forms[k % len(forms)]
        Q.append(N(d.qid('C'), f'$lim[x->4] f(x) = {Fv}$ and $lim[x->4] g(x) = {Gv}$. Find {ask.replace("lim ", "lim[x->4] ")}.', val, label='limit =', level=1,
                   explain=f'Put {Fv} in for $f$ and {Gv} in for $g$: {frac_str(val)}.'))
    polys = [('x^3 - 2x + 1', 2), ('3x^2', 2), ('x^2 + 4x - 7', -1), ('5 - x^3', 1), ('2x^4 - x', -1), ('x^2(x - 3)', 4), ('(x + 1)^3', 1), ('7x - 2', 3), ('x^5 - x^4', 2), ('4', 9)]
    for f, a0 in polys:
        v = S(f).subs(x, a0)
        Q.append(N(d.qid('D'), f'Find $lim[x->{a0}] ({D(f, False)})$.', v, label='limit =', level=1, explain=f'Polynomial: plug in. {num(v)}'))
    rats = [('frac{2x + 1}{x + 2}', '(2x + 1)/(x + 2)', 2), ('frac{2x + 1}{-x - 2}', '(2x + 1)/(-x - 2)', 2), ('frac{x^2 - 1}{x + 3}', '(x^2 - 1)/(x + 3)', 1), ('frac{5x}{x^2 + 1}', '5x/(x^2 + 1)', 2),
            ('frac{x^3 + 1}{2x - 1}', '(x^3 + 1)/(2x - 1)', 2), ('frac{x - 4}{x + 4}', '(x - 4)/(x + 4)', 0), ('frac{sqrt(x + 5)}{x}', 'sqrt(x + 5)/x', 4), ('frac{x^2 + x}{3 - x}', '(x^2 + x)/(3 - x)', -2),
            ('sqrt(x^2 + 9)', 'sqrt(x^2 + 9)', 4), ('frac{1}{x} + frac{1}{x + 1}', '1/x + 1/(x + 1)', 1)]
    for disp, f, a0 in rats:
        v = S(f).subs(x, a0)
        Q.append(N(d.qid('Q'), f'Find $lim[x->{a0}] {disp}$.', v, label='limit =', level=2, explain=f'The bottom is not 0 at $x = {a0}$, so plug in: {frac_str(v)}.'))
    opts = ['just a number: that is the limit', 'a nonzero number over 0: infinite limit or DNE', '0 over 0: more algebra needed']
    plug = [('frac{x^2 - 1}{x - 1}', 1, 2), ('frac{x^2 + 1}{(x - 1)^2}', 1, 1), ('frac{x^2 + 2x + 1}{(x - 1)^2}', 1, 1), ('frac{x^2 - 4}{x}', 2, 0), ('frac{x^2 - 3x}{x}', 0, 2),
            ('frac{x + 1}{x - 2}', 2, 1), ('frac{x^3 - 8}{x - 2}', 2, 2), ('frac{x}{x + 7}', 0, 0), ('frac{sin(x)}{x}', 0, 2), ('frac{cos(x)}{x}', 0, 1)]
    for f, a0, k in plug:
        Q.append(MC(d.qid('K'), f'Plug $x = {a0}$ into ${f}$. What happens?', opts, k, fixed=True, level=2, explain=opts[k] + '.'))
    whyl = [('$lim[x->2] (x^2 + 3x) = lim[x->2] x^2 + lim[x->2] 3x$', 'Sum law'), ('$lim[x->2] 3x = 3 lim[x->2] x$', 'Constant multiple law'),
            ('$lim[x->2] x^2 = (lim[x->2] x)^2$', 'Power law'), ('$lim[x->2] frac{x}{x + 1} = frac{lim[x->2] x}{lim[x->2] (x + 1)}$', 'Quotient law'),
            ('$lim[x->2] x(x + 1) = (lim[x->2] x)(lim[x->2] (x + 1))$', 'Product law'), ('$lim[x->2] sqrt(x + 7) = sqrt(lim[x->2] (x + 7))$', 'Root law')]
    names = ['Sum law', 'Constant multiple law', 'Product law', 'Quotient law', 'Power law', 'Root law']
    for stp, law in whyl:
        o = [law] + [w for w in names if w != law][:3]
        Q.append(MC(d.qid('W'), f'Which law justifies this step? {stp}', o, level=3, explain=law + '.'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 4. Factor and cancel
FACT = [('x^2 - 1', 'x - 1', 'x + 1'), ('x^2 - 4', 'x - 2', 'x + 2'), ('x^2 - 9', 'x - 3', 'x + 3'), ('x^2 + x - 2', 'x - 1', 'x + 2'), ('x^2 - 5x + 6', 'x - 2', 'x - 3'),
        ('x^2 + 2x - 8', 'x - 2', 'x + 4'), ('x^2 - x - 6', 'x - 3', 'x + 2'), ('x^3 - 8', 'x - 2', 'x^2 + 2x + 4'), ('x^2 - 16', 'x + 4', 'x - 4'), ('2x^2 - 2x', 'x - 1', '2x'),
        ('x^2 + 5x + 4', 'x + 1', 'x + 4'), ('x^3 - x', 'x - 1', 'x(x + 1)'), ('x^2 - 2x - 15', 'x - 5', 'x + 3'), ('x^3 + 1', 'x + 1', 'x^2 - x + 1')]
# (top, bottom, a): 0/0 limits that factor
FL = [('x^2 - 1', 'x - 1', 1), ('x^2 - 4', 'x - 2', 2), ('x - 1', 'x^2 + x - 2', 1), ('x^2 - 5x + 6', 'x - 2', 2), ('x^2 + 2x - 8', 'x^2 - 4', 2), ('x^2 - x - 6', 'x - 3', 3),
      ('x^3 - 8', 'x - 2', 2), ('x^2 - 16', 'x + 4', -4), ('2x^2 - 2x', 'x - 1', 1), ('x^2 + 5x + 4', 'x^2 - 1', -1), ('x^2 - 9', 'x^2 - 2x - 3', 3), ('x^3 - x', 'x - 1', 1),
      ('x^2 - 2x - 15', 'x - 5', 5), ('x^3 + 1', 'x + 1', -1), ('x^2 - 4', 'x^2 - 5x + 6', 2), ('x^2 + 3x', 'x', 0)]


def deck_factor():
    d = Deck('l-factor', 'Factor and Cancel', 'The first trick for 0/0: factor the top and bottom.', 'Limits')
    L = []
    L.append(MC('L1', 'Find $lim[x->1] frac{x^2 - 1}{x - 1}$. Plugging in gives $frac{0}{0}$. Both are 0 at $x = 1$, so both have a factor of', ['$(x - 1)$', '$(x + 1)$', '$x$', '$(x^2 - 1)$'],
                hint='A polynomial that is 0 at $x = 1$ has $(x - 1)$ as a factor.', explain='That shared factor is what makes $frac{0}{0}$.'))
    L.append(STEPS('L2', 'Finish $lim[x->1] frac{x^2 - 1}{x - 1}$.', [
        E(d, 'L2.1', 'Factor the top.', 'x + 1', x + 1, label='$x^2 - 1 = (x - 1)·($', post='$)$', hint='Difference of squares.', work='$frac{(x - 1)(x + 1)}{x - 1}$'),
        E(d, 'L2.2', 'Cancel the $(x - 1)$. (Fine in a limit, because $x ≠ 1$ there.)', 'x + 1', x + 1, label='simplified =', hint='What is left?', work='$= x + 1$ (for $x ≠ 1$)'),
        LIM('L2.3', 'Now plug in.', 2, label=f'{L_(1)} = ', hint='$1 + 1$', work='limit $= 2$'),
    ]))
    L.append(LIM('L3', 'Your turn (from class): $lim[x->1] frac{x - 1}{x^2 + x - 2}$. Factor the bottom.', sp.Rational(1, 3), label='limit =', hint='$x^2 + x - 2 = (x - 1)(x + 2)$',
                 explain='Cancel to get $frac{1}{x + 2}$, then plug in: $frac{1}{3}$.'))
    L.append(MC('L4', 'Why are we allowed to cancel $(x - 1)$?', ['A limit only looks at $x$ near 1, never at $x = 1$, so $x - 1 ≠ 0$', 'Because $x - 1 = 1$', 'We are not; it is a trick', 'Because $0/0 = 1$'],
                hint='Does the limit care about $x = 1$ itself?', explain='The simplified function matches the original everywhere except $x = 1$, which a limit ignores.'))
    d.lesson(L)

    T = [
        MC('T1', 'Plugging in gives $frac{0}{0}$. A good first move is', ['factor the top and bottom and cancel', 'say the limit is 0', 'say the limit is DNE', 'say the limit is 1'], explain='$frac{0}{0}$ means there is a common factor hiding.'),
        TF('T2', 'If $p(a) = 0$ for a polynomial $p$, then $(x - a)$ is a factor of $p(x)$.', True, explain='The factor theorem.'),
        TF('T3', '$frac{(x - 2)(x + 2)}{x - 2}$ and $x + 2$ have the same limit as $x -> 2$.', True, explain='They agree everywhere except $x = 2$.'),
        MC('T4', 'After canceling, you plug in and get $frac{3}{0}$. The limit is', ['$infty$, $-infty$ or DNE', '3', '0', 'still $frac{0}{0}$'], explain='Now it is an infinite-limit question: check signs.'),
        MC('T5', '$x^2 - 9$ factors as', ['$(x - 3)(x + 3)$', '$(x - 9)(x + 1)$', '$(x - 3)^2$', '$x(x - 9)$'], explain='Difference of squares: $a^2 - b^2 = (a - b)(a + b)$.'),
    ]
    d.drill('theory', 'Theory', T, 'all')

    Q = []
    for top, f1, f2 in FACT:
        assert sp.expand(S(f1) * S(f2) - S(top)) == 0, top
        Q.append(E(d, d.qid('F'), f'Factor ${D(top)}$. Fill in the missing factor.', f2, S(f2), label=f'${D(top)} = ({D(f1)})·($', post='$)$', level=1, explain=f'${D(top)} = ({D(f1)})({D(f2)})$'))
    for top, bot, a0 in FL:
        simp = sp.cancel(S(top) / S(bot))
        Q.append(E(d, d.qid('C'), f'Factor and cancel: $frac{{{D(top)}}}{{{D(bot)}}}$ simplifies to', sp_app(simp), simp, label='simplified =', level=2, ranges={'x': [2.5, 4.5]},
                   explain=f'Cancel the common factor: ${D(sp_app(simp))}$.'))
    for top, bot, a0 in FL:
        e = S(top) / S(bot)
        simp = sp.cancel(e)
        ans = lim_of(e, a0)
        Q.append(STEPS(d.qid('W'), f'Find $lim[x->{a0}] frac{{{D(top)}}}{{{D(bot)}}}$.', [
            MC(None, f'Plug in $x = {a0}$. You get', ['$frac{0}{0}$', 'a number', '$frac{a}{0}$ with $a ≠ 0$'], work='$frac{0}{0}$: factor'),
            E(d, None, 'Factor, cancel, and write what is left.', sp_app(simp), simp, label='simplified =', ranges={'x': [2.5, 4.5]}, work=f'$= {D(sp_app(simp))}$'),
            LIM(None, 'Plug in.', ans, label='limit =', work=f'limit $= {frac_str(ans) if not isinstance(ans, str) else ans}$'),
        ], level=3, explain=f'{frac_str(ans) if not isinstance(ans, str) else ans}'))
    for top, bot, a0 in [('x - 2', 'x^2 - 4x + 4', 2), ('x + 1', 'x^2 + 2x + 1', -1), ('x^2 - 1', '(x - 1)^3', 1), ('x', 'x^3', 0)]:
        e = S(top) / S(bot)
        ans = lim_of(e, a0)
        Q.append(LIM(d.qid('X'), f'Find $lim[x->{a0}] frac{{{D(top)}}}{{{D(bot)}}}$. (After canceling, check what is left.)', ans, label='limit =', level=3,
                     explain=f'After canceling you get a nonzero number over 0: {ans}.'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 5. Squeeze theorem
def deck_squeeze():
    d = Deck('l-squeeze', 'The Squeeze Theorem', 'Trap a wiggly function between two simple ones.', 'Limits')
    L = []
    L.append(MC('L1', 'What is $lim[x->0] x^2 sin(frac{1}{x})$? The $sin(frac{1}{x})$ wiggles forever, so we cannot plug in. But sine is always between −1 and 1:\n$-1 <= sin(frac{1}{x}) <= 1$\nMultiply everything by $x^2$ (which is never negative):',
                ['$-x^2 <= x^2 sin(frac{1}{x}) <= x^2$', '$-1 <= x^2 sin(frac{1}{x}) <= 1$', '$x^2 <= x^2 sin(frac{1}{x}) <= -x^2$', '$0 <= x^2 sin(frac{1}{x}) <= x^2$'],
                hint='Multiply all three parts by $x^2$.', explain='Now the wiggly function is trapped between $-x^2$ and $x^2$.'))
    L.append(LIM('L2', 'Both outside functions are easy. Find $lim[x->0] x^2$ (and $lim[x->0] -x^2$ is the same).', 0, label='limit =', hint='Plug in 0.', explain='Both squeeze down to 0.'))
    L.append(LIM('L3', '**Squeeze Theorem:** if $f(x) <= g(x) <= h(x)$ near $a$, and $f$ and $h$ have the **same** limit $L$, then $g$ has limit $L$ too. So $lim[x->0] x^2 sin(frac{1}{x}) =$', 0,
                 label='limit =', hint='It is trapped between two things going to 0.', explain='0. The wiggles get squeezed flat.'))
    L.append(MC('L4', 'What if the two outside functions go to **different** limits, like 0 and 2?', ['The Squeeze Theorem tells you nothing', 'The limit is 1 (the average)', 'The limit is 0', 'The limit is 2'],
                hint='Is the middle function trapped at one value?', explain='The outside limits must agree for the squeeze to work.'))
    d.lesson(L)
    T = [
        MC('T1', 'The Squeeze Theorem needs', ['$f(x) <= g(x) <= h(x)$ near $a$ and $lim f = lim h$', '$f$, $g$, $h$ to be polynomials', '$g(a)$ to be defined', '$lim f ≠ lim h$'], explain='Trapped, and both walls meet at the same height.'),
        MC('T2', 'For every $x$, $sin(x)$ and $cos(x)$ are between', ['−1 and 1', '0 and 1', '$-x$ and $x$', '0 and $pi$'], explain='That is the usual starting point for a squeeze.'),
        TF('T3', 'If $1 <= g(x) <= 3$ for all $x$, then $lim[x->0] g(x)$ must be 2.', False, explain='The walls are 1 and 3, which do not agree. $g$ could do anything in between.'),
        MC('T4', 'The Squeeze Theorem is most useful for functions like', ['$x^2 sin(frac{1}{x})$ that wiggle and cannot be plugged in', 'polynomials', '$frac{x^2 - 1}{x - 1}$', '$frac{1}{x}$'], explain='Wiggly pieces with known bounds.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    walls = [('4x - 9', 'x^2 - 4x + 7', 4), ('2x', 'x^4 - x^2 + 2', 1), ('1 - x^2', '1 + x^2', 0), ('3x - 2', 'x^3', 1), ('cos(x)', '1 + x^2', 0), ('-x^2 + 6x', 'x^2 - 6x + 18', 3),
             ('cos(x)', '1', 0), ('2 - x^2', '2 + x^2', 0)]
    for lo, hi, a0 in walls:
        Lv = S(lo).subs(x, a0)
        assert Lv == S(hi).subs(x, a0)
        Q.append(LIM(d.qid('W'), f'For $x$ near {a0}, ${D(lo)} <= g(x) <= {D(hi)}$. Find $lim[x->{a0}] g(x)$.', Lv, label=f'$lim[x->{a0}] g(x)$ =', level=2,
                     explain=f'Both walls go to {num(Lv)} at $x = {a0}$, so $g$ is squeezed to {num(Lv)}.'))
    for lo, hi, a0 in [('x', 'x + 2', 0), ('1', '3', 2), ('x^2', '2x^2 + 1', 0), ('-1', '1', 0)]:
        Q.append(MC(d.qid('N'), f'For $x$ near {a0}, ${D(lo)} <= g(x) <= {D(hi)}$. What can you say about $lim[x->{a0}] g(x)$?', ['Nothing: the walls go to different limits', f'It is {num(S(lo).subs(x, a0))}', f'It is {num(S(hi).subs(x, a0))}', 'It does not exist'],
                    level=2, explain='The two walls do not meet, so the Squeeze Theorem does not apply.'))
    for f, wall in [('x^2 sin(frac{1}{x})', 'x^2'), ('x cos(frac{1}{x})', '|x|'), ('x^4 sin(frac{2}{x})', 'x^4'), ('x^2 cos(frac{3}{x})', 'x^2'), ('x sin(frac{1}{x^2})', '|x|'),
                    ('x^3 cos(frac{1}{x})', '|x^3|'), ('sqrt(x) sin(frac{1}{x})', 'sqrt(x)'), ('x^2 sin^2(frac{1}{x})', 'x^2')]:
        lim_side = '^+' if 'sqrt' in f else ''
        Q.append(LIM(d.qid('S'), f'Find $lim[x->0{lim_side}] {f}$.', 0, label='limit =', level=3, explain=f'The trig part stays between −1 and 1, so the whole thing is trapped between $-{wall}$ and ${wall}$, which both go to 0.'))
        Q.append(MC(d.qid('B'), f'To find $lim[x->0{lim_side}] {f}$ with the Squeeze Theorem, which walls work?', [f'$-{wall}$ and ${wall}$', '$-1$ and $1$', f'$0$ and ${wall}$', f'$-{wall}$ and $1$'],
                    level=1, explain=f'Start from $-1 <=$ trig $<= 1$ and multiply by the outside factor.'))
    for q_, r_, w_ in [('$-1 <= sin(frac{1}{x}) <= 1$. Multiply by $x^2$:', '$-x^2 <= x^2 sin(frac{1}{x}) <= x^2$', ['$-1 <= x^2 sin(frac{1}{x}) <= 1$', '$x^2 <= x^2 sin(frac{1}{x}) <= 1$', '$0 <= x^2 sin(frac{1}{x}) <= 1$']),
                       ('$-1 <= cos(x) <= 1$. Add 2:', '$1 <= 2 + cos(x) <= 3$', ['$-3 <= 2 + cos(x) <= 3$', '$2 <= 2 + cos(x) <= 3$', '$-1 <= 2 + cos(x) <= 1$']),
                       ('$0 <= sin^2(x) <= 1$. Multiply by $x^4$:', '$0 <= x^4 sin^2(x) <= x^4$', ['$-x^4 <= x^4 sin^2(x) <= x^4$', '$0 <= x^4 sin^2(x) <= 1$', '$x^4 <= x^4 sin^2(x) <= 1$'])]:
        Q.append(MC(d.qid('M'), q_, [r_] + w_, level=1, explain=r_))
    d.drill('practice', 'Practice', Q, 'pool', setSize=10)
    d.save()


# ====================================================================== 6. Trig limits
def deck_trig():
    d = Deck('l-trig', 'Trig Limits', 'The two special limits, and how to use them.', 'Limits')
    L = []
    L.append({'id': 'L1', 'type': 'ratio', 'title': 'The famous one', 'text': 'Plugging $x = 0$ into $frac{sin(x)}{x}$ gives $frac{0}{0}$. Move closer and closer to 0 and watch the top and the bottom.',
              'f': 'sin(x)', 'g': 'x', 'op': '/', 'a': 0, 'dir': 1, 'start': 1, 'goal': 5,
              'after': 'Up close, $sin(x)$ and $x$ are almost the same number, so their ratio heads to **1**: $lim[x->0] frac{sin(x)}{x} = 1$.'})
    L.append(MC('L2', 'The other one to know: $lim[x->0] frac{1 - cos(x)}{x} =$', ['0', '1', '$infty$', 'DNE'], hint='The top shrinks much faster than the bottom.', explain='$lim[x->0] frac{1 - cos(x)}{x} = 0$'))
    L.append(STEPS('L3', 'Use them with a little algebra. Find $lim[x->0] frac{sin(5x)}{x}$.', [
        N('L3.1', 'We want $5x$ on the bottom too. Multiply top and bottom by 5: $frac{sin(5x)}{x} = k·frac{sin(5x)}{5x}$. What is $k$?', 5, label='$k$ =', hint='$frac{5}{5} = 1$, so nothing changed.',
          work='$= 5·frac{sin(5x)}{5x}$'),
        LIM('L3.2', 'As $x -> 0$, $5x -> 0$ too, so $frac{sin(5x)}{5x} -> 1$.', 5, label='limit =', hint='$5·1$', work='limit $= 5$'),
    ]))
    L.append(LIM('L4', '$tan(x) = frac{sin(x)}{cos(x)}$, so $frac{tan(x)}{x} = frac{sin(x)}{x}·frac{1}{cos(x)}$. Find $lim[x->0] frac{tan(x)}{x}$.', 1, label='limit =',
                 hint='$1·frac{1}{cos(0)}$', explain='$1·1 = 1$'))
    L.append(LIM('L5', 'From class: $lim[x->0] frac{1 - cos(x)}{sin(x)}$. Divide top and bottom by $x$ and use the limit laws.', 0, label='limit =',
                 hint='$frac{(1 - cos(x))/x}{sin(x)/x} -> frac{0}{1}$', explain='$frac{0}{1} = 0$'))
    d.lesson(L)
    T = [
        MATCH('T1', 'Match each limit to its value.', [['$lim[x->0] frac{sin(x)}{x}$', '1'], ['$lim[x->0] frac{1 - cos(x)}{x}$', '0']], explain='Know these two by heart.'),
        TF('T2', '$lim[x->0] frac{1 - cos(x)}{x} = 1$', False, explain='It is 0. (It was a trick question in class too!)'),
        MC('T3', 'To use $lim frac{sin(u)}{u} = 1$ on $frac{sin(7x)}{x}$, you need', ['$7x$ on the bottom too', 'to plug in $x = 0$', 'to factor', 'the conjugate'], explain='Multiply top and bottom by 7.'),
        MC('T4', 'Why can you not just plug $x = 0$ into $frac{sin(x)}{x}$?', ['It gives $frac{0}{0}$', 'It gives $frac{1}{0}$', 'Sine is not continuous', 'You can; the answer is 0'], explain='$frac{0}{0}$ is indeterminate.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for a_, b_ in [(5, 1), (3, 1), (2, 3), (4, 2), (7, 7), (1, 4), (6, 5), (3, 2), (8, 1), (1, 3)]:
        Q.append(LIM(d.qid('A'), f'Find $lim[x->0] frac{{sin({a_ if a_ != 1 else ""}x)}}{{{b_ if b_ != 1 else ""}x}}$.', sp.Rational(a_, b_), label='limit =', level=2,
                     explain=f'$frac{{{a_}}}{{{b_}}}·frac{{sin({a_}x)}}{{{a_}x}} -> frac{{{a_}}}{{{b_}}}$'))
    for a_ in [4, 3, 10, 2, 6, 9]:
        Q.append(N(d.qid('K'), f'$frac{{sin({a_}x)}}{{x}} = k·frac{{sin({a_}x)}}{{{a_}x}}$. What is $k$?', a_, label='$k$ =', level=1, explain=f'Multiply top and bottom by {a_}: $k = {a_}$.'))
    for a_, b_ in [(3, 5), (2, 7), (4, 1), (6, 3), (1, 2), (5, 5)]:
        Q.append(LIM(d.qid('B'), f'Find $lim[x->0] frac{{sin({a_ if a_ != 1 else ""}x)}}{{sin({b_ if b_ != 1 else ""}x)}}$.', sp.Rational(a_, b_), label='limit =', level=3,
                     explain=f'Divide top and bottom by $x$: $frac{{{a_}}}{{{b_}}}$.'))
    for a_, b_ in [(2, 1), (3, 4), (5, 2), (1, 6), (4, 4), (7, 2)]:
        Q.append(LIM(d.qid('T'), f'Find $lim[x->0] frac{{tan({a_ if a_ != 1 else ""}x)}}{{{b_ if b_ != 1 else ""}x}}$.', sp.Rational(a_, b_), label='limit =', level=3,
                     explain=f'$tan = frac{{sin}}{{cos}}$, and $cos(0) = 1$: $frac{{{a_}}}{{{b_}}}$.'))
    for f, v in [('frac{x}{sin(x)}', 1), ('frac{1 - cos(x)}{x}', 0), ('frac{1 - cos(3x)}{x}', 0), ('frac{sin^2(x)}{x}', 0), ('frac{sin(x)}{x} + cos(x)', 2), ('frac{x + sin(x)}{x}', 2),
                 ('frac{sin(x)cos(x)}{x}', 1), ('frac{2x}{sin(3x)}', sp.Rational(2, 3)), ('x cot(x)', 1), ('frac{1 - cos(x)}{sin(x)}', 0)]:
        Q.append(LIM(d.qid('M'), f'Find $lim[x->0] {f}$.', v, label='limit =', level=2, explain=f'Use $frac{{sin(x)}}{{x}} -> 1$ and $frac{{1 - cos(x)}}{{x}} -> 0$ with the limit laws: {frac_str(v)}.'))
    for a_ in [2, 3, 6]:
        Q.append(STEPS(d.qid('W'), f'Find $lim[x->0] frac{{sin({a_}x)}}{{x}}$ one step at a time.', [
            N(None, f'Write $frac{{sin({a_}x)}}{{x}} = k·frac{{sin({a_}x)}}{{{a_}x}}$.', a_, label='$k$ =', work=f'$= {a_}·frac{{sin({a_}x)}}{{{a_}x}}$'),
            LIM(None, f'Use $frac{{sin({a_}x)}}{{{a_}x}} -> 1$.', a_, label='limit =', work=f'limit $= {a_}$'),
        ], level=3, explain=str(a_)))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 7. Limits with square roots
SQ = [('sqrt(x + 2) - 1', 'x + 1', -1, 'sqrt(x + 2) + 1', 'x + 1'), ('sqrt(x) - 2', 'x - 4', 4, 'sqrt(x) + 2', 'x - 4'), ('sqrt(x + 5) - 3', 'x - 4', 4, 'sqrt(x + 5) + 3', 'x - 4'),
      ('sqrt(x^2 + 9) - 3', 'x^2', 0, 'sqrt(x^2 + 9) + 3', 'x^2'), ('sqrt(x + 1) - 1', 'x', 0, 'sqrt(x + 1) + 1', 'x'), ('3 - sqrt(x)', '9 - x', 9, '3 + sqrt(x)', '9 - x'),
      ('sqrt(4 + x) - 2', 'x', 0, 'sqrt(4 + x) + 2', 'x'), ('sqrt(x) - 1', 'x - 1', 1, 'sqrt(x) + 1', 'x - 1'), ('sqrt(2x + 1) - 3', 'x - 4', 4, 'sqrt(2x + 1) + 3', '2x - 8'),
      ('sqrt(x + 7) - 3', 'x - 2', 2, 'sqrt(x + 7) + 3', 'x - 2'), ('sqrt(x + 9) - 3', 'x', 0, 'sqrt(x + 9) + 3', 'x'), ('2 - sqrt(x + 3)', 'x - 1', 1, '2 + sqrt(x + 3)', '1 - x')]


def deck_sqrtlim():
    d = Deck('l-sqrt', 'Limits with Square Roots', 'Multiply by the conjugate.', 'Limits')
    d.keys = ['sqrt(']
    L = []
    L.append(MC('L1', 'Find $lim[x->-1] frac{sqrt(x + 2) - 1}{x + 1}$. Plugging in gives $frac{0}{0}$, and there is a square root. Multiply top and bottom by the **conjugate** of the top, which is',
                ['$sqrt(x + 2) + 1$', '$sqrt(x + 2) - 1$', '$x + 1$', '$sqrt(x + 2)$'], hint='Flip the sign in the middle.', explain='$(a - b)(a + b) = a^2 - b^2$ gets rid of the root.'))
    L.append(STEPS('L2', 'Finish $lim[x->-1] frac{sqrt(x + 2) - 1}{x + 1}$.', [
        E(d, 'L2.1', 'Multiply out the top: $(sqrt(x + 2) - 1)(sqrt(x + 2) + 1)$.', 'x + 1', x + 1, label='top =', hint='$(x + 2) - 1$', work='$frac{x + 1}{(x + 1)(sqrt(x + 2) + 1)}$'),
        MC('L2.2', 'Cancel the $(x + 1)$. (Do not multiply out the bottom!) What is left?', ['$frac{1}{sqrt(x + 2) + 1}$', '$sqrt(x + 2) + 1$', '$frac{x + 1}{sqrt(x + 2)}$', '$1$'],
           hint='The top was $x + 1$.', work='$= frac{1}{sqrt(x + 2) + 1}$'),
        LIM('L2.3', 'Plug in $x = -1$.', sp.Rational(1, 2), label='limit =', hint='$frac{1}{sqrt(1) + 1}$', work='limit $= frac{1}{2}$'),
    ]))
    L.append(MC('L3', 'From class: a calculator falls apart on $frac{sqrt(x^2 + 9) - 3}{x^2}$ near 0 (round-off error). The conjugate gets the exact answer. Which conjugate?',
                ['$sqrt(x^2 + 9) + 3$', '$sqrt(x^2 + 9) - 3$', '$x^2 + 3$', '$sqrt(x^2) + 3$'], hint='Same as before: flip the middle sign.', explain='It simplifies to $frac{1}{sqrt(x^2 + 9) + 3} -> frac{1}{6}$.'))
    d.lesson(L)
    T = [
        MC('T1', 'The conjugate of $sqrt(x) - 5$ is', ['$sqrt(x) + 5$', '$-sqrt(x) - 5$', '$sqrt(x) - 5$', '$x - 25$'], explain='Flip the sign between the terms.'),
        MC('T2', '$(sqrt(a) - b)(sqrt(a) + b) =$', ['$a - b^2$', '$a + b^2$', '$sqrt(a) - b^2$', '$a^2 - b^2$'], explain='Difference of squares; the root disappears.'),
        TF('T3', 'After multiplying by the conjugate, you should multiply out the bottom too.', False, explain='Leave the bottom factored so the bad factor can cancel.'),
        MC('T4', 'When do you reach for the conjugate?', ['$frac{0}{0}$ with a square root in it', 'whenever there is a fraction', 'when plugging in gives a number', 'for trig limits'], explain='It is the square-root trick for $frac{0}{0}$.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for top, bot, a0, conj, newtop in SQ:
        Q.append(MC(d.qid('C'), f'What do you multiply top and bottom of $frac{{{D(top)}}}{{{D(bot)}}}$ by?', [f'${D(conj)}$', f'${D(top)}$', f'${D(bot)}$', f'${D(conj.replace("sqrt", "").replace("(", "").replace(")", ""))}$'] if False else
                    [f'${D(conj)}$', f'${D(top)}$', f'${D(bot)}$', '$sqrt(2)$'], level=1, explain=f'The conjugate ${D(conj)}$.'))
        Q.append(E(d, d.qid('U'), f'Multiply out $({D(top)})({D(conj)})$.', newtop, sp.expand(S(top) * S(conj)), label='top =', level=2, ranges={'x': [1.2, 3]}, explain=f'$= {D(newtop)}$'))
    for top, bot, a0, conj, newtop in SQ:
        e = S(top) / S(bot)
        ans = lim_of(e, a0)
        rest = sp.simplify(S(newtop) / S(bot))
        Q.append(STEPS(d.qid('W'), f'Find $lim[x->{a0}] frac{{{D(top)}}}{{{D(bot)}}}$.', [
            E(d, None, f'Multiply top and bottom by ${D(conj)}$. The top becomes', newtop, sp.expand(S(top) * S(conj)), label='top =', ranges={'x': [1.2, 3]}, work=f'$frac{{{D(newtop)}}}{{({D(bot)})({D(conj)})}}$'),
            MC(None, 'Cancel. What is left?', [f'$frac{{{num(rest)}}}{{{D(conj)}}}$', f'${D(conj)}$', f'$frac{{{D(bot)}}}{{{D(conj)}}}$', '0'], work=f'$= frac{{{num(rest)}}}{{{D(conj)}}}$'),
            LIM(None, f'Plug in $x = {a0}$.', ans, label='limit =', work=f'limit $= {frac_str(ans)}$'),
        ], level=3, explain=f'{frac_str(ans)}'))
    for top, bot, a0 in [('sqrt(x + 3)', 'x', 1), ('sqrt(x) + 2', 'x + 1', 4), ('sqrt(2x + 1)', 'x - 1', 4), ('sqrt(x^2 + 7)', 'x', 3)]:
        v = (S(top) / S(bot)).subs(x, a0)
        Q.append(LIM(d.qid('D'), f'Find $lim[x->{a0}] frac{{{D(top)}}}{{{D(bot)}}}$. (Check first: is it even $frac{{0}}{{0}}$?)', v, label='limit =', level=2, explain=f'No $frac{{0}}{{0}}$ here. Just plug in: {frac_str(v)}.'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 8. Complex fractions
CF = [('frac{1}{x + 2} + 1', 'x + 3', -3, '(x + 3)/(x + 2)', '1/(x + 2)'), ('frac{1}{x + 1} - frac{1}{2}', 'x - 1', 1, '(1 - x)/(2(x + 1))', '-1/(2(x + 1))'),
      ('frac{1}{x} - frac{1}{3}', 'x - 3', 3, '(3 - x)/(3x)', '-1/(3x)'), ('frac{1}{x} - 1', 'x - 1', 1, '(1 - x)/x', '-1/x'), ('frac{2}{x} - 1', 'x - 2', 2, '(2 - x)/x', '-1/x'),
      ('frac{1}{x + 4} - frac{1}{4}', 'x', 0, '-x/(4(x + 4))', '-1/(4(x + 4))'), ('frac{1}{x^2} - frac{1}{4}', 'x - 2', 2, '(4 - x^2)/(4x^2)', '-(2 + x)/(4x^2)'),
      ('frac{3}{x + 1} - 1', 'x - 2', 2, '(2 - x)/(x + 1)', '-1/(x + 1)'), ('frac{1}{x - 2} + frac{1}{2}', 'x', 0, 'x/(2(x - 2))', '1/(2(x - 2))'), ('1 - frac{5}{x}', 'x - 5', 5, '(x - 5)/x', '1/x')]
CS = [('frac{1}{x} + frac{5}{x(x - 5)}', 0, '1/(x - 5)'), ('frac{1}{x - 3} - frac{4}{x^2 - 2x - 3}', 3, '1/(x + 1)'), ('frac{1}{x - 1} - frac{2}{x^2 - 1}', 1, '1/(x + 1)'),
      ('frac{1}{x} - frac{1}{x^2 + x}', 0, '1/(x + 1)'), ('frac{2}{x - 2} - frac{8}{x^2 - 4}', 2, '2/(x + 2)'), ('frac{1}{x + 2} + frac{4}{x^2 - 4}', -2, '1/(x - 2)')]


def deck_complex():
    d = Deck('l-complex', 'Limits with Complex Fractions', 'Combine the little fractions first.', 'Limits')
    L = []
    L.append(MC('L1', 'Find $lim[x->-3] frac{frac{1}{x + 2} + 1}{x + 3}$. It is $frac{0}{0}$, and there are fractions inside a fraction. First combine the top over a common denominator:',
                ['$frac{1}{x + 2} + 1 = frac{x + 3}{x + 2}$', '$frac{1}{x + 2} + 1 = frac{2}{x + 2}$', '$frac{1}{x + 2} + 1 = frac{1}{x + 3}$', '$frac{1}{x + 2} + 1 = x + 3$'],
                hint='$1 = frac{x + 2}{x + 2}$', explain='$frac{1 + (x + 2)}{x + 2} = frac{x + 3}{x + 2}$'))
    L.append(STEPS('L2', 'Finish it: $frac{(x + 3)/(x + 2)}{x + 3}$.', [
        E(d, 'L2.1', 'Dividing by $x + 3$ cancels the $x + 3$ on top. What is left?', '1/(x + 2)', 1 / (x + 2), label='simplified =', ranges={'x': [0.5, 2]}, hint='$frac{x + 3}{(x + 2)(x + 3)}$',
          work='$= frac{1}{x + 2}$'),
        LIM('L2.2', 'Plug in $x = -3$.', -1, label='limit =', hint='$frac{1}{-1}$', work='limit $= -1$'),
    ]))
    L.append(LIM('L3', 'From class: $lim[x->0] (frac{1}{x} + frac{5}{x(x - 5)})$. Each piece blows up, so combine into one fraction first.', sp.Rational(-1, 5), label='limit =',
                 hint='Common denominator $x(x - 5)$: $frac{(x - 5) + 5}{x(x - 5)} = frac{1}{x - 5}$.', explain='$frac{1}{x - 5} -> -frac{1}{5}$'))
    d.lesson(L)
    T = [
        MC('T1', 'To simplify a fraction inside a fraction, first', ['combine the small fractions over a common denominator', 'plug in', 'multiply by the conjugate', 'take the derivative'], explain='Get one fraction, then cancel.'),
        TF('T2', '$lim[x->0] (frac{1}{x} + frac{5}{x(x - 5)})$ can be done with the sum law, piece by piece.', False, explain='Each piece has no limit, so the sum law does not apply. Combine first.'),
        MC('T3', '$frac{a/b}{c}$ is the same as', ['$frac{a}{bc}$', '$frac{ac}{b}$', '$frac{a}{b} + c$', '$frac{b}{ac}$'], explain='Dividing by $c$ multiplies the bottom by $c$.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for top, bot, a0, comb, simp in CF:
        tex = top.replace('frac{', '(').replace('}{', ')/(').replace('}', ')')
        Q.append(E(d, d.qid('C'), f'Combine into one fraction: ${top}$', comb, sp.together(S(tex)), label='combined =', level=1, ranges={'x': [6, 8]}, explain=f'$= {D(comb)}$'))
    for top, bot, a0, comb, simp in CF:
        Q.append(E(d, d.qid('S'), f'Simplify $frac{{{top}}}{{{D(bot)}}}$, using ${top} = {D(comb)}$.', simp, sp.simplify(S(comb) / S(bot)), label='simplified =', level=2, ranges={'x': [6, 8]},
                   explain=f'Cancel ${D(bot)}$: ${D(simp)}$.'))
    for top, bot, a0, comb, simp in CF:
        ans = sp.simplify(S(simp).subs(x, a0))
        Q.append(STEPS(d.qid('W'), f'Find $lim[x->{a0}] frac{{{top}}}{{{D(bot)}}}$.', [
            E(d, None, 'Combine the top into one fraction.', comb, S(comb), label='top =', ranges={'x': [6, 8]}, work=f'top $= {D(comb)}$'),
            E(d, None, 'Divide by the bottom and cancel.', simp, S(simp), label='simplified =', ranges={'x': [6, 8]}, work=f'$= {D(simp)}$'),
            LIM(None, 'Plug in.', ans, label='limit =', work=f'limit $= {frac_str(ans)}$'),
        ], level=3, explain=frac_str(ans)))
    for e_, a0, simp in CS:
        ans = S(simp).subs(x, a0)
        Q.append(STEPS(d.qid('V'), f'Find $lim[x->{a0}] ({e_})$.', [
            E(d, None, 'Combine into one fraction and cancel.', simp, S(simp), label='simplified =', ranges={'x': [6, 8]}, work=f'$= {D(simp)}$'),
            LIM(None, 'Plug in.', ans, label='limit =', work=f'limit $= {frac_str(ans)}$'),
        ], level=3, explain=frac_str(ans)))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 9. Combo limits (which tool?)
TOOLS = ['Plug in (it is just a number)', 'Infinite limit: check the signs', 'Factor and cancel', 'Multiply by the conjugate', 'Combine fractions', 'Squeeze Theorem', 'Special trig limit']
COMBO = [('frac{x^2 + 1}{x + 2}', 1, 0), ('frac{x^2 - 9}{x - 3}', 3, 2), ('frac{sqrt(x) - 2}{x - 4}', 4, 3), ('frac{frac{1}{x} - frac{1}{2}}{x - 2}', 2, 4), ('x^2 cos(frac{1}{x})', 0, 5),
         ('frac{sin(3x)}{x}', 0, 6), ('frac{x + 1}{(x - 2)^2}', 2, 1), ('frac{x^2 + x - 6}{x - 2}', 2, 2), ('frac{x}{sqrt(x + 1) - 1}', 0, 3), ('frac{1}{x} - frac{1}{x^2 + x}', 0, 4),
         ('frac{3x - 1}{x - 5}', 5, 1), ('sqrt(x^2 + 7)', 3, 0), ('frac{tan(x)}{2x}', 0, 6), ('x sin(frac{1}{x})', 0, 5), ('frac{x^3 - 1}{x - 1}', 1, 2), ('frac{3 - sqrt(x)}{9 - x}', 9, 3),
         ('cos(x) + x^3', 0, 0), ('frac{1 - cos(x)}{x}', 0, 6)]
MIXED = [('(x^2 - 9)/(x - 3)', 'frac{x^2 - 9}{x - 3}', 3), ('(sqrt(x) - 2)/(x - 4)', 'frac{sqrt(x) - 2}{x - 4}', 4), ('(1/x - 1/2)/(x - 2)', 'frac{1/x - 1/2}{x - 2}', 2),
         ('sin(3x)/x', 'frac{sin(3x)}{x}', 0), ('(x + 1)/(x - 2)^2', 'frac{x + 1}{(x - 2)^2}', 2), ('(x^2 + x - 6)/(x - 2)', 'frac{x^2 + x - 6}{x - 2}', 2), ('x/(sqrt(x + 1) - 1)', 'frac{x}{sqrt(x + 1) - 1}', 0),
         ('(3x - 1)/(x - 5)', 'frac{3x - 1}{x - 5}', 5), ('tan(x)/(2x)', 'frac{tan(x)}{2x}', 0), ('(x^3 - 1)/(x - 1)', 'frac{x^3 - 1}{x - 1}', 1), ('(3 - sqrt(x))/(9 - x)', 'frac{3 - sqrt(x)}{9 - x}', 9),
         ('(x^2 + 2)/(x - 1)', 'frac{x^2 + 2}{x - 1}', 1), ('cos(x)/abs(pi - x)', 'frac{cos(x)}{|pi - x|}', 'pi'), ('(x^2 - 4)/(x^2 - 5x + 6)', 'frac{x^2 - 4}{x^2 - 5x + 6}', 2),
         ('(sqrt(x^2 + 9) - 3)/x^2', 'frac{sqrt(x^2 + 9) - 3}{x^2}', 0), ('(x - 3)/(x^2 - 2x - 4)', 'frac{x - 3}{x^2 - 2x - 4}', 3), ('(1 - cos(x))/sin(x)', 'frac{1 - cos(x)}{sin(x)}', 0),
         ('(x^2 + 4)/(x - 2)^2', 'frac{x^2 + 4}{(x - 2)^2}', 2), ('(x^2 - 4)/(x - 2)', 'frac{x^2 - 4}{x - 2}', 2), ('sin(x^2 + pi/2)', 'sin(x^2 + frac{pi}{2})', 0),
         ('(2x + 1)/(-x - 2)', 'frac{2x + 1}{-x - 2}', 2), ('(x^2 + 2x + 1)/(x - 1)^2', 'frac{x^2 + 2x + 1}{(x - 1)^2}', 1), ('(5 - 2x)/(x - 3)', 'frac{5 - 2x}{x - 3}', 3),
         ('sin(5x)/sin(2x)', 'frac{sin(5x)}{sin(2x)}', 0)]


def deck_combo():
    d = Deck('l-combo', 'Combo Limits', 'Pick the right tool for each limit.', 'Limits')
    L = []
    L.append(MC('L1', 'Every limit starts the same way: **plug in**. You get one of three things. Which one means you are done?', ['a number', '$frac{a}{0}$ with $a ≠ 0$', '$frac{0}{0}$'], fixed=True,
                hint='Which one is already an answer?', explain='A number is the limit. $frac{a}{0}$ means an infinite limit or DNE. $frac{0}{0}$ means use a trick.'))
    L.append(MC('L2', 'Plugging in gives $frac{0}{0}$. Match the clue to the trick: the expression has a **square root**.', ['Multiply by the conjugate', 'Factor and cancel', 'Combine fractions', 'Squeeze Theorem'],
                hint='Which trick gets rid of a root?', explain='Conjugate: $(a - b)(a + b) = a^2 - b^2$.'))
    L.append(MATCH('L3', 'Match each clue to its tool.', [['polynomials on top and bottom', 'Factor and cancel'], ['a square root', 'Multiply by the conjugate'], ['fractions inside a fraction', 'Combine fractions'],
                   ['a wiggly $sin(frac{1}{x})$ piece', 'Squeeze Theorem'], ['$sin(kx)$ over $x$', 'Special trig limit']], hint='One tool for each clue.', explain='That is the whole flow chart.'))
    d.lesson(L)
    T = [
        TF('T1', 'For $lim[x->a] f(x)$ to exist, $f(x)$ must be defined at $x = a$.', False, explain='A limit ignores the point itself.'),
        TF('T2', 'If $lim[x->2] f(x) = 0$ and $lim[x->2] g(x) = 0$, then $lim[x->2] frac{f(x)}{g(x)}$ does not exist.', False, explain='$frac{0}{0}$ is indeterminate; it can be anything.'),
        TF('T3', 'If $p$ is a polynomial, then $lim[x->a] p(x) = p(a)$.', True, explain='Direct substitution.'),
        TF('T4', 'If $lim[x->a] (f(x) - g(x))$ exists, then it must equal $lim[x->a] f(x) - lim[x->a] g(x)$.', False, explain='$f$ and $g$ might not have limits on their own (like $frac{1}{x}$ and $frac{1}{x}$).'),
        TF('T5', '$lim[x->3] frac{x - 3}{x^2 - 2x - 4} = frac{lim[x->3] (x - 3)}{lim[x->3] (x^2 - 2x - 4)}$', True, explain='The bottom goes to $9 - 6 - 4 = -1 ≠ 0$, so the quotient law applies.'),
        TF('T6', '$lim[x->2] sin(g(x)) = sin(lim[x->2] g(x))$, if $lim[x->2] g(x)$ exists.', True, explain='Sine is continuous, so the limit passes inside.'),
        TF('T7', 'If you plug in and get $frac{a}{0}$, this is an "indeterminate form" and could be any number.', False, explain='$frac{a}{0}$ with $a ≠ 0$ is an infinite limit or DNE. Only $frac{0}{0}$ is indeterminate.'),
        TF('T8', '$lim[x->0] frac{1 - cos(x)}{x} = 1$', False, explain='It is 0.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for f, a0, k in COMBO:
        o = [TOOLS[k]] + [t for t in TOOLS if t != TOOLS[k]]
        o = [o[0]] + R.sample(o[1:], 3)
        Q.append(MC(d.qid('W'), f'What is the best tool for $lim[x->{a0}] {f}$?', o, level=1, explain=f'{TOOLS[k]}.'))
    for src, disp, a0 in MIXED:
        e = S(src)
        ans = lim_of(e, S(str(a0)))
        Q.append(LIM(d.qid('M'), f'Find $lim[x->{D(str(a0))}] {disp}$.', ans, label='limit =', level=2 if R.random() < 0.5 else 3,
                     explain='Plug in first, then use the right tool. ' + (f'The limit is {frac_str(ans)}.' if not isinstance(ans, str) else {'inf': 'It blows up to $infty$.', '-inf': 'It goes to $-infty$.', 'DNE': 'It does not exist.'}[ans])))
        for side in (['^-', '^+'] if isinstance(ans, str) and ans == 'DNE' else []):
            a2 = lim_of(e, S(str(a0)), side[1])
            Q.append(LIM(d.qid('O'), f'Find $lim[x->{D(str(a0))}{side}] {disp}$.', a2, label='limit =', level=3, explain='Check the sign of the top and bottom on that side.'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 10. Continuity
def deck_cont():
    d = Deck('l-cont', 'Continuity', 'No holes, no jumps, no blow-ups.', 'Limits')
    gR = d.graph('rem', {'window': [-1, 4, -1, 5], 'pieces': [{'expr': 'x+1', 'from': -1, 'to': 4}], 'holes': [[2, 3]], 'dots': [[2, 4.5]]})
    gJ = d.graph('jump', {'window': [-1, 4, -1, 5], 'pieces': [{'expr': 'x+1', 'from': -1, 'to': 2}, {'expr': 'x-1', 'from': 2, 'to': 4}], 'holes': [[2, 3]], 'dots': [[2, 1]]})
    gI = d.graph('inf', {'window': [-1, 4, -5, 5], 'pieces': [{'expr': '1/(x-2)', 'from': -1, 'to': 1.8}, {'expr': '1/(x-2)', 'from': 2.2, 'to': 4}], 'vlines': [2]})
    gC = d.graph('cont', {'window': [-1, 4, -1, 5], 'pieces': [{'expr': '(x-1)^2', 'from': -1, 'to': 3.2}]})
    gU = d.graph('undef', {'window': [-1, 4, -1, 5], 'pieces': [{'expr': '4-x', 'from': -1, 'to': 4}], 'holes': [[2, 2]]})
    L = []
    L.append(ORDER('L1', 'A function is **continuous** at $x = a$ when three things are true. Put them in the order you check them.', ['$f(a)$ is defined', '$lim[x->a] f(x)$ exists', '$lim[x->a] f(x) = f(a)$'],
                   hint='First the point, then the limit, then compare.', explain='Informally: you can draw it through $x = a$ without lifting your pencil.'))
    L.append(dict(MC('L2', 'This graph is not continuous at $x = 2$. Which condition fails?', ['$lim[x->2] f(x) ≠ f(2)$', '$f(2)$ is undefined', 'the limit does not exist', 'none: it is continuous'],
                     hint='There is a dot at $x = 2$, and the curve heads somewhere else.', explain='The limit is 3 but $f(2) = 4.5$. This is a **removable** discontinuity.'), graph=gR))
    L.append(dict(MC('L3', 'Which kind of discontinuity is this?', ['jump', 'removable', 'infinite', 'it is continuous'], hint='Do the two sides meet?', explain='The two sides go to different heights: a **jump**.'), graph=gJ))
    L.append(N('L4', 'Piecewise functions: $f(x) = x^2 + k$ for $x < 2$ and $f(x) = 3x$ for $x >= 2$. What $k$ makes $f$ continuous at $x = 2$?', 2, label='$k$ =',
               hint='Make the two pieces meet at $x = 2$: $4 + k = 6$.', explain='$k = 2$'))
    L.append(MC('L5', '**Intermediate Value Theorem:** if $f$ is continuous on $[a, b]$, it hits every height between $f(a)$ and $f(b)$. $f(x) = x^3 - x^2 - 3x + 1$ has $f(0) = 1$ and $f(1) = -2$. So on $[0, 1]$ it…',
                ['has at least one zero', 'has no zeros', 'has exactly two zeros', 'is never negative'], hint='Is 0 between 1 and −2?', explain='0 is between 1 and −2, so $f(c) = 0$ for some $c$ in $(0, 1)$.'))
    d.lesson(L)
    T = [
        PICK('T1', 'Which are part of the definition of "continuous at $x = a$"? Select all.', ['$f(a)$ is defined', '$lim[x->a] f(x)$ exists', '$lim[x->a] f(x) = f(a)$', '$f(a) = 0$', "$f'(a)$ exists"], [0, 1, 2],
             explain='Just those three.'),
        MATCH('T2', 'Match each discontinuity to its description.', [['removable', 'a hole (a single point is off)'], ['jump', 'the two sides go to different heights'], ['infinite', 'a vertical asymptote']],
              explain='Removable ones can be fixed by redefining one point.'),
        TF('T3', 'Polynomials are continuous everywhere.', True, explain='No holes, jumps or asymptotes.'),
        TF('T4', 'Rational functions are continuous everywhere on their domains.', True, explain='They only break where the bottom is 0.'),
        MC('T5', 'If $f$ is continuous at $a$, then $lim[x->a] f(x) =$', ['$f(a)$', '0', 'DNE', '$infty$'], explain='That is what makes plugging in work.'),
        MC('T6', 'The Intermediate Value Theorem needs $f$ to be', ['continuous on $[a, b]$', 'differentiable', 'a polynomial', 'increasing'], explain='A break could let $f$ skip over a height.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    graphs = [(gR, 'No: the limit and the value are different', 'removable'), (gJ, 'No: the limit does not exist', 'jump'), (gI, 'No: the function blows up', 'infinite'),
              (gC, 'Yes', None), (gU, 'No: $f(2)$ is undefined', 'removable')]
    copts = ['Yes', 'No: $f(2)$ is undefined', 'No: the limit does not exist', 'No: the limit and the value are different', 'No: the function blows up']
    for g, why, kind in graphs:
        Q.append(dict(MC(d.qid('G'), 'Is $f$ continuous at $x = 2$?', copts, copts.index(why), fixed=True, level=1, explain=why + '.'), graph=g))
        if kind:
            Q.append(dict(MC(d.qid('K'), 'What kind of discontinuity is at $x = 2$?', ['removable', 'jump', 'infinite'], ['removable', 'jump', 'infinite'].index(kind), fixed=True, level=2,
                             explain=kind.capitalize() + '.'), graph=g))
    pw = [('x^2 + k', '3x', 2), ('kx + 1', 'x^2', 3), ('k - x', '2x + 1', 1), ('kx^2', 'x + 6', 2), ('x + k', 'x^3', 2), ('2x + k', '5 - x', 1), ('kx', 'x^2 + 4', 2), ('k', 'sqrt(x)', 9)]
    k = sp.Symbol('k')
    for left, right, a0 in pw:
        kv = sp.solve(sp.Eq(S(left.replace('k', '(K)')).subs(sp.Symbol('K'), k).subs(x, a0), S(right).subs(x, a0)), k)[0]
        Q.append(N(d.qid('P'), f'$f(x) = {D(left, False)}$ for $x < {a0}$ and $f(x) = {D(right, False)}$ for $x >= {a0}$. What $k$ makes $f$ continuous at $x = {a0}$?', kv, label='$k$ =', level=2,
                   explain=f'Make the pieces meet at $x = {a0}$: $k = {frac_str(kv)}$.'))
    pcheck = [('-x^2 + 4', '4x - 8', 3, False), ('x + 1', 'x^2 + 1', 1, True), ('2x', 'x^2', 2, True), ('x^2', 'x + 3', 2, False), ('3 - x', 'x - 1', 2, True), ('sqrt(x)', 'x - 1', 4, False)]
    for left, right, a0, ok in pcheck:
        lv, rv = S(left).subs(x, a0), S(right).subs(x, a0)
        assert (lv == rv) == ok
        Q.append(MC(d.qid('C'), f'$f(x) = {D(left, False)}$ for $x < {a0}$ and $f(x) = {D(right, False)}$ for $x >= {a0}$. Is $f$ continuous at $x = {a0}$?', ['Yes', 'No'], 0 if ok else 1, fixed=True, level=2,
                    explain=f'Left side → {num(lv)}, right side and $f({a0})$ = {num(rv)}. ' + ('They match.' if ok else 'They do not match.')))
    where = [('frac{x^2 - 4}{x - 2}', '$x = 2$ only', ['nowhere', '$x = 2$ and $x = -2$', '$x = 4$']), ('frac{1}{x^2 - 9}', '$x = 3$ and $x = -3$', ['$x = 9$ only', '$x = 3$ only', 'nowhere']),
             ('x^3 - 5x + 1', 'nowhere', ['$x = 0$', '$x = 5$', '$x = 1$']), ('frac{x}{x^2 + 1}', 'nowhere', ['$x = 1$ and $x = -1$', '$x = 0$', '$x = -1$ only']),
             ('tan(x)', '$x = frac{pi}{2} + kpi$ (odd multiples of $frac{pi}{2}$)', ['$x = kpi$', 'nowhere', '$x = 0$ only']), ('frac{x + 1}{x(x - 5)}', '$x = 0$ and $x = 5$', ['$x = -1$', '$x = 5$ only', 'nowhere'])]
    for f, r_, w_ in where:
        Q.append(MC(d.qid('W'), f'Where is $f(x) = {f}$ discontinuous?', [r_] + w_, level=2, explain=r_ + '.'))
    for f, a0, b0, ok in [('x^3 - x^2 - 3x + 1', 0, 1, True), ('x^2 - 2', 1, 2, True), ('x^2 + 1', -1, 1, False), ('cos(x) - x', 0, 1, True), ('x^3 + x + 1', -1, 0, True), ('x^2 - 4x + 5', 0, 3, False)]:
        fa, fb = S(f).subs(x, a0), S(f).subs(x, b0)
        sure = bool(fa * fb < 0)
        assert sure == ok
        Q.append(MC(d.qid('I'), f'$f(x) = {D(f)}$. $f({a0}) = {num(fa)}$ and $f({b0}) = {num(fb)}$. Does the Intermediate Value Theorem promise a zero in $({a0}, {b0})$?',
                    ['Yes', 'No'], 0 if ok else 1, fixed=True, level=3, explain=('0 is between them, and $f$ is continuous.' if ok else 'Both values have the same sign, so the IVT promises nothing.')))
    for f, a0, v in [('sin(x^2 + frac{pi}{2})', 0, 1), ('cos(frac{pi x}{3})', 1, sp.Rational(1, 2)), ('sqrt(x^2 + 16)', 3, 5), ('e^(x - 1)', 1, 1), ('ln(x^2 + 1)', 0, 0), ('frac{x^2 + 1}{x + 1}', 1, 1)]:
        Q.append(LIM(d.qid('V'), f'This function is continuous at $x = {a0}$. Find $lim[x->{a0}] {f}$.', v, label='limit =', level=1, explain=f'Continuous, so just plug in: {frac_str(v)}.'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== 11. Limits at infinity
def deck_atinf():
    d = Deck('l-atinf', 'Limits at Infinity', 'What a function does far out on the ends.', 'Limits')
    gH = d.graph('hyp', {'window': [-9, 9, -5, 5], 'pieces': [{'expr': '2+1/x', 'from': -9, 'to': -0.2}, {'expr': '2+1/x', 'from': 0.2, 'to': 9}], 'xstep': 2})
    L = []
    L.append(dict(LIM('L1', '$f(x) = 2 + frac{1}{x}$. As $x$ gets huge (10, 100, 1000…), $f(x)$ is 2.1, 2.01, 2.001… Find $lim[x->infty] f(x)$.', 2, label='$lim[x->infty] f(x)$ =',
                      hint='What are the values closing in on?', explain='$y = 2$ is a **horizontal asymptote**.'), graph=gH))
    L.append(LIM('L2', 'Polynomials never level off: they go to $infty$ or $-infty$, and only the **leading term** matters. Find $lim[x->-infty] (x^3 + 2x - 1)$.', '-inf', label='limit =',
                 hint='$x^3$ for a huge negative $x$ is a huge negative number.', explain='$-infty$'))
    L.append(LIM('L3', 'Rational functions: compare leading terms. $lim[x->infty] frac{3x^2 + x - 1}{x^4 + 2x - 2}$ behaves like $frac{3x^2}{x^4} = frac{3}{x^2}$. So the limit is', 0, label='limit =',
                 hint='$frac{3}{x^2}$ when $x$ is huge.', explain='Bottom wins: 0.'))
    L.append(LIM('L4', 'Same degree on top and bottom: $lim[x->infty] frac{-3x^4 - 2}{3x^4 + x}$ behaves like $frac{-3x^4}{3x^4}$.', -1, label='limit =', hint='The $x^4$ cancels.', explain='$-1$'))
    L.append(LIM('L5', 'Top wins: $lim[x->infty] frac{2x^6 - 1}{3x^3 + x - 7}$ behaves like $frac{2x^6}{3x^3} = frac{2}{3}x^3$.', 'inf', label='limit =', hint='$frac{2}{3}x^3$ for huge $x$.', explain='$infty$'))
    d.lesson(L)
    T = [
        MATCH('T1', 'For $lim[x->infty] frac{p(x)}{q(x)}$, match the degrees to the answer.', [['degree of top < degree of bottom', '0'], ['degrees equal', 'ratio of the leading coefficients'],
              ['degree of top > degree of bottom', '$infty$ or $-infty$']], explain='Leading order is all that matters at infinity!'),
        MC('T2', 'If $lim[x->infty] f(x) = L$, then the graph has', ['a horizontal asymptote $y = L$', 'a vertical asymptote $x = L$', 'a hole at $L$', 'a zero at $L$'], explain='It levels off at height $L$.'),
        LIM('T3', 'Find $lim[x->infty] sin(x)$.', 'DNE', label='limit =', explain='Sine keeps waving between −1 and 1 forever, so it never settles.'),
        LIM('T4', 'Find $lim[x->-infty] e^x$.', 0, label='limit =', explain='$e^x$ shrinks toward 0 on the left.'),
        LIM('T5', 'Find $lim[x->infty] ln(x)$.', 'inf', label='limit =', explain='Slowly, but it grows without bound.'),
        MC('T6', 'For $f(x) = -x^4$, the end behavior is', ['down on both ends', 'up on both ends', 'down on the left, up on the right', 'up on the left, down on the right'], explain='Even power, negative leading coefficient.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    polys = ['-x^4', '2x^3', '-x^5/2', 'x^3 + 2x - 1', '2x^8 + 32x^2 - x - 4', '2x^4 - x - 100', '5x^3 - 3x^2 + 4', '-3x^2 + x', '7 - x^3', 'x^6 - x^7']
    for f in polys:
        for side in ['infty', '-infty']:
            ans = sp.limit(S(f), x, sp.oo if side == 'infty' else -sp.oo)
            a = 'inf' if ans == sp.oo else '-inf'
            Q.append(LIM(d.qid('P'), f'Find $lim[x->{side}] ({D(f, False)})$.', a, label='limit =', level=1, explain='Only the leading term matters.'))
    rats = [('(3x^2 + x - 1)/(x^4 + 2x - 2)', 'frac{3x^2 + x - 1}{x^4 + 2x - 2}'), ('(3x^3 + x - 1)/(x^4 + 2x - 2)', 'frac{3x^3 + x - 1}{x^4 + 2x - 2}'), ('(3x^5 + x - 1)/(x^4 + 2x - 2)', 'frac{3x^5 + x - 1}{x^4 + 2x - 2}'),
            ('(2x^6 - 1)/(3x^3 + x - 7)', 'frac{2x^6 - 1}{3x^3 + x - 7}'), ('(-3x^4 - 2)/(3x^4 + x)', 'frac{-3x^4 - 2}{3x^4 + x}'), ('(-x^4 - 2x - 1)/(3x^7 + x)', 'frac{-x^4 - 2x - 1}{3x^7 + x}'),
            ('(4x^2 + 1)/(2x^2 - 5)', 'frac{4x^2 + 1}{2x^2 - 5}'), ('(5x - 3)/(x + 1)', 'frac{5x - 3}{x + 1}'), ('(x^3 + 1)/(2x - 1)', 'frac{x^3 + 1}{2x - 1}'), ('(7x)/(x^2 + 1)', 'frac{7x}{x^2 + 1}'),
            ('(3e^x + 4x - 1)/(-5e^x - 2)', 'frac{3e^x + 4x - 1}{-5e^x - 2}'), ('(1 - x^2)/(x^2 + x)', 'frac{1 - x^2}{x^2 + x}')]
    for src, disp in rats:
        for side in (['infty', '-infty'] if 'e^x' not in src else ['infty']):
            ans = sp.limit(S(src), x, sp.oo if side == 'infty' else -sp.oo)
            a = 'inf' if ans == sp.oo else '-inf' if ans == -sp.oo else ans
            Q.append(LIM(d.qid('R'), f'Find $lim[x->{side}] {disp}$.', a, label='limit =', level=2, explain='Compare the leading terms of the top and bottom.'))
    roots = [('sqrt(3x^6 + x - 1)/(x^4 + 2x - 2)', 'frac{sqrt(3x^6 + x - 1)}{x^4 + 2x - 2}'), ('sqrt(3x^6 + x - 1)/(x^2 + 2x - 2)', 'frac{sqrt(3x^6 + x - 1)}{x^2 + 2x - 2}'),
             ('sqrt(3x - 1)/(x^2 + 2x - 2)', 'frac{sqrt(3x - 1)}{x^2 + 2x - 2}'), ('sqrt(3x^2 + 4)/(x + 6)', 'frac{sqrt(3x^2 + 4)}{x + 6}'), ('sqrt(4x^2 + 1)/(2x - 3)', 'frac{sqrt(4x^2 + 1)}{2x - 3}')]
    for src, disp in roots:
        for side in ['infty', '-infty']:
            if 'sqrt(3x - 1)' in src and side == '-infty':
                continue
            ans = sp.limit(S(src), x, sp.oo if side == 'infty' else -sp.oo)
            a = 'inf' if ans == sp.oo else '-inf' if ans == -sp.oo else ans
            Q.append(LIM(d.qid('Q'), f'Find $lim[x->{side}] {disp}$. (A decimal is fine.)', a, label='limit =', tol=0.01, level=3,
                         explain='$sqrt(x^2) = |x|$, which is $-x$ when $x$ is negative. Compare leading terms.'))
    for f, side, a in [('e^x', 'infty', 'inf'), ('e^x', '-infty', 0), ('e^(-x)', 'infty', 0), ('ln(x)', 'infty', 'inf'), ('arctan(x)', 'infty', sp.pi / 2), ('arctan(x)', '-infty', -sp.pi / 2),
                       ('sin(x)', 'infty', 'DNE'), ('cos(x)', '-infty', 'DNE'), ('frac{sin(x)}{x}', 'infty', 0), ('2 + frac{1}{x}', '-infty', 2)]:
        Q.append(LIM(d.qid('E'), f'Find $lim[x->{side}] {f}$.' + (' (A decimal is fine.)' if a in (sp.pi / 2, -sp.pi / 2) else ''), a, label='limit =', tol=0.01, level=2,
                     explain={'DNE': 'It keeps oscillating, so there is no limit.'}.get(a if isinstance(a, str) else '', f'The limit is {a if isinstance(a, str) else num(a)}.')))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


# ====================================================================== review side quests
def deck_evaluate():
    d = Deck('l-evaluate', 'Evaluate Functions', 'Review: plug numbers into formulas, pieces and graphs.', 'Limits')
    gP = d.graph('pg', {'window': [-3, 4, -1, 6], 'pieces': [{'expr': 'x+3', 'from': -3, 'to': 1}, {'expr': '5-x', 'from': 1, 'to': 4}], 'holes': [[1, 4]], 'dots': [[1, 2]]})
    L = [
        N('L1', '$f(x) = x^2 - 3x$. To find $f(-2)$, replace every $x$ with $(-2)$: $(-2)^2 - 3(-2)$.', 10, label='$f(-2)$ =', hint='$4 + 6$', explain='Parentheses keep the signs right: 10.'),
        N('L2', 'Piecewise: $f(x) = x + 1$ for $x < 2$ and $f(x) = x^2$ for $x >= 2$. Find $f(2)$.', 4, label='$f(2)$ =', hint='$x = 2$ belongs to the piece with $>=$.', explain='$2^2 = 4$'),
    ]
    d.lesson(L, optional=True)
    Q = []
    for f, a0 in [('x^2 - 3x', -2), ('2x^3 - x', 2), ('5 - x^2', -3), ('x^2 + 4x + 4', -2), ('(x - 1)(x + 5)', 3), ('-x^2', 4), ('3x^4', -1), ('x^3 - x^2 - 3x + 1', 1), ('7', 100), ('4x - x^3', -2)]:
        Q.append(N(d.qid('P'), f'$f(x) = {D(f)}$. Find $f({a0})$.', S(f).subs(x, a0), label=f'$f({a0})$ =', level=1, explain=f'{num(S(f).subs(x, a0))}'))
    for f, src, a0 in [('frac{x + 1}{x - 2}', '(x + 1)/(x - 2)', 4), ('frac{x^2}{x + 3}', 'x^2/(x + 3)', -1), ('sqrt(x + 7)', 'sqrt(x + 7)', 9), ('frac{1}{x} + x', '1/x + x', 2),
                       ('sqrt(25 - x^2)', 'sqrt(25 - x^2)', 3), ('frac{2x - 1}{x^2 + 1}', '(2x - 1)/(x^2 + 1)', 1), ('|x - 5|', 'abs(x - 5)', 2), ('sin(frac{pi x}{2})', 'sin(pi x/2)', 1)]:
        Q.append(N(d.qid('R'), f'$f(x) = {f}$. Find $f({a0})$.', S(src).subs(x, a0), label=f'$f({a0})$ =', level=1, explain=f'{frac_str(S(src).subs(x, a0))}'))
    for l_, r_, c, a0 in [('x + 1', 'x^2', 2, 2), ('x + 1', 'x^2', 2, 1), ('3 - x', '2x', 0, 0), ('3 - x', '2x', 0, -4), ('x^2', '10 - x', 3, 3), ('x^2', '10 - x', 3, 5), ('-x', 'x + 4', -1, -1), ('5', 'x^3', 1, 2)]:
        v = S(l_).subs(x, a0) if a0 < c else S(r_).subs(x, a0)
        Q.append(N(d.qid('W'), f'$f(x) = {D(l_)}$ for $x < {c}$ and $f(x) = {D(r_)}$ for $x >= {c}$. Find $f({a0})$.', v, label=f'$f({a0})$ =', level=2,
                   explain=f'${a0} {"<" if a0 < c else ">="} {c}$, so use ${D(l_ if a0 < c else r_)}$: {num(v)}.'))
    for at in [-2, 0, 1, 3, -3, 2]:
        Q.append({'id': d.qid('G'), 'type': 'graph', 'graph': gP, 'ask': 'value', 'at': at, 'answer': None, 'level': 2, 'explain': 'Read the height of the graph (the filled point) right at that $x$.'})
    for f, a0 in [('x^2', 3), ('x^2 + x', 1), ('2x^2 - 1', 2), ('x^2 - 4x', -1), ('3x + 5', 2), ('x^3', 1)]:
        val = sp.expand(S(f).subs(x, a0 + h))
        Q.append(E(d, d.qid('H'), f'$f(x) = {D(f)}$. Find $f({a0} + h)$ and multiply it out.', sp_app(val), val, ['h'], label=f'$f({a0} + h)$ =', level=3, explain=f'${D(sp_app(val))}$'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()
    graphtruth(os.path.join(ROOT, 'decks', 'l-evaluate.json'))


def deck_vasym():
    d = Deck('l-vasym', 'Vertical Asymptotes', 'Review: where the bottom is 0 (and does not cancel).', 'Limits')
    L = [
        MC('L1', 'A rational function has a **vertical asymptote** where the bottom is 0 and the top is not. Where is the vertical asymptote of $f(x) = frac{x + 1}{x - 3}$?', ['$x = 3$', '$x = -1$', '$x = 1$', 'there is none'],
           hint='Set the bottom equal to 0.', explain='$x - 3 = 0$ at $x = 3$, and the top is 4 there.'),
        MC('L2', 'Careful: $f(x) = frac{x^2 - 4}{x - 2}$ has bottom 0 at $x = 2$, but the top is 0 too. It cancels to $x + 2$. So at $x = 2$ there is', ['a hole, not an asymptote', 'a vertical asymptote', 'a jump', 'nothing at all'],
           hint='Does the $(x - 2)$ cancel?', explain='Canceled factors make holes. Only factors left on the bottom make asymptotes.'),
    ]
    d.lesson(L, optional=True)
    Q = []
    items = [('frac{x + 1}{x - 3}', [3]), ('frac{2}{x^2 - 9}', [3, -3]), ('frac{x^2 - 4}{x - 2}', []), ('frac{x}{x^2 + 1}', []), ('frac{x - 1}{x^2 - x - 6}', [3, -2]),
             ('frac{x + 2}{x^2 - 4}', [2]), ('frac{5}{x}', [0]), ('frac{x^2}{(x - 1)^2}', [1]), ('frac{x + 3}{x^2 + 5x + 6}', [-2]), ('frac{1}{x^2 - 5x}', [0, 5]),
             ('frac{3x}{2x - 1}', [0.5]), ('frac{x^2 + 1}{x^3 - x}', [0, 1, -1]), ('frac{x - 4}{x^2 - 16}', [-4]), ('frac{1}{x^2 + 4}', []), ('frac{2x + 6}{x + 3}', []), ('frac{x}{x^2 - 2x + 1}', [1])]
    for f, ans in items:
        Q.append({'id': d.qid('A'), 'type': 'crit', 'text': f'List every vertical asymptote of $f(x) = {f}$.', 'answers': ans, 'var': 'x', 'label': 'Asymptote at $x$ =',
                  'noneText': 'There are none', 'level': 2 if len(ans) != 1 else 1, 'explain': 'Bottom = 0 and the factor does not cancel: ' + (', '.join(f'$x = {a}$' for a in ans) if ans else 'none') + '.'})
    for f, a0, kind in [('frac{x^2 - 4}{x - 2}', 2, 'hole'), ('frac{x + 1}{x - 3}', 3, 'asymptote'), ('frac{x^2 - 1}{x + 1}', -1, 'hole'), ('frac{x}{x^2 - 9}', 3, 'asymptote'),
                        ('frac{x - 5}{x^2 - 25}', 5, 'hole'), ('frac{x - 5}{x^2 - 25}', -5, 'asymptote'), ('frac{x^2 + x}{x}', 0, 'hole'), ('frac{1}{(x - 2)^2}', 2, 'asymptote')]:
        Q.append(MC(d.qid('H'), f'At $x = {a0}$, does $f(x) = {f}$ have a hole or a vertical asymptote?', ['a hole', 'a vertical asymptote'], 0 if kind == 'hole' else 1, fixed=True, level=3,
                    explain='The factor cancels: a hole.' if kind == 'hole' else 'The factor stays on the bottom: an asymptote.'))
    for f, z in [('2x - 6', 3), ('x + 7', -7), ('4x + 2', -0.5), ('3x', 0), ('5 - x', 5), ('6x - 4', sp.Rational(2, 3))]:
        Q.append(N(d.qid('Z'), f'Solve ${D(f)} = 0$.', z, label='$x$ =', level=1, explain=f'$x = {frac_str(z)}$'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


def deck_sqroots():
    d = Deck('l-sqroots', 'Square Roots', 'Review: simplify roots and use conjugates.', 'Limits')
    d.keys = ['sqrt(']
    L = [
        E(d, 'L1', 'Pull perfect squares out of a root: $sqrt(50) = sqrt(25·2) = 5sqrt(2)$. Simplify $sqrt(12)$.', '2sqrt(3)', 2 * sp.sqrt(3), [], label='$sqrt(12)$ =', hint='$12 = 4·3$', explain='$2sqrt(3)$'),
        E(d, 'L2', 'Conjugates: $(a - b)(a + b) = a^2 - b^2$, and the root disappears. Multiply out $(sqrt(x) - 3)(sqrt(x) + 3)$.', 'x - 9', x - 9, label='product =', hint='$(sqrt(x))^2 - 3^2$', explain='$x - 9$'),
    ]
    d.lesson(L, optional=True)
    Q = []
    for n_, ans in [(50, '5sqrt(2)'), (12, '2sqrt(3)'), (18, '3sqrt(2)'), (75, '5sqrt(3)'), (8, '2sqrt(2)'), (48, '4sqrt(3)'), (200, '10sqrt(2)'), (27, '3sqrt(3)'), (98, '7sqrt(2)'), (45, '3sqrt(5)')]:
        Q.append(E(d, d.qid('S'), f'Simplify $sqrt({n_})$.', ans, sp.sqrt(n_), [], label=f'$sqrt({n_})$ =', level=1, explain=f'${D(ans)}$'))
    for e_, ans in [('frac{1}{sqrt(2)}', 'sqrt(2)/2'), ('frac{6}{sqrt(3)}', '2sqrt(3)'), ('frac{4}{sqrt(8)}', 'sqrt(2)'), ('frac{10}{sqrt(5)}', '2sqrt(5)'), ('frac{3}{sqrt(6)}', 'sqrt(6)/2'), ('frac{1}{sqrt(3)}', 'sqrt(3)/3')]:
        Q.append(E(d, d.qid('R'), f'Rationalize: write ${e_}$ with no root on the bottom.', ans, S(e_.replace('frac{', '(').replace('}{', ')/(').replace('}', ')')), [], label='answer =', level=2,
                   explain=f'Multiply top and bottom by the root: ${D(ans)}$.'))
    for a_, b_ in [('sqrt(x)', '3'), ('sqrt(x + 2)', '1'), ('sqrt(x)', '5'), ('sqrt(x + 5)', '3'), ('sqrt(2x + 1)', '3'), ('2', 'sqrt(x + 3)'), ('sqrt(x^2 + 9)', '3'), ('sqrt(x)', 'sqrt(2)')]:
        prod = sp.expand((S(a_) - S(b_)) * (S(a_) + S(b_)))
        Q.append(E(d, d.qid('C'), f'Multiply out $({D(a_)} - {D(b_)})({D(a_)} + {D(b_)})$.', sp_app(prod), prod, label='product =', level=2, ranges={'x': [1, 3]}, explain=f'$a^2 - b^2 = {D(sp_app(prod))}$'))
    for e_, rhs, sol in [('sqrt(x + 3)', 4, 13), ('sqrt(2x)', 6, 18), ('sqrt(x) + 1', 5, 16), ('sqrt(x - 4)', 3, 13), ('3sqrt(x)', 12, 16), ('sqrt(5x + 1)', 4, 3)]:
        Q.append(N(d.qid('Q'), f'Solve ${D(e_)} = {rhs}$.', sol, label='$x$ =', level=3, explain=f'Square both sides and solve: $x = {sol}$.'))
    Q.append(MC(d.qid('A'), '$sqrt(x^2)$ is equal to', ['$|x|$', '$x$', '$-x$', '$x^2$'], level=3, explain='If $x = -3$: $sqrt(9) = 3 = |-3|$.'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


def deck_fractions():
    d = Deck('l-fractions', 'Reducing Fractions', 'Review: factor and cancel; combine fractions.', 'Limits')
    L = [
        E(d, 'L1', 'Reduce by factoring and canceling: $frac{x^2 - 4}{x - 2} = frac{(x - 2)(x + 2)}{x - 2}$.', 'x + 2', x + 2, label='reduced =', hint='Cancel the matching factor.', explain='$x + 2$'),
        E(d, 'L2', 'To add fractions, get a common denominator: $frac{1}{x} + frac{1}{x + 1} = frac{(x + 1) + x}{x(x + 1)}$. Simplify the top.', '(2x + 1)/(x(x + 1))', (2 * x + 1) / (x * (x + 1)),
          label='sum =', hint='$(x + 1) + x = 2x + 1$', explain='$frac{2x + 1}{x(x + 1)}$'),
        MC('L3', 'Only **factors** cancel, never terms. Which one is a correct cancel?', ['$frac{x(x + 3)}{x} = x + 3$', '$frac{x + 3}{x} = 3$', '$frac{x^2 + 1}{x} = x + 1$', '$frac{x + 5}{5} = x$'],
           hint='The thing you cancel has to multiply everything on top.', explain='In $frac{x + 3}{x}$ the $x$ is added, not multiplied, so it cannot cancel.'),
    ]
    d.lesson(L, optional=True)
    Q = []
    for a_, b_ in [(18, 24), (15, 35), (42, 56), (12, 30), (27, 45), (16, 64)]:
        Q.append(N(d.qid('N'), f'Reduce $frac{{{a_}}}{{{b_}}}$ (type it as a fraction).', sp.Rational(a_, b_), label='reduced =', tol=0.0001, level=1, explain=f'${frac_str(sp.Rational(a_, b_))}$'))
    for top, bot in [('x^2 - 4', 'x - 2'), ('x^2 - 9', 'x + 3'), ('x^2 + 5x + 6', 'x + 2'), ('x^2 - x', 'x'), ('2x + 6', 'x + 3'), ('x^3 - x', 'x^2 - x'), ('x^2 - 1', 'x^2 + 2x + 1'),
                     ('3x^2 - 12', 'x - 2'), ('x^2 - 6x + 9', 'x^2 - 9'), ('4x^2 - 1', '2x + 1'), ('x^2 + 3x', 'x^2 - 9'), ('5x - 10', '10x - 20')]:
        simp = sp.cancel(S(top) / S(bot))
        Q.append(E(d, d.qid('R'), f'Reduce $frac{{{D(top)}}}{{{D(bot)}}}$.', sp_app(simp), simp, label='reduced =', level=2, ranges={'x': [4, 6]}, explain=f'Factor, cancel: ${D(sp_app(simp))}$.'))
    for e_, src in [('frac{1}{x} + frac{1}{x + 1}', '1/x + 1/(x + 1)'), ('frac{1}{x} - frac{1}{2}', '1/x - 1/2'), ('frac{3}{x - 1} + frac{2}{x + 1}', '3/(x - 1) + 2/(x + 1)'),
                    ('frac{x}{x + 2} - 1', 'x/(x + 2) - 1'), ('frac{1}{x + 2} + 1', '1/(x + 2) + 1'), ('frac{2}{x} + frac{5}{x^2}', '2/x + 5/x^2'), ('frac{1}{x - 3} - frac{1}{x + 3}', '1/(x - 3) - 1/(x + 3)'),
                    ('frac{4}{x^2 - 4} + frac{1}{x - 2}', '4/(x^2 - 4) + 1/(x - 2)')]:
        comb = sp.factor(sp.together(S(src)))
        Q.append(E(d, d.qid('C'), f'Write ${e_}$ as one fraction.', sp_app(comb), comb, label='one fraction =', level=3, ranges={'x': [4, 6]}, explain=f'${D(sp_app(comb))}$'))
    for wrong in ['$frac{x + 3}{x} = 3$', '$frac{x^2 + 1}{x} = x + 1$', '$frac{x + 5}{5} = x$', '$frac{2x + 4}{2} = x + 4$']:
        Q.append(TF(d.qid('T'), f'Is this correct? {wrong}', False, level=2, explain='Only factors cancel, not terms.'))
    d.drill('practice', 'Practice', Q, 'pool')
    d.save()


def deck_precise():
    d = Deck('l-precise', 'The Precise Definition of a Limit', 'Optional: epsilons and deltas.', 'Limits')
    L = [
        MC('L1', '$lim[x->a] f(x) = L$ **precisely** means: for every distance $epsilon > 0$ (how close $f(x)$ must get to $L$), there is a distance $delta > 0$ so that whenever $0 < |x - a| < delta$, we get $|f(x) - L| < epsilon$. In words:',
           ['You can make $f(x)$ as close to $L$ as you like by taking $x$ close enough to $a$', '$f(a) = L$', '$f$ is continuous', '$f(x)$ equals $L$ for $x$ near $a$'],
           hint='$epsilon$ is the target; $delta$ is how close $x$ must be.', explain='Someone names an $epsilon$; you must answer with a $delta$ that works.'),
        N('L2', 'Prove $lim[x->2] (3x + 1) = 7$. We need $|3x + 1 - 7| = 3|x - 2| < epsilon$, which holds when $|x - 2| < frac{epsilon}{3}$. If $epsilon = 0.3$, what $delta$ works?', 0.1, label='$delta$ =',
          hint='$delta = frac{epsilon}{3}$', explain='$delta = frac{0.3}{3} = 0.1$'),
        MC('L3', 'For a line $f(x) = mx + b$, the right choice is always $delta =$', ['$frac{epsilon}{|m|}$', '$epsilon$', '$m epsilon$', '$epsilon + m$'], hint='$|f(x) - L| = |m||x - a|$', explain='$delta = frac{epsilon}{|m|}$'),
    ]
    d.lesson(L)
    T = [
        MC('T1', 'In the precise definition, who picks $epsilon$?', ['It is given (any positive number at all)', 'You pick it to be convenient', 'It must be 1', 'It is always $delta$'], explain='Your $delta$ must work for every $epsilon$.'),
        TF('T2', 'In the definition, $x = a$ itself is included.', False, explain='$0 < |x - a|$ leaves out $x = a$: the limit never looks at the point.'),
        MC('T3', '$|x - a| < delta$ means', ['$x$ is within $delta$ of $a$', '$x < delta$', '$a < delta$', '$x$ is more than $delta$ from $a$'], explain='Absolute value is distance.'),
    ]
    d.drill('theory', 'Theory', T, 'all')
    Q = []
    for m_, b_, a0, eps in [(3, 1, 2, 0.3), (2, -1, 1, 0.1), (5, 0, 3, 0.05), (4, 2, -1, 0.2), (-2, 7, 1, 0.4), (6, -5, 2, 0.06), (0.5, 1, 4, 0.01), (10, 3, 0, 0.5), (-4, 1, 2, 0.08), (7, 7, 1, 0.07)]:
        Lv = m_ * a0 + b_
        delta = eps / abs(m_)
        Q.append(N(d.qid('D'), f'For $lim[x->{a0}] ({D(tidy(poly_str([sp.nsimplify(m_), b_])))}) = {num(Lv)}$ and $epsilon = {eps}$, find the largest $delta$ that works.', delta, label='$delta$ =', tol=0.0005,
                   level=2, explain=f'$delta = frac{{epsilon}}{{|m|}} = frac{{{eps}}}{{{abs(m_)}}} = {num(delta)}$'))
    for q_, r_, w_ in [('If a $delta$ works for some $epsilon$, a smaller $delta$', 'also works', ['never works', 'works only if $epsilon$ grows', 'must equal $epsilon$']),
                       ('$|f(x) - L| < epsilon$ says', '$f(x)$ is within $epsilon$ of $L$', ['$f(x) < epsilon$', '$L < epsilon$', '$f(x)$ is far from $L$']),
                       ('To prove a limit with the precise definition, you must', 'find a $delta$ for every $epsilon > 0$', ['find one $epsilon$', 'plug in $x = a$', 'show $f(a) = L$'])]:
        Q.append(MC(d.qid('C'), q_, [r_] + w_, level=1, explain=r_ + '.'))
    d.drill('practice', 'Practice', Q, 'pool', setSize=8)
    d.save()


def deck_review1():
    d = Deck('review1', 'Chapter Review: Limits', 'Which tool, and a practice test.', 'Limits')
    tool = []
    for k, (f, a0, kk) in enumerate(COMBO):
        o = [TOOLS[kk]] + R.sample([t for t in TOOLS if t != TOOLS[kk]], 3)
        tool.append(MC(f'W{k + 1}', f'What is the best tool for $lim[x->{a0}] {f}$?', o, level=1 + (k % 3 == 2), topic='Which tool?', explain=f'{TOOLS[kk]}.'))
    d.drill('tool', 'Which tool?', tool, 'pool', setSize=10)
    topics = {'limits-intro': 'Limits from graphs', 'l-infinite': 'Infinite limits', 'l-laws': 'Limit laws', 'l-factor': 'Factor and cancel', 'l-trig': 'Trig limits',
              'l-sqrt': 'Square roots', 'l-complex': 'Complex fractions', 'l-cont': 'Continuity', 'l-atinf': 'Limits at infinity'}
    ex = []
    rr = random.Random(5)
    for did, top in topics.items():
        src = json.load(open(os.path.join(ROOT, 'decks', did + '.json')))
        qs = [q for q in src['drills']['practice']['questions'] if q.get('level', 1) >= 2]
        rr.shuffle(qs)
        for q in qs[:6]:
            q = copy.deepcopy(q)
            pre = did.replace('l-', '').replace('limits-intro', 'lim').upper()[:3]
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
    deck_limits()
    deck_infinite()
    deck_laws()
    deck_factor()
    deck_squeeze()
    deck_trig()
    deck_sqrtlim()
    deck_complex()
    deck_combo()
    deck_cont()
    deck_atinf()
    deck_evaluate()
    deck_vasym()
    deck_sqroots()
    deck_fractions()
    deck_precise()
    deck_review1()
    write_manifest('world1')
