"""World 3 (Applications of Derivatives) in the new stop format, laid out by class day (days 22 to 31).
Every stop: a short lesson, a Theory set (every question required), and a Practice pool with levels.

This script CONVERTS the older World 3 decks, kept as they were in tools/gen/src/w3/, and adds generated
practice where a stop was thin. It writes the decks and maps/applications.json.
   python3 tools/gen/world3.py && python3 tools/stops.py && node tools/gen/verify.js
Edit the deck JSON files directly from now on: running this again overwrites them."""
import json, os, copy, random, re
import sympy as sp
from lib import *

SRC = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src', 'w3')
UNIT = 'Applications of Derivatives'
x = sp.Symbol('x')
DRILLABLE = {'mc', 'tf', 'num', 'expr', 'crit', 'interval', 'multi', 'steps', 'match', 'pick', 'bank', 'order', 'graph', 'sketch', 'tap', 'lim'}
_src = {}


def src(dk):
    if dk not in _src:
        _src[dk] = json.load(open(os.path.join(SRC, dk + '.json')))
    return _src[dk]


def slides(dk):
    d = src(dk)
    out = {}
    for L in ([d['lesson']] if d.get('lesson') else d.get('lessons', [])):
        for s in L['slides']:
            out[s['id']] = s
    return out


def Sl(dk, sid, pre=None, text=None, **kw):
    """one lesson step from the old deck, optionally with new text or a sentence in front"""
    s = copy.deepcopy(slides(dk)[sid])
    if text is not None:
        s['text'] = text
    if pre:
        s['text'] = pre + (s.get('text') or '')
    s.update(kw)
    s.pop('needs', None)
    return s


def Q(dk, kind, ids=None, level=None, skip=()):
    """drill questions from the old deck (all of them, or the ids listed), with a level"""
    qs = src(dk)['drills'][kind]['questions']
    out = []
    for q in qs:
        if (ids is None or q['id'] in ids) and q['id'] not in skip:
            q = copy.deepcopy(q)
            q.pop('stage', None)
            if level:
                q['level'] = level(q) if callable(level) else level
            out.append(q)
    if ids is not None:
        assert len(out) == len(set(ids) - set(skip)), (dk, kind, ids)
    return out


def lv(q, n):
    q = copy.deepcopy(q)
    q['level'] = n
    q.pop('title', None) if q['type'] not in ('steps',) else None
    return q


def strip_levels(qs):
    out = []
    for q in qs:
        q = copy.deepcopy(q)
        q.pop('level', None)
        q.pop('stage', None)
        out.append(q)
    return out


def build(id, title, subtitle, lessons, theory, practice, graphs=None, optional=False, setSize=None, more=None):
    d = Deck(id, title, subtitle, UNIT)
    d.d['graphs'] = copy.deepcopy(graphs or {})
    if len(lessons) == 1:
        d.d['lesson'] = {'slides': lessons[0][1]}
    elif lessons:
        d.d['lessons'] = [{'id': 'part%d' % (i + 1), 'title': t, 'slides': s} for i, (t, s) in enumerate(lessons)]
    if optional:
        d.d['lessonOptional'] = True
    if theory:
        d.drill('theory', 'Theory', strip_levels(theory), 'all')
    if practice:
        kw = {'setSize': setSize} if setSize else {}
        assert all(q.get('level') in (1, 2, 3) for q in practice), (id, [q['id'] for q in practice if not q.get('level')])
        d.drill('practice', 'Practice', practice, 'pool', **kw)
    for k, v in (more or {}).items():
        d.d['drills'][k] = v
    return d


def by_type(m, default=1):
    return lambda q: m.get(q['type'], default)


def app_poly(c):
    """coefficients (highest power first) -> app syntax, e.g. 2*x^3-3*x^2+6*x"""
    n = len(c) - 1
    out = ''
    for i, a in enumerate(c):
        p = n - i
        if a == 0:
            continue
        mag = abs(a)
        term = (str(mag) if (mag != 1 or p == 0) else '') + (('*' if mag != 1 else '') + ('x' if p == 1 else 'x^%d' % p) if p else '')
        out += ('-' if a < 0 else ('+' if out else '')) + term
    return out or '0'


def show_poly(c):
    return app_poly(c).replace('*', '').replace('+', ' + ').replace('-', ' - ').strip().replace('  ', ' ') if c[0] > 0 else '-' + app_poly([-c[0]] + list(c[1:])).replace('*', '').replace('+', ' + ').replace('-', ' - ') if all(v == 0 for v in c[1:]) else _show_neg(c)


def _show_neg(c):
    s = app_poly(c).replace('*', '')
    s = s[0] + s[1:].replace('+', ' + ').replace('-', ' - ')
    return s


def iv(a, b):
    f = lambda v: '-inf' if v == -sp.oo else 'inf' if v == sp.oo else str(v)
    return '(%s,%s)' % (f(a), f(b))


def ivshow(a, b):
    f = lambda v: '-∞' if v == -sp.oo else '∞' if v == sp.oo else str(v).replace('-', '−')
    return '$(%s, %s)$' % (f(a), f(b))


# ====================================================================== Day 22: Related Rates
def parse_rr(s):
    names = sorted(set(re.findall(r"[A-Za-zθ]'", s)), key=len)
    t = s.replace('θ', 'th')
    t = re.sub(r"([A-Za-z]+)'", r'\1_p', t).replace('^', '**')
    return sp.sympify(t, locals={'E': sp.Symbol('E'), 'S': sp.Symbol('S'), 'pi': sp.pi}), names


