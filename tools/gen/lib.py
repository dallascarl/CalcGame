"""Helpers for building CalcGame decks.

The generator scripts in this folder WRITE decks/*.json. They are a starting point only:
once a deck is written, edit the JSON directly (on GitHub or on your computer). Running a
generator again overwrites its decks, so do that only for a deck nobody has hand-edited.

Every formula answer is written once, in the same syntax students type ("app syntax":
2x cos(x^2), e^(3x), sqrt(x+1), arctan(x)), and is checked two ways:
  * against a true answer computed with sympy, and
  * by the app's own parser (node tools/gen/verify.js), so what is graded is what was checked.
"""
import json, random, re, os
from fractions import Fraction
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application, convert_xor

x, y, u, h, t, a, b = sp.symbols('x y u h t a b')
yp = sp.Symbol('yp')        # y' (dy/dx) inside formulas
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MANIFEST = []               # (deck id, question id, answer string, vars, samples)
TRANS = standard_transformations + (implicit_multiplication_application, convert_xor)
LOCAL = {'e': sp.E, 'ln': sp.log, 'log': sp.log, 'arctan': sp.atan, 'arcsin': sp.asin, 'arccos': sp.acos,
         'pi': sp.pi, 'sec': sp.sec, 'csc': sp.csc, 'cot': sp.cot, 'sqrt': sp.sqrt, 'x': x, 'y': y, 'u': u,
         'h': h, 't': t, 'a': a, 'b': b, 'yp': yp, 'sinh': sp.sinh, 'cosh': sp.cosh, 'tanh': sp.tanh, 'abs': sp.Abs}


def S(s):
    """app syntax -> sympy"""
    s = s.replace("y'", ' yp ').replace('π', 'pi')
    s = re.sub(r'(arcsin|arccos|arctan|sinh|cosh|tanh|sqrt|sin|cos|tan|sec|csc|cot|ln)\(', r' \1(', s)
    return parse_expr(s, local_dict=dict(LOCAL), transformations=TRANS)


# ---------------------------------------------------------------- display
def _top(s, chars):
    """positions of chars at paren depth 0"""
    d, out = 0, []
    for i, c in enumerate(s):
        if c == '(':
            d += 1
        elif c == ')':
            d -= 1
        elif d == 0 and c in chars:
            out.append(i)
    return out


def _strip(s):
    s = s.strip()
    if s.startswith('(') and s.endswith(')'):
        d = 0
        for i, c in enumerate(s):
            d += c == '('
            d -= c == ')'
            if d == 0 and i < len(s) - 1:
                return s
        return s[1:-1]
    return s


def D(s, frac=True):
    """app syntax -> the math markup the app draws (put it inside $...$).
    A single top-level division becomes a stacked fraction."""
    s = s.replace("y'", "y'").replace('*', '·')
    if frac:
        sl = _top(s, '/')
        pm = [i for i in _top(s, '+-') if i > 0 and s[i - 1] not in '(^']
        if len(sl) == 1 and not pm:
            A, B = s[:sl[0]], s[sl[0] + 1:]
            neg = A.startswith('-')
            if neg:
                A = A[1:]
            if '{' not in A + B:
                return ('-' if neg else '') + 'frac{' + _strip(A) + '}{' + _strip(B) + '}'
    return s


def M(s, frac=True):
    return '$' + D(s, frac) + '$'


# ---------------------------------------------------------------- numbers
def num(v):
    v = float(sp.N(v))
    r = round(v, 6)
    return int(r) if abs(r - round(r)) < 1e-9 else r


def frac_str(q):
    q = sp.nsimplify(q)
    if q.is_Integer:
        return str(int(q))
    p, d = sp.fraction(q)
    return f'{p}/{d}'


def poly_str(coeffs, var='x'):
    """[a_n, ..., a_0] -> '3x^2 - 4x + 1' in app syntax"""
    n = len(coeffs) - 1
    parts = []
    for k, c in enumerate(coeffs):
        p = n - k
        if c == 0:
            continue
        c = sp.nsimplify(c)
        sign = '-' if c < 0 else '+'
        a_ = abs(c)
        cs = '' if (a_ == 1 and p > 0) else (str(a_) if a_.is_Integer else '(' + frac_str(a_) + ')')
        vs = '' if p == 0 else (var if p == 1 else f'{var}^{p}')
        parts.append((sign, cs + vs))
    if not parts:
        return '0'
    s = ('-' if parts[0][0] == '-' else '') + parts[0][1]
    for sign, body in parts[1:]:
        s += f' {sign} {body}'
    return s