def plug_ins(qs, rng, prefix, level=2):
    """from each "differentiate in t" answer, a plug-in-the-numbers question"""
    out = []
    for q in qs:
        if 'θ' in q['answer'] or 'solve for' in q['text']:
            continue
        e, _ = parse_rr(q['answer'])
        syms = sorted(e.free_symbols, key=lambda s: s.name)
        for _try in range(40):
            vals = {}
            for s in syms:
                vals[s] = rng.choice([1, 2, 3, -1, -2] if s.name.endswith('_p') else [2, 3, 4, 5, 6])
            if {s.name for s in syms} >= {'x', 'y'} and 'sqrt' in q['answer']:
                vals[sp.Symbol('x')], vals[sp.Symbol('y')] = 3, 4
            try:
                v = sp.N(e.subs(vals))
            except Exception:
                continue
            if v.is_real and 0.2 < abs(v) < 5000:
                break
        else:
            continue
        v = float(v)
        lab = q['label'].replace(' =', '').strip().strip('$')
        if not re.fullmatch(r"[A-Za-z]'", lab):
            continue
        m = re.search(r"\$(%s = [^$]+)\$" % re.escape(lab), q.get('explain', ''))
        shown = m.group(1) if m else '%s = %s' % (lab, D(q['answer']))
        given = ', '.join('$%s = %s$' % (s.name.replace('_p', "'"), str(vals[s]).replace('-', '−')) for s in syms)
        given = ' and '.join(given.rsplit(', ', 1))
        exact = abs(v - round(v)) < 1e-9
        out.append(N(prefix + q['id'], '$$%s$$\nFind $%s$ when %s.%s' % (shown, lab, given, '' if exact else ' A decimal is fine.'),
                     round(v) if exact else round(v, 4), label='$%s$ %s' % (lab, '=' if exact else '≈'), tol=None if exact else max(abs(v) * 0.005, 0.0005), level=level,
                     hint='Every letter has a value now. Put them in and compute.', explain='$%s$ %s %s.' % (lab, '=' if exact else '≈', num(round(v) if exact else round(v, 3)))))
    return out


def deck_related():
    rng = random.Random(322)
    diffs = Q('related', 'diff')
    one = [q for q in diffs if len(set(re.findall(r"[A-Za-zθ]'", q['answer']))) == 1 and 'solve for' not in q['text']]
    many = [q for q in diffs if q not in one]
    probs = {q['id']: q for q in Q('related', 'problems')}
    easy = ['P1', 'P2', 'P3', 'P4', 'P5', 'P6', 'P8', 'P14', 'P16']
    hard = [k for k in probs if k not in easy]
    sl = slides('related')

    # ---- Related Rates (day 22)
    lesson = [Sl('related', k) for k in ('L1', 'L3', 'L4', 'L5', 'L7', 'L9')]
    theory = [
        MC('T1', '“How fast is the area growing?” What is that question asking for?', ['$frac{dA}{dt}$', '$A$', '$frac{dr}{dt}$', '$frac{dA}{dr}$'],
           hint='“How fast” means a rate with respect to time.', explain='A rate of change in time: $frac{dA}{dt}$.'),
        MC('T2', 'A balloon’s radius **shrinks** at 3 cm/s. In symbols:', ['$frac{dr}{dt} = -3$', '$frac{dr}{dt} = 3$', '$r = -3$', '$r = 3t$'],
           hint='Shrinking means the radius is going down.', explain='A quantity that is getting smaller has a negative rate.'),
        TF('T3', 'In a related rates problem, differentiating $r^2$ with respect to $t$ gives $2r$.', False,
           hint='$r$ is a function of $t$. Which rule applies?', explain='Chain rule: $frac{d}{dt}(r^2) = 2r frac{dr}{dt}$.'),
        copy.deepcopy(sl['L2']), copy.deepcopy(sl['L6']), copy.deepcopy(sl['L12']), copy.deepcopy(sl['L10']),
    ]
    theory[5]['text'] = 'From $V\' = 4pi r^2 r\'$ with $V\'$ = 100 and $r$ = 5, find $r\'$.'
    theory[3]['text'] = 'A ripple’s radius grows at a steady 2 cm/s, and its area is $A = pi r^2$. Which rate stays the same the whole time?'
    practice = [lv(q, 1) for q in one] + plug_ins(one, rng, 'N') + [lv(probs[k], 3) for k in easy]
    d1 = build('related', 'Related Rates', 'Every variable is a function of time: differentiate, then plug in.', [(None, lesson)], theory, practice, setSize=10)

    # ---- Related Rates II (day 23)
    p13 = probs['P13']
    st = copy.deepcopy(p13['steps'])
    L = [
        MC('L1', 'Water drains from a cone-shaped funnel 20 ft tall with top radius 10 ft. The water is $h$ ft deep and its surface has radius $r$.\n$$V = frac{1}{3}pi r^2 h$$\nWe know $frac{dV}{dt}$ and want $frac{dh}{dt}$. What is in the way?',
           ['The formula has a second changing variable, $r$, and we do not know $frac{dr}{dt}$', 'The volume formula is wrong for water', 'Nothing. Differentiate right away'],
           hint='Count the letters on the right side that change as the water drains.',
           explain='Two changing variables would need two rates. The fix: get rid of $r$ before differentiating.'),
        N('L2', '**Similar triangles.** The water makes a small cone with the same shape as the funnel (20 ft tall, top radius 10 ft). When the water is 12 ft deep, what is the radius of its surface?', 6,
          label='$r$ =', hint='$frac{r}{12} = frac{10}{20}$', explain='The radius is always half the depth: $r$ = 6.'),
        dict(st[0], id='L3', hint='The ratio of radius to height is the same for the water as for the funnel.'),
        dict(st[1], id='L4', hint='Replace $r$ with $frac{h}{2}$ and simplify.'),
        dict(st[2], id='L5', hint='Chain rule: $frac{d}{dt}(h^3) = 3h^2 h\'$.'),
        MC('L6', 'Now the reading. “Water **drains** at 0.3 ft³/s.” What does that say?', ['$frac{dV}{dt} = -0.3$', '$frac{dV}{dt} = 0.3$', '$V = 0.3$', '$frac{dh}{dt} = -0.3$'],
           hint='Is the volume going up or down?', explain='Draining means the volume goes down, so its rate is negative. Drains, shrinks, melts and slides down all mean a negative rate.'),
    ]
    L[0]['figure'] = p13.get('figure')
    if not L[0]['figure']:
        L[0].pop('figure')
    theory2 = [
        TF('T1', 'Substituting $r = frac{h}{2}$ **before** differentiating is fine, because it is true at every moment.', True,
           hint='Is the water’s radius half its depth the whole time, or only at one instant?', explain='A relationship that always holds can go in before you differentiate.'),
        TF('T2', 'Substituting $h$ = 12 **before** differentiating is fine, because the problem asks about that moment.', False,
           hint='What is the derivative of the constant 12?', explain='$h$ = 12 is true at one instant only. Put it in early and $h$ becomes a constant, so its rate disappears.'),
        MC('T3', 'A kite flies 100 ft above the ground, $x$ ft away horizontally. Which equation links the angle of elevation $theta$ to $x$?',
           ['$tan theta = frac{100}{x}$', '$sin theta = frac{100}{x}$', '$tan theta = frac{x}{100}$', '$theta = 100x$'],
           hint='The height is opposite the angle and $x$ is adjacent.', explain='Opposite over adjacent: $tan theta = frac{100}{x}$.'),
        MC('T4', 'A 13-ft ladder slides down a wall. Which quantity is a **constant**?', ['The length of the ladder', 'The height of the top', 'The distance of the bottom from the wall', 'None of them'],
           hint='What does not change as the ladder slides?', explain='The ladder stays 13 ft long, so 13 goes into the equation as a number: $x^2 + y^2 = 169$.'),
        MC('T5', 'A snowball melts so that its surface area decreases at 1 cm²/min. In symbols:', ['$frac{dS}{dt} = -1$', '$frac{dS}{dt} = 1$', '$S = -1$', '$frac{dr}{dt} = -1$'],
           hint='Which quantity is the 1 cm²/min about?', explain='The rate is about the surface area, and it is going down.'),
        MC('T6', 'Two cars leave an intersection, one heading east ($x$) and one north ($y$). $z$ is the distance between them. Which equation links them?',
           ['$x^2 + y^2 = z^2$', '$x + y = z$', '$xy = z$', '$z = frac{1}{2}xy$'], hint='East and north make a right angle.', explain='A right triangle: the Pythagorean theorem.'),
        MC('T7', 'In a problem about a changing angle, $frac{d theta}{dt}$ comes out in…', ['radians per unit of time', 'degrees per unit of time', 'feet per second', 'no units at all'],
           hint='The derivative formulas for sine, cosine and tangent assume one kind of angle measure.', explain='The trig derivative rules only work in radians, so the rate is in radians per second (or minute, or hour).'),
    ]
    practice2 = [lv(q, 1) for q in many] + plug_ins(many, rng, 'N') + [lv(probs[k], 3) for k in hard]
    d2 = build('related2', 'Related Rates II', 'Harder geometry and harder reading: cones, shadows, angles and moving cars.', [(None, L)], theory2, practice2, setSize=10)
    return [d1, d2]


# ====================================================================== Day 24: Linearization, Newton
def deck_linear():
    lesson = [Sl('linear', 'N1'), Sl('linear', 'N3'), Sl('linear', 'N5'),
              Sl('linear', 'N7', text='So $L(x) = frac{1}{2} - frac{1}{4}(x - 2)$. Use it to estimate $frac{1}{2.1}$: find $L(2.1)$.'),
              Sl('linear', 'N15'), Sl('linear', 'N17')]
    tids = ['T1', 'T3', 'T5', 'T9', 'T12', 'T14', 'T16']
    theory = Q('linear', 'theory', tids)
    sl = slides('linear')
    practice = (Q('linear', 'theory', level=1, skip=tids)
                + Q('linear', 'calc', level=lambda q: 3 if q['type'] == 'multi' and len(q['parts']) == 3 else 2)
                + [lv(sl['N10'], 3), lv(sl['N13'], 3), lv(sl['N18'], 2), lv(sl['N19'], 2)])
    return [build('linear', 'Linearization and Differentials', 'Approximating a function with its tangent line.', [(None, lesson)], theory, practice, graphs=src('linear').get('graphs'))]


def deck_newton():
    lesson = [Sl('newton', 'L8', pre='Newton’s method hunts for a **root** of $f$ (where the curve crosses the $x$-axis) when no formula will find it.\n'),
              Sl('newton', 'L9'),
              Sl('newton', 'L15', text='The tangent line at $x_0$ hits the $x$-axis at $x_1$, where $0 - f(x_0) = f\'(x_0)(x_1 - x_0)$. Divide by $f\'(x_0)$:\n$$-frac{f(x_0)}{f\'(x_0)} = x_1 - x_0$$\nSolve for $x_1$.'),
              Sl('newton', 'L17'), Sl('newton', 'L21'), Sl('newton', 'L26', pre='Newton’s method can also compute numbers like √2: write a function whose root **is** that number.\n')]
    tids = ['T3', 'T5', 'T7', 'T10', 'T13', 'T17', 'T26']
    lev = {'given': 1, 'fromf': 2, 'two': 3}
    calc = []
    for q in src('newton')['drills']['calc']['questions']:
        q2 = copy.deepcopy(q)
        q2['level'] = lev[q2.pop('stage')]
        calc.append(q2)
    practice = Q('newton', 'theory', level=1, skip=tids) + calc
    return [build('newton', "Newton's Method", 'Using tangent lines to home in on a root.', [(None, lesson)], Q('newton', 'theory', tids), practice, graphs=src('newton').get('graphs'))]


# ====================================================================== Day 25: Max and Mins
def deck_maxmin():
    a = [Sl('maxmin', 's02', pre='The **absolute minimum** of a function is the height of its lowest point. The **absolute maximum** is the height of its highest point.\n'),
         Sl('maxmin', 's09'), Sl('maxmin', 's12'),
         Sl('maxmin', 's19', pre='**Extreme Value Theorem.** If $f$ is continuous on a closed interval $[a, b]$, then $f$ has an absolute maximum and an absolute minimum on $[a, b]$.\n'),
         Sl('maxmin', 's21'), Sl('maxmin', 's23')]
    b = [Sl('maxmin', 's27', pre='A **local maximum** is a point at least as high as every point near it on both sides, like the top of a hill. A **local minimum** is the bottom of a valley.\n'),
         Sl('maxmin', 's32', pre='A **critical point** is an $x$-value in the domain where $f\'(x) = 0$ or $f\'(x)$ does not exist. Local highs and lows can only happen there. (**Fermat’s Theorem:** if $f$ has a local max or min at $c$ and $f\'(c)$ exists, then $f\'(c) = 0$.)\n'),
         Sl('maxmin', 's34'), Sl('maxmin', 's41'), Sl('maxmin', 's44'), Sl('maxmin', 's49')]
    tids = ['t02', 't03', 't05', 't06', 't10', 't12', 't15', 't17']
    practice = Q('maxmin', 'theory', level=1, skip=tids) + Q('maxmin', 'calc', level=by_type({'graph': 1, 'crit': 2, 'num': 3}))
    return [build('maxmin', 'Max and Mins', 'Highest and lowest points: absolute and local extremes, critical points, and how to find them.',
                  [('Absolute max and min', a), ('Local extremes and critical points', b)], Q('maxmin', 'theory', tids), practice, graphs=src('maxmin').get('graphs'))]