def tidy(s):
    """light clean-up of an app-syntax string: + - -> -, 1x -> x"""
    s = re.sub(r'\+\s*-', '- ', s)
    s = re.sub(r'-\s*-', '+ ', s)
    s = re.sub(r'(?<![\d.])1(?=[a-z(])', '', s)
    return re.sub(r'\s+', ' ', s).strip()


# ---------------------------------------------------------------- verification
def samples(truth, vars_, ranges=None, n=8, seed=0):
    rng = random.Random(seed)
    syms = [yp if v == "y'" else sp.Symbol(v) for v in vars_]
    f = sp.lambdify(syms, truth, 'mpmath')
    out, tries = [], 0
    while len(out) < n and tries < 400:
        tries += 1
        env = {}
        for v in vars_:
            lo, hi = (ranges or {}).get(v, [0.35, 2.65])
            env[v] = lo + (hi - lo) * rng.random()
        try:
            val = complex(f(*[env[v] for v in vars_]))
        except Exception:
            continue
        if abs(val.imag) > 1e-9 or not (abs(val.real) < 1e12):
            continue
        out.append([env, val.real])
    if len(out) < 4:
        raise ValueError(f'could not sample truth {truth} on {ranges}')
    return out


def register(deck, qid, answer, vars_, truth, ranges=None, upToC=False):
    for k, ans in enumerate([answer] if isinstance(answer, str) else answer):
        MANIFEST.append({'deck': deck, 'id': qid, 'answer': ans, 'vars': vars_, 'upToC': upToC,
                         'samples': samples(truth, vars_, ranges, seed=hash((deck, qid, k)) & 0xffff)})


# ---------------------------------------------------------------- question builders
class Deck:
    def __init__(self, id, title, subtitle='', unit='', course='Calculus 1'):
        self.d = {'id': id, 'course': course, 'unit': unit, 'title': title, 'subtitle': subtitle,
                  'version': 2, 'graphs': {}, 'drills': {}}
        self.id = id
        self.n = 0
        self.keys = []      # the keys every formula question in this deck shows (plus what an answer needs)

    def qid(self, p):
        self.n += 1
        if p in ('T', 'L') and self.n < 20:
            self.n = 20
        return f'{p}{self.n}'

    def lesson(self, slides, optional=False, title=None):
        L = {'slides': slides}
        if title:
            L['title'] = title
        self.d['lesson'] = L
        if optional:
            self.d['lessonOptional'] = True

    def drill(self, kind, title, questions, mode, **kw):
        dr = {'title': title, 'mode': mode}
        dr.update(kw)
        dr['questions'] = questions
        self.d['drills'][kind] = dr

    def graph(self, name, g):
        self.d['graphs'][name] = g
        return name

    def save(self):
        ids = set()
        for L in [self.d.get('lesson')] + list(self.d.get('lessons', [])):
            if L:
                for s in L['slides']:
                    assert s['id'] not in ids, s['id']
                    ids.add(s['id'])
        for dr in self.d['drills'].values():
            for q in dr['questions']:
                assert q['id'] not in ids, (self.id, q['id'])
                ids.add(q['id'])
        with open(os.path.join(ROOT, 'decks', self.id + '.json'), 'w') as f:
            json.dump(self.d, f, indent=1, ensure_ascii=False)
            f.write('\n')


NAMES = ['sin(', 'cos(', 'tan(', 'sec(', 'csc(', 'cot(', 'sqrt(', 'e^(', 'ln(', 'arctan(', 'arcsin(', 'arccos(',
         'sinh(', 'cosh(', 'tanh(', 'pi']


def keys_for(answer, base):
    """the deck's usual keys, plus any the answer needs"""
    ks = list(base)
    for a in [answer] if isinstance(answer, str) else answer:
        for k in NAMES:
            stem = k.rstrip('(').replace('^', '')
            if k == 'e^(':
                need = re.search(r'(?<![a-z])e\^', a)
            elif k == 'pi':
                need = 'pi' in a
            else:
                need = re.search(r'(?<![a-z])' + re.escape(stem) + r'\(', a)
            if need and k not in ks:
                ks.append(k)
        if re.search(r'(?<![a-z])e(?![a-z^])', a) and 'e' not in ks:
            ks.append('e')
    return ks