# ====================================================================== Day 26: MVT, first derivative test
def deck_mvt():
    lesson = [Sl('mvt', 'M1'), Sl('mvt', 'M4'), Sl('mvt', 'M9'), Sl('mvt', 'M10'), Sl('mvt', 'M12'),
              Sl('mvt', 'M15', pre='You drive to Grandma’s house, 60 miles away, in exactly 1 hour. Your average speed was 60 mph.\n')]
    tids = ['T4', 'T7', 'T8', 'T9', 'T10', 'T12', 'T18']
    sl = slides('mvt')
    practice = (Q('mvt', 'theory', level=1, skip=tids) + Q('mvt', 'calc', level=by_type({'multi': 3}, 2))
                + [lv(sl['M6'], 3), lv(sl['M8'], 2), lv(sl['M16'], 3), lv(sl['M18'], 3)])
    return [build('mvt', 'Mean Value Theorem', 'Where the slope of a tangent equals the average slope.', [(None, lesson)], Q('mvt', 'theory', tids), practice, graphs=src('mvt').get('graphs'))]


def cubic(p, q, sign=1):
    """f with f'(x) = 6 sign (x - p)(x - q)"""
    return [2 * sign, -3 * (p + q) * sign, 6 * p * q * sign, 0]


def deck_incdec():
    rng = random.Random(326)
    g = src('curve').get('graphs')
    lesson = [Sl('curve', k) for k in ('L1', 'L2', 'L3', 'L5', 'L6', 'L7')]
    theory = [Sl('curve', 'L4', text='Here is the graph of $f\'$ (not $f$). What happens to $f$ at $x$ = 2?')] + Q('curve', 'tests', ['T2', 'T9', 'T10', 'T11', 'T15', 'T16'])
    d = build('incdec', 'Increasing, Decreasing and the First Derivative Test', 'What the sign of f′ says about f, and how to find local highs and lows with it.', [(None, lesson)], theory, [], graphs=g)
    d.keys = []
    P = Q('curve', 'tests', ['T1', 'T3', 'T4', 'T5', 'T6'], level=1)
    P += Q('curve', 'tests', ['T20', 'T21', 'T22', 'T23', 'T24', 'T25', 'T26'], level=2)
    P += Q('curve', 'data', ['D1', 'D3', 'D4', 'D27', 'D32', 'D34'], level=2)
    P += Q('curve', 'data', ['D7', 'D10', 'D12', 'D15', 'D21', 'D22', 'D24'], level=3)
    pairs = [(p, q) for p in range(-4, 4) for q in range(p + 1, 5) if (p + q) % 2 == 0 or True]
    rng.shuffle(pairs)
    n = 0
    for p, q in pairs[:10]:                      # level 1: read a sign from a factored derivative
        n += 1
        where = rng.choice(['left', 'mid', 'right'])
        m = {'left': p - rng.randint(1, 2), 'mid': None, 'right': q + rng.randint(1, 2)}[where]
        if where == 'mid':
            if q - p < 2:
                m, where = q + 1, 'right'
            else:
                m = rng.randint(p + 1, q - 1)
        fac = lambda r: '(x + %d)' % -r if r < 0 else '(x - %d)' % r if r > 0 else 'x'
        a, b = m - p, m - q
        inc = a * b > 0
        P.append(MC('G%d' % n, '$$f\'(x) = %s%s$$\nAt $x$ = %s, is $f$ increasing or decreasing?' % (fac(p), fac(q), str(m).replace('-', '−')), ['Increasing', 'Decreasing', 'Neither'], 0 if inc else 1, fixed=True, level=1,
                    hint='Find the sign of each factor at that $x$, then multiply the signs.',
                    explain='The factors are %s and %s there, so $f\'$ is %s and $f$ is %s.' % (str(a).replace('-', '−'), str(b).replace('-', '−'), 'positive' if inc else 'negative', 'increasing' if inc else 'decreasing')))
    for p, q in pairs[10:20]:                     # level 3: the whole first derivative test
        n += 1
        sign = rng.choice([1, 1, -1])
        c = cubic(p, q, sign)
        f = sum(co * x ** (3 - i) for i, co in enumerate(c))
        dc = [3 * c[0], 2 * c[1], c[2]]
        up = iv(-sp.oo, p) + 'U' + iv(q, sp.oo) if sign > 0 else iv(p, q)
        hi, lo = (p, q) if sign > 0 else (q, p)
        qid = 'G%d' % n
        P.append(STEPS(qid, 'Run the first derivative test on\n$$f(x) = %s$$' % _show_neg(c), [
            E(d, qid + '.1', 'Find $f\'(x)$.', app_poly(dc), sp.diff(f, x), label="$f'(x)$ =", keys=[], hint='Power rule on each term.', work="$f'(x) = %s$" % _show_neg(dc)),
            CRIT(qid + '.2', 'Find every critical number.', [p, q], '$x$ =', noneText='No critical numbers', hint="Factor: $f'(x) = %d(x %s)(x %s)$." % (6 * sign, ('+ %d' % -p) if p < 0 else '- %d' % p, ('+ %d' % -q) if q < 0 else '- %d' % q),
                 explain="$f'(x) = 0$ at $x$ = %s and $x$ = %s." % (str(p).replace('-', '−'), str(q).replace('-', '−'))),
            INTERVAL(qid + '.3', 'Where is $f$ increasing? (Open intervals.)', up, label='Increasing on', noneText='Never increasing', hint='Test one point in each of the three pieces.',
                     explain="$f'$ is positive there."),
            CRIT(qid + '.4', 'Where does $f$ have a local **max**?', [hi], '$x$ =', noneText='No local max', hint="Where does $f'$ change from + to −?", explain="$f'$ goes from + to − at $x$ = %s." % str(hi).replace('-', '−')),
            CRIT(qid + '.5', 'Where does $f$ have a local **min**?', [lo], '$x$ =', noneText='No local min', hint="Where does $f'$ change from − to +?", explain="$f'$ goes from − to + at $x$ = %s." % str(lo).replace('-', '−')),
        ], level=3, title='First derivative test'))
    d.drill('practice', 'Practice', P, 'pool')
    return [d]


# ====================================================================== Day 27: concavity
def deck_concavity():
    rng = random.Random(327)
    lesson = [Sl('curve', k) for k in ('L9', 'L10', 'L11', 'L12', 'L14', 'L15')]
    theory = [Sl('curve', 'L13')] + Q('curve', 'tests', ['T12', 'T13', 'T14', 'T17', 'T18', 'T19'])
    d = build('concavity', 'Concavity and the Second Derivative Test', 'How a graph bends, where the bend changes, and a second way to sort critical numbers.', [(None, lesson)], theory, [], graphs=src('curve').get('graphs'))
    d.keys = []
    P = Q('curve', 'tests', ['T7', 'T8'], level=1) + Q('curve', 'tests', ['T27', 'T28', 'T29', 'T30'], level=2)
    P += Q('curve', 'data', ['D5', 'D29', 'D33'], level=2) + Q('curve', 'data', ['D8', 'D9', 'D16', 'D19', 'D20'], level=3)
    n = 0
    for c0, v in [(1, -4), (3, 5), (-2, 12), (0, -9), (4, 0), (-1, 2), (5, -1), (2, 0)]:      # level 1: the second derivative test, numbers given
        n += 1
        ans = 0 if v < 0 else 1 if v > 0 else 2
        P.append(MC('G%d' % n, "$f'(%s) = 0$ and $f''(%s) = %s$. At $x$ = %s, $f$ has…" % (c0, c0, str(v).replace('-', '−'), str(c0).replace('-', '−')), ['a local max', 'a local min', 'no answer from this test'], ans, fixed=True, level=1,
                    hint='Positive second derivative: a cup. Negative: a frown.',
                    explain=['A flat spot on a frown is a hilltop: local max.', 'A flat spot in a cup is a valley: local min.', "When $f''(c) = 0$ the test says nothing. Use the first derivative test."][ans]))
    for a, b in [(1, 3), (-2, 5), (2, -4), (-1, 0), (3, 2), (-3, -6)]:                          # level 2: one inflection point
        n += 1
        c = [1, -3 * a, b, 0]
        f = sum(co * x ** (3 - i) for i, co in enumerate(c))
        P.append(INTERVAL('G%d' % n, '$$f(x) = %s$$\nWhere is $f$ concave up?' % _show_neg(c), iv(a, sp.oo), label='Concave up on', noneText='Never concave up', level=2,
                          hint="Find $f''(x)$ and see where it is positive.", explain="$f''(x) = 6x %s$, which is positive for $x > %s$." % (('- %d' % (6 * a)) if a > 0 else '+ %d' % (-6 * a), str(a).replace('-', '−'))))
        assert sp.expand(sp.diff(f, x, 2) - (6 * x - 6 * a)) == 0
    for p, q in [(0, 2), (-1, 1), (1, 3), (-2, 0), (-3, 1), (0, 4), (-1, 2), (1, 2)]:           # level 3: concavity of a quartic
        n += 1
        c = [1, -2 * (p + q), 6 * p * q, 0, 0]
        f = sum(co * x ** (4 - i) for i, co in enumerate(c))
        d2 = [12, -12 * (p + q), 12 * p * q]
        assert sp.expand(sp.diff(f, x, 2) - sum(co * x ** (2 - i) for i, co in enumerate(d2))) == 0
        qid = 'G%d' % n
        P.append(STEPS(qid, 'Find where this graph bends each way.\n$$f(x) = %s$$' % _show_neg(c), [
            E(d, qid + '.1', "Find $f''(x)$.", app_poly(d2), sp.diff(f, x, 2), label="$f''(x)$ =", keys=[], hint='Differentiate twice.', work="$f''(x) = %s$" % _show_neg(d2)),
            INTERVAL(qid + '.2', 'Where is $f$ concave **down**?', iv(p, q), label='Concave down on', noneText='Never concave down',
                     hint="$f''(x) = 12(x %s)(x %s)$. Where is it negative?" % (('+ %d' % -p) if p < 0 else '- %d' % p, ('+ %d' % -q) if q < 0 else '- %d' % q), explain="$f''$ is negative between its two zeros."),
            CRIT(qid + '.3', 'Find the $x$-value of every inflection point.', [p, q], '$x$ =', noneText='No inflection points', hint='Where does the concavity change?',
                 explain="$f''$ changes sign at both zeros, so both are inflection points."),
        ], level=3, title='Concavity'))
    for p, q in [(-1, 3), (0, 2), (-2, 2), (1, 5), (-3, 1), (-4, -2)]:                           # level 3: second derivative test from scratch
        n += 1
        c = cubic(p, q)
        f = sum(co * x ** (3 - i) for i, co in enumerate(c))
        qid = 'G%d' % n
        vp, vq = 6 * (p - q), 6 * (q - p)
        opts = ['local max', 'local min', 'test fails']
        P.append(STEPS(qid, 'Use the second derivative test on\n$$f(x) = %s$$\nThe critical numbers are $x$ = %s and $x$ = %s.' % (_show_neg(c), str(p).replace('-', '−'), str(q).replace('-', '−')), [
            E(d, qid + '.1', "Find $f''(x)$.", app_poly([12, -6 * (p + q)]), sp.diff(f, x, 2), label="$f''(x)$ =", keys=[], hint="$f'(x) = %s$." % _show_neg([6, -6 * (p + q), 6 * p * q]), work="$f''(x) = %s$" % _show_neg([12, -6 * (p + q)])),
            dict(MC(qid + '.2', "$f''(%s)$ = %s. So $x$ = %s is a…" % (p, str(vp).replace('-', '−'), str(p).replace('-', '−')), opts, 0, fixed=True, hint='Negative means frown.', explain='Concave down at a flat spot: local max.')),
            dict(MC(qid + '.3', "$f''(%s)$ = %s. So $x$ = %s is a…" % (q, vq, str(q).replace('-', '−')), opts, 1, fixed=True, hint='Positive means cup.', explain='Concave up at a flat spot: local min.')),
        ], level=3, title='Second derivative test'))
    d.drill('practice', 'Practice', P, 'pool')
    return [d]