def E(deck, qid, text, answer, truth, vars_=('x',), label=None, post=None, level=None, explain=None,
      ranges=None, keys=None, show=None, hint=None, work=None, title=None, topic=None, upToC=False):
    """a typed-formula question, checked against sympy truth (upToC: any antiderivative counts)"""
    vars_ = list(vars_)
    q = {'id': qid, 'type': 'expr'}
    if title:
        q['title'] = title
    if text:
        q['text'] = text
    q['answer'] = answer
    q['vars'] = vars_
    ks = keys_for(answer, deck.keys if keys is None else keys)
    if ks:
        q['keys'] = ks
    if label:
        q['label'] = label
    if post:
        q['post'] = post
    if ranges:
        q['ranges'] = ranges
    if upToC:
        q['upToC'] = True
    q['show'] = show or M(answer if isinstance(answer, str) else answer[0])
    if level:
        q['level'] = level
    if topic:
        q['topic'] = topic
    if hint:
        q['hint'] = hint
    if explain:
        q['explain'] = explain
    if work:
        q['work'] = work
    register(deck.id, qid, answer, vars_, sp.sympify(truth), ranges, upToC)
    return q


def N(qid, text, answer, label=None, tol=None, level=None, explain=None, hint=None, work=None, title=None, topic=None):
    q = {'id': qid, 'type': 'num'}
    if title:
        q['title'] = title
    q['text'] = text
    q['answer'] = num(answer)
    if label:
        q['label'] = label
    if tol is not None:
        q['tol'] = tol
    if level:
        q['level'] = level
    if topic:
        q['topic'] = topic
    if hint:
        q['hint'] = hint
    if explain:
        q['explain'] = explain
    if work:
        q['work'] = work
    return q


def MC(qid, text, options, answer=0, level=None, explain=None, hint=None, graph=None, fixed=None, work=None, title=None, topic=None):
    q = {'id': qid, 'type': 'mc'}
    if title:
        q['title'] = title
    q['text'] = text
    q['options'] = options
    q['answer'] = answer
    if graph:
        q['graph'] = graph
    if fixed:
        q['fixed'] = True
    if level:
        q['level'] = level
    if topic:
        q['topic'] = topic
    if hint:
        q['hint'] = hint
    if explain:
        q['explain'] = explain
    if work:
        q['work'] = work
    assert len(set(options)) == len(options), options
    return q


def TF(qid, text, answer, explain=None, hint=None, level=None, topic=None):
    q = {'id': qid, 'type': 'tf', 'text': text, 'answer': bool(answer)}
    if level:
        q['level'] = level
    if topic:
        q['topic'] = topic
    if hint:
        q['hint'] = hint
    if explain:
        q['explain'] = explain
    return q


def MATCH(qid, text, pairs, explain=None, hint=None, level=None, topic=None):
    q = {'id': qid, 'type': 'match', 'text': text, 'pairs': pairs}
    if level:
        q['level'] = level
    if topic:
        q['topic'] = topic
    if hint:
        q['hint'] = hint
    if explain:
        q['explain'] = explain
    return q


def PICK(qid, text, options, answers, explain=None, hint=None, level=None, topic=None):
    q = {'id': qid, 'type': 'pick', 'text': text, 'options': options, 'answers': answers}
    if level:
        q['level'] = level
    if topic:
        q['topic'] = topic
    if hint:
        q['hint'] = hint
    if explain:
        q['explain'] = explain
    return q


def ORDER(qid, text, items, explain=None, hint=None, level=None, topic=None):
    q = {'id': qid, 'type': 'order', 'text': text, 'items': items}
    if level:
        q['level'] = level
    if topic:
        q['topic'] = topic
    if hint:
        q['hint'] = hint
    if explain:
        q['explain'] = explain
    return q