# ====================================================================== Day 28: curve sketching and its review stops
def deck_curve():
    lesson = [
        MATCH('L0', 'A sketch is built from two signs. Match each pair of signs with the shape of the graph there.',
              [["$f' > 0$, $f'' > 0$", 'Rising, bending up'], ["$f' > 0$, $f'' < 0$", 'Rising, bending down'], ["$f' < 0$, $f'' > 0$", 'Falling, bending up'], ["$f' < 0$, $f'' < 0$", 'Falling, bending down']],
              hint="$f'$ says up or down. $f''$ says cup or frown.", explain='The first derivative gives the direction and the second gives the bend.'),
        Sl('curve', 'L16', explain='Start with where the function lives and finish with the drawing. The review stops next to this one cover the first four.'),
        Sl('curve', 'L17'), Sl('curve', 'L18', text='One with asymptotes: $f(x) = frac{x^2 + 2x + 1}{x^2}$. Place the data, mark the regions, and sketch. Draw each piece as its own stroke.')]
    theory = [
        MC('H1', "On an interval, $f' < 0$ and $f'' > 0$. The graph there is…", ['falling and bending up', 'falling and bending down', 'rising and bending up', 'rising and bending down'],
           hint="$f'$ is the direction. $f''$ is the bend.", explain='Negative slope, so falling. Positive second derivative, so cupped upward.'),
        TF('H2', 'The graph of a function can cross its **horizontal** asymptote.', True, hint='A horizontal asymptote only describes the far left and far right.',
           explain='$f(x) = frac{x}{x^2 + 1}$ has the asymptote $y = 0$ and crosses it at the origin.'),
        TF('H3', 'The graph of a function can cross its **vertical** asymptote.', False, hint='What is true about $f$ at that $x$?', explain='The function is not defined there, so there is no point of the graph on that line.'),
        MC('H4', '$f$ has a vertical asymptote at $x$ = 2. How should the sketch handle it?', ['A dashed vertical line at $x$ = 2, with each side drawn as its own piece', 'One smooth curve passing through $x$ = 2', 'A dot at $(2, 0)$'],
           hint='The graph never touches that line.', explain='Draw the asymptote first, then sketch the left piece and the right piece separately.'),
        MC('H5', "$f'$ changes from + to − at $x$ = 1, and $f(1) = 4$. What goes on the sketch?", ['A hilltop at $(1, 4)$', 'A valley at $(1, 4)$', 'An inflection point at $(1, 4)$', 'An $x$-intercept at $x$ = 1'],
           hint='Rising, then falling.', explain='Rising then falling is a local max, at the point $(1, 4)$.'),
        MC('H6', "$f$ is undefined at $x$ = 0. On the sign chart for $f'$, that point…", ['still splits the number line', 'is left off', 'ends the chart'],
           hint='Can the sign of $f\'$ change across a vertical asymptote?', explain="It is not a critical number, but $f'$ can change sign there, so it splits the chart."),
    ]
    P = Q('curve', 'data', ['D2', 'D6', 'D11', 'D13', 'D14', 'D17', 'D18', 'D23', 'D25', 'D26', 'D28', 'D30', 'D31'], level=1)
    P += Q('curve', 'sketch', level=2) + Q('curve', 'full', level=3)
    return [build('curve', 'Curve Sketching', 'Put the whole picture together: the data first, then the drawing.', [(None, lesson)], theory, P, graphs=src('curve').get('graphs'), setSize=8)]


def review_deck(dk, title, subtitle, keep, levels):
    sl = slides(dk)
    lesson = [Sl(dk, k) for k in keep]
    P = []
    for kind, L in levels.items():
        P += Q(dk, kind, level=L)
    P += [lv(s, 1) for k, s in sl.items() if k not in keep and s['type'] in DRILLABLE]
    return build(dk, title, subtitle, [(None, lesson)], [], P, graphs=src(dk).get('graphs'), optional=True)


def deck_reviews():
    return [
        review_deck('geom', 'Standard Geometry', 'Review: area, volume and perimeter formulas, the Pythagorean theorem and similar triangles.', ['L1', 'L2', 'L4', 'L7', 'L8'], {'formulas': 1, 'use': 2}),
        review_deck('domain', 'Domain', 'Review: where a function is defined.', ['L1', 'L2', 'L3', 'L4', 'L7'], {'rules': 1, 'find': 2}),
        review_deck('intercepts', 'Intercepts', 'Review: where a graph crosses the axes.', ['L1', 'L2', 'L3', 'L4', 'L5'], {'y': 1, 'x': 2}),
        review_deck('asym', 'Asymptotes', 'Review: vertical, horizontal and slant asymptotes.', ['L1', 'L3', 'L4', 'L5', 'L7'], {'vert': 1, 'horiz': 2, 'slant': 3}),
        review_deck('longdiv', 'Long Division', 'Review: polynomial long division for slant asymptotes.', ['L1', 'L2', 'L3', 'L4', 'L5'], {'slant': 2, 'divide': 3}),
    ]


# ====================================================================== Day 29: L'Hopital
def deck_lhop():
    a = [Sl('lhop', 'F1'),
         Sl('lhop', 'F5', text='That $0/0$ limit came out to 1. But $frac{x^2}{x}$ → 0 and $frac{x}{x^2}$ → ∞ as $x$ → $0^+$, and those are $0/0$ battles too. What can a $0/0$ limit turn out to be?',
            hint='Three limits of the same form gave three different answers.'),
         Sl('lhop', 'R1'), Sl('lhop', 'R4'), Sl('lhop', 'R7'), Sl('lhop', 'R10')]
    a[3]['explain'] = 'Only $0/0$ and $∞/∞$. Other forms must be rewritten first (the next lesson).'
    b = [Sl('lhop', 'O1'), Sl('lhop', 'O2'), Sl('lhop', 'O4'), Sl('lhop', 'O5')]
    sl = slides('lhop')
    tids = ['TF1', 'TF5', 'TF17', 'TF24', 'TF27', 'TF32']
    theory = Q('lhop', 'forms', tids) + [copy.deepcopy(sl['R5']), copy.deepcopy(sl['R6'])]
    P = (Q('lhop', 'forms', level=1, skip=tids) + Q('lhop', 'basic', level=by_type({'num': 2, 'steps': 3}, 1)) + Q('lhop', 'other', level=by_type({'num': 3, 'steps': 3}, 1))
         + [lv(sl[k], 2) for k in ('R8', 'R11', 'R12')] + [lv(sl[k], 3) for k in ('O8', 'O9')])
    return [build('lhop', "L'Hopital's Rule", 'Indeterminate forms, using derivatives to beat 0/0 and ∞/∞, and turning the other five forms into those two.',
                  [('Indeterminate forms and the rule', a), ('The other five forms', b)], theory, P, graphs=src('lhop').get('graphs'))]


# ====================================================================== Days 30 and 31: optimization
def deck_opt():
    setup = src('opt')['drills']['setup']['questions']
    groups = {}
    for q in setup:
        if '\n' in q.get('text', '') and q['text'].startswith('**'):
            head, body = q['text'].split('\n', 1)
            groups.setdefault(body, []).append((head, q))
    bodies = list(groups)
    full = bodies[2::3]                                    # every third problem becomes one whole set-up problem (level 3)
    tids = ['S60', 'S61', 'S10', 'S12', 'S46']
    theory = Q('opt', 'setup', tids) + [TF('T1', 'Before you differentiate, the function you are optimizing should be written with only **one** variable.', True,
                                           hint='What is the constraint for?', explain='The constraint lets you replace one variable, so the function has a single variable and an ordinary derivative.')]
    P, n = [], 0
    for body in bodies:
        parts = groups[body]
        if body in full and len(parts) >= 2 and not any(q['id'] in tids for _, q in parts):
            n += 1
            steps = []
            for head, q in sorted(parts, key=lambda hq: 0 if 'optimized' in hq[0] else 1 if 'constraint' in hq[0] else 2):
                s = copy.deepcopy(q)
                s['text'] = head.strip('*').strip() if not head.startswith('**') else head
                s.pop('id')
                steps.append(s)
            P.append(STEPS('U%d' % n, body, steps, level=3, title='Set it up'))
        else:
            for head, q in parts:
                if q['id'] not in tids:
                    P.append(lv(q, 2 if q['type'] == 'expr' else 1))
    lesson = [Sl('opt', k) for k in ('L1', 'L2', 'L3', 'L4', 'L5', 'L6')]
    d1 = build('opt', 'Optimization', 'Turn a word problem into a function. Step one: what is being optimized?', [(None, lesson)], theory, P)

    # ---- Optimization II (day 31)
    L2 = [Sl('opt', 'L7', text='Back to the pen along the river. The area is\n$$A(x) = x(1200 - 2x)$$\nfor $x$ between 0 and 600. Find $A\'(x)$.'),
          Sl('opt', 'L8'), Sl('opt', 'L9'), Sl('opt', 'L10'), Sl('opt', 'L11'), Sl('opt', 'L12')]
    theory2 = Q('opt', 'setup', ['S62', 'S63']) + [
        MC('T1', 'A continuous function on a closed interval $[a, b]$ has its absolute maximum…', ['at a critical number or at an endpoint', 'always at a critical number', 'always at an endpoint', "wherever $f'' = 0$"],
           hint='This is the closed interval method.', explain='Compare the values at the critical numbers and at both endpoints. The largest one wins.'),
        MC('T2', 'A problem asks for the **dimensions** of the largest pen, and you find $x$ = 300. Are you done?', ['No. Find $y$ too, and answer the question that was asked', 'Yes', "No. Compute $A''(300)$ and stop there"],
           hint='Read the last sentence of the problem again.', explain='Dimensions means both sides. Always go back and answer what was asked.'),
        TF('T3', "If the function has only one critical number in its interval and $f''$ is negative there, that critical number gives the absolute maximum.", True,
           hint='One hilltop and no valleys.', explain='With a single critical number, a local max there is the absolute max.'),
        MC('T4', 'In the fence problem, $x$ has to be between 0 and 600. Where do those limits come from?', ['Lengths cannot be negative: $x ≥ 0$ and $y = 1200 - 2x ≥ 0$', 'From the second derivative', "From solving $A'(x) = 0$", 'They are a guess'],
           hint='What must be true of the two sides of a real pen?', explain='Both sides have to be at least 0. That gives the interval to search.'),
    ]
    P2 = Q('opt', 'solve', level=3)
    n = 0
    for q in setup:
        if q['type'] != 'expr' or '\n' not in q['text']:
            continue
        v = sp.Symbol(q['vars'][0], positive=True)
        f = sp.sympify(q['answer'].replace('^', '**'), locals={q['vars'][0]: v, 'pi': sp.pi})
        try:
            cs = [c for c in sp.solve(sp.diff(f, v), v) if c.is_real and c > 0 and sp.N(f.subs(v, c)).is_real]
        except Exception:
            cs = []
        if len(cs) != 1:
            continue
        c = cs[0]
        cv = float(c)
        f2 = float(sp.diff(f, v, 2).subs(v, c))
        if abs(f2) < 1e-9:
            continue
        n += 1
        name = q['label'].replace(' =', '').strip().strip('$')
        if not re.fullmatch(r"[A-Za-z](\^2)?\([a-z]\)", name):
            continue
        shown = q.get('show', M(q['answer'])).strip('$')
        var = q['vars'][0]
        exact = abs(cv - round(cv, 2)) < 1e-9
        cshow = num(round(cv, 2)) if exact else num(round(cv, 3))
        P2.append(N('C%d' % n, '$$%s = %s$$\nFind the critical number with $%s > 0$.%s' % (name, shown, var, '' if exact else ' A decimal is fine.'), num(round(cv, 2)) if exact else round(cv, 4), label='$%s$ %s' % (var, '=' if exact else '≈'),
                    tol=None if exact else 0.01, level=2, hint='Differentiate, set the derivative equal to 0, and solve.', explain='The derivative is 0 at $%s$ %s %s.' % (var, '=' if exact else '≈', cshow)))
        f2s = str(num(round(f2, 3))).replace('-', '−')
        if n % 2:
            continue
        f2x = abs(f2 - round(f2)) < 1e-9
        P2.append(MC('K%d' % n, ('For $%s = %s$, the only critical number with $%s > 0$ is $%s$ %s %s, and the second derivative there is ' + ('' if f2x else 'about ') + '%s. So that critical number gives a…') % (name, shown, var, var, '=' if exact else '≈', cshow, f2s),
                     ['maximum', 'minimum', 'neither'], 0 if f2 < 0 else 1, fixed=True, level=1, hint='Negative second derivative: frown. Positive: cup.',
                     explain='The second derivative is %s there, so the graph is concave %s: a %s.' % ('negative' if f2 < 0 else 'positive', 'down' if f2 < 0 else 'up', 'maximum' if f2 < 0 else 'minimum')))
    d2 = build('opt2', 'Optimization II', 'Finish the job: the derivative, the critical number, the check, and the answer to the question asked.', [(None, L2)], theory2, P2, setSize=9)
    return [d1, d2]