def BANK(qid, text, blanks, distractors=(), explain=None, hint=None, level=None, topic=None):
    q = {'id': qid, 'type': 'bank', 'text': text, 'blanks': blanks, 'distractors': list(distractors)}
    if level:
        q['level'] = level
    if topic:
        q['topic'] = topic
    if hint:
        q['hint'] = hint
    if explain:
        q['explain'] = explain
    return q


def STEPS(qid, text, steps, level=None, explain=None, title=None, topic=None):
    for k, st in enumerate(steps):
        if not st.get('id'):
            st['id'] = f'{qid}.{k + 1}'
        st.pop('level', None)
    q = {'id': qid, 'type': 'steps'}
    if title:
        q['title'] = title
    q['text'] = text
    q['steps'] = steps
    if level:
        q['level'] = level
    if topic:
        q['topic'] = topic
    if explain:
        q['explain'] = explain
    return q


def LIM(qid, text, answer, label=None, level=None, explain=None, hint=None, work=None, tol=None, topic=None, graph=None):
    """a limit answer: a number, 'inf', '-inf' or 'DNE'"""
    q = {'id': qid, 'type': 'lim', 'text': text}
    q['answer'] = answer if isinstance(answer, str) else num(answer)
    if label:
        q['label'] = label
    if tol is not None:
        q['tol'] = tol
    if graph:
        q['graph'] = graph
    for k, v in (('level', level), ('topic', topic), ('hint', hint), ('explain', explain), ('work', work)):
        if v:
            q[k] = v
    return q


def lim_of(e, a0, dirn='+-'):
    """sympy limit as 'inf' / '-inf' / 'DNE' / number"""
    a0 = sp.sympify(a0)
    if dirn == '+-':
        L1, L2 = sp.limit(e, x, a0, '-'), sp.limit(e, x, a0, '+')
        if L1 != L2:
            return 'DNE'
        r = L1
    else:
        r = sp.limit(e, x, a0, dirn)
    if r == sp.oo:
        return 'inf'
    if r == -sp.oo:
        return '-inf'
    if not r.is_finite:
        return 'DNE'
    return r


def INFO(qid, text, title=None):
    q = {'id': qid, 'type': 'info'}
    if title:
        q['title'] = title
    q['text'] = text
    return q


def sp_app(e):
    """sympy -> app syntax (what a student would type)"""
    from sympy.printing.str import StrPrinter

    class P(StrPrinter):
        def _print_Pow(self, ex, rational=False):
            b, n = ex.as_base_exp()
            if b == sp.E:
                return 'e^(' + self._print(n) + ')'
            if n == sp.Rational(1, 2):
                return 'sqrt(' + self._print(b) + ')'
            if n == sp.Rational(-1, 2):
                return '1/sqrt(' + self._print(b) + ')'
            if isinstance(b, (sp.sin, sp.cos, sp.tan, sp.sec, sp.csc, sp.cot)) and n.is_Integer and n > 0:
                return self._print(b) + '^' + str(n)
            bs = self._print(b)
            if not (b.is_Symbol or (b.is_Integer and b > 0) or isinstance(b, sp.Function)):
                bs = '(' + bs + ')'
            if n.is_Integer and n > 0:
                return bs + '^' + str(n)
            return bs + '^(' + self._print(n) + ')'

        def _print_exp(self, ex):
            return 'e^(' + self._print(ex.args[0]) + ')'

        def _print_log(self, ex):
            return 'ln(' + self._print(ex.args[0]) + ')'

        def _print_atan(self, ex):
            return 'arctan(' + self._print(ex.args[0]) + ')'

        def _print_asin(self, ex):
            return 'arcsin(' + self._print(ex.args[0]) + ')'

        def _print_acos(self, ex):
            return 'arccos(' + self._print(ex.args[0]) + ')'

        def _print_Abs(self, ex):
            return 'abs(' + self._print(ex.args[0]) + ')'

        def _print_Symbol(self, ex):
            return "y'" if ex.name == 'yp' else ex.name

    s = P().doprint(e)
    s = s.replace('*', '')
    s = re.sub(r'(?<=[0-9])(?=[0-9])', '', s)
    return tidy(s)


def write_manifest(name):
    with open(os.path.join(ROOT, 'tools', 'gen', 'out', name + '.manifest.json'), 'w') as f:
        json.dump(MANIFEST, f)
    print(f'{len(MANIFEST)} formula answers to verify')