# ====================================================================== Chapter review
def deck_review():
    r = src('review3')
    lesson = [Sl('review3', k) for k in ('L1', 'L3', 'L5', 'L8', 'L9', 'L12')]
    tool = {'title': 'Which tool?', 'mode': 'pool', 'setSize': 10, 'questions': [lv(q, 1) for q in r['drills']['tool']['questions']]}
    mixed = Q('review3', 'theory', level=1) + Q('review3', 'problems', level=by_type({'multi': 3, 'steps': 3}, 2))
    exam = copy.deepcopy(r['drills']['exam'])
    d = build('review3', 'Chapter Review: Applications', 'A warm-up, mixed practice from every stop, and a practice test scored by topic.', [(None, lesson)], [], mixed, graphs=r.get('graphs'), optional=True,
              more={'tool': tool, 'exam': exam})
    d.d['drills'] = {'tool': d.d['drills']['tool'], 'practice': d.d['drills']['practice'], 'exam': d.d['drills']['exam']}
    d.d['drills']['practice']['title'] = 'Mixed practice'
    return [d]


# ====================================================================== the map, by class day
def write_map():
    days = [(22, [('geom', 'review', 28), ('related', 'main', 72)]), (23, [('related2', 'main', 50)]), (24, [('lin', 'main', 28), ('newton', 'main', 72)]), (25, [('max', 'main', 50)]),
            (26, [('mvt', 'main', 28), ('incdec', 'main', 72)]), (27, [('concavity', 'main', 50)]),
            (28, [('domain', 'review', 16), ('intercepts', 'review', 50), ('asym', 'review', 84)], [('longdiv', 'review', 28), ('curve', 'main', 72)]),
            (29, [('lhop', 'main', 50)]), (30, [('opt', 'main', 50)]), (31, [('opt2', 'main', 50)])]
    info = {
        'geom': ('geom', 'Standard Geometry', None, 'Review: area, volume and perimeter formulas, and similar triangles.'),
        'related': ('related', 'Related Rates', None, 'Every variable is a function of time: differentiate, then plug in.'),
        'related2': ('related2', 'Related Rates II', None, 'Harder geometry and harder reading: cones, shadows, angles and moving cars.'),
        'lin': ('linear', 'Linearization and Differentials', 'Linearization', 'Approximating a function with its tangent line.'),
        'newton': ('newton', "Newton's Method", None, 'Using tangent lines to home in on a root.'),
        'max': ('maxmin', 'Max and Mins', None, 'Highest and lowest points: absolute and local extremes, critical points, and how to find them.'),
        'mvt': ('mvt', 'Mean Value Theorem', None, 'Where the slope of a tangent equals the average slope.'),
        'incdec': ('incdec', 'Increasing, Decreasing and the First Derivative Test', 'First Derivative Test', 'What the sign of f′ says about f, and how to find local highs and lows with it.'),
        'concavity': ('concavity', 'Concavity and the Second Derivative Test', 'Concavity', 'How a graph bends, where the bend changes, and a second way to sort critical numbers.'),
        'domain': ('domain', 'Domain', None, 'Review: where a function is defined.'),
        'intercepts': ('intercepts', 'Intercepts', None, 'Review: where a graph crosses the axes.'),
        'asym': ('asym', 'Asymptotes', None, 'Review: vertical, horizontal and slant asymptotes.'),
        'longdiv': ('longdiv', 'Long Division', None, 'Review: polynomial long division for slant asymptotes.'),
        'curve': ('curve', 'Curve Sketching', None, 'Put the whole picture together: the data first, then the drawing.'),
        'lhop': ('lhop', "L'Hopital's Rule", None, 'Indeterminate forms, then using derivatives to beat 0/0 and ∞/∞, then the other five forms.'),
        'opt': ('opt', 'Optimization', None, 'Turn a word problem into a function. Step one: what is being optimized?'),
        'opt2': ('opt2', 'Optimization II', None, 'Finish the job: the derivative, the critical number, the check, and the answer to the question asked.'),
    }
    nodes = [{'id': 'start', 'kind': 'start', 'title': 'Start', 'x': 50, 'y': 10, 'deck': None, 'requires': [], 'blurb': 'Tap a stop on the map to walk there.'}]
    regions, y, prev = [], 22, 'start'
    for day, *rows in days:
        h = 31 + 30 * (len(rows) - 1)
        regions.append({'label': 'Day %d' % day, 'x': 3, 'y': y, 'w': 94, 'h': h})
        mains = [nid for row in rows for nid, kind, _ in row if kind == 'main']
        for ri, row in enumerate(rows):
            for nid, kind, px in row:
                deck, title, label, blurb = info[nid]
                n = {'id': nid, 'kind': kind, 'title': title}
                if label:
                    n['label'] = label
                n.update({'x': px, 'y': y + 18 + 30 * ri, 'deck': deck, 'blurb': blurb})
                if kind == 'main':
                    n['requires'] = [prev]
                else:
                    n['requires'] = [prev]
                    n['from'] = [mains[-1]]
                nodes.append(n)
        prev = mains[-1]
        y += h + 5
    nodes.append({'id': 'review', 'kind': 'boss', 'title': 'Chapter Review', 'x': 50, 'y': y + 14, 'deck': 'review3', 'requires': ['opt2'],
                  'blurb': 'A warm-up, mixed practice from every stop, and a practice test scored by topic.'})
    m = {'course': 'Calculus 1', 'world': 3, 'id': 'applications', 'title': 'Applications of Derivatives', 'short': 'Applications', 'height': y + 34, 'regions': regions, 'nodes': nodes}
    with open(os.path.join(ROOT, 'maps', 'applications.json'), 'w') as f:
        json.dump(m, f, indent=1, ensure_ascii=False)
        f.write('\n')


if __name__ == '__main__':
    decks = (deck_related() + deck_linear() + deck_newton() + deck_maxmin() + deck_mvt() + deck_incdec() + deck_concavity() + deck_curve()
             + deck_reviews() + deck_lhop() + deck_opt() + deck_review())
    for d in decks:
        used = set(re.findall(r'"graph": "([^"]+)"', json.dumps({k: v for k, v in d.d.items() if k != 'graphs'})))
        d.d['graphs'] = {k: v for k, v in d.d.get('graphs', {}).items() if k in used}
        d.save()
        dr = d.d['drills']
        L = [d.d['lesson']] if d.d.get('lesson') else d.d.get('lessons', [])
        pr = dr.get('practice', {}).get('questions', [])
        print('%-11s lesson %-8s theory %2d  practice %3d  levels %s' % (d.id, '+'.join(str(len(l['slides'])) for l in L), len(dr.get('theory', {}).get('questions', [])), len(pr),
                                                                       [sum(1 for q in pr if q.get('level') == k) for k in (1, 2, 3)]))
    write_map()
    write_manifest('world3')
