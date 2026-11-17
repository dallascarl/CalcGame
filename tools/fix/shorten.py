"""Long typed answers become multiple choice (Dallas, Nov 16, 2026: "too much typing is going to be killer").
Any formula answer of LIMIT characters or more, in a lesson or a drill, is turned into a four-way choice. The wrong
choices are the classic slips (a dropped chain-rule factor, a flipped sign, sin for cos, a number off by one, an
upside-down fraction), and each is checked with the app's own parser to make sure it really is wrong.
   python3 tools/fix/shorten.py          (-n to only report)"""
import json, glob, os, re, sys, random, subprocess, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'gen'))
from lib import _top, _strip
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
LIMIT = 16


FN = ('arcsin', 'arccos', 'arctan', 'sinh', 'cosh', 'tanh', 'sqrt', 'cbrt', 'sin', 'cos', 'tan', 'sec', 'csc', 'cot', 'ln', 'log', 'abs')


def _open(s, j):
    """index of the bracket that closes at j"""
    d = 0
    for i in range(j, -1, -1):
        d += s[i] == ')'; d -= s[i] == '('
        if d == 0:
            return i
    return 0


def _close(s, i):
    d = 0
    for j in range(i, len(s)):
        d += s[j] == '('; d -= s[j] == ')'
        if d == 0:
            return j
    return len(s) - 1


def _bare(t):
    t = t.strip()
    return t[1:-1].strip() if t.startswith('(') and _close(t, 0) == len(t) - 1 else t


def fracs(s):
    """draw every division as a stacked fraction, reading a/b the way the app does (b is one factor)"""
    while True:
        k = s.find('/')
        if k < 0:
            return s
        # left operand: the product just before the slash
        a = k
        while a > 0 and s[a - 1] == ' ':
            a -= 1
        end_l = a
        while True:
            if a > 0 and s[a - 1] == ')':
                a = _open(s, a - 1)
                for f in FN:
                    if s[:a].endswith(f) and not s[:a - len(f)][-1:].isalpha():
                        a -= len(f); break
            elif a > 0 and s[a - 1] == '}':
                d = 0
                while a > 0:
                    a -= 1; d += s[a] == '}'; d -= s[a] == '{'
                    if d == 0 and s[a] == '{' and not s[:a].endswith('}'):
                        break
                a -= 4 if s[:a].endswith('frac') else 0
            else:
                b = a
                while a > 0 and (s[a - 1].isalnum() or s[a - 1] in "._'"):
                    a -= 1
                if a == b:
                    break
            if a > 0 and s[a - 1] == '^':
                a -= 1; continue
            break
        # right operand: one factor, with its power
        b = k + 1
        while b < len(s) and s[b] == ' ':
            b += 1
        st = b
        m = re.match(r'\d+\.?\d*', s[b:])
        if m:
            b += m.end()
        else:
            f = next((f for f in FN if s.startswith(f + '(', b)), None)
            if f:
                b = _close(s, b + len(f)) + 1
            elif b < len(s) and s[b] == '(':
                b = _close(s, b) + 1
            else:
                m = re.match(r"[A-Za-z]'?", s[b:]); b += m.end() if m else 0
        while b < len(s) and s[b] == '^':
            b = _close(s, b + 1) + 1 if s[b + 1:b + 2] == '(' else b + 1 + (re.match(r'-?\w+', s[b + 1:]) or re.match('', '')).end()
        L, R = s[a:end_l], s[st:b]
        if not L.strip() or not R.strip():
            return s.replace('/', '÷')
        s = s[:a] + 'frac{' + _bare(L) + '}{' + _bare(R) + '}' + s[b:]


def mk(s):
    """app syntax -> the markup the app draws"""
    return '$' + fracs(s.replace('*', '·')).strip() + '$'


def cands(s):
    """(kind, wrong answer) pairs"""
    out = []
    # a chain-rule factor left off: drop a bracketed factor at either end
    d, cut = 0, []
    for i, c in enumerate(s):
        d += c == '('; d -= c == ')'
        if c == ')' and d == 0 and i + 1 < len(s) and s[i + 1] == '(':
            cut.append(i + 1)
    for i in cut:
        out += [('drop', s[:i]), ('drop', s[i:])]
    for m in re.finditer(r'(?<=[\w)\'])\s*([+\-])\s*(?=[\w(])', s):
        if s[:m.start()].count('(') - s[:m.start()].count(')') <= 1:
            out.append(('sign', s[:m.start(1)] + ('-' if m.group(1) == '+' else '+') + s[m.end(1):]))
    for a, b in (('sin(', 'cos('), ('cos(', 'sin('), ('sec(', 'tan('), ('tan(', 'sec('), ('ln(', 'e^('), ('arcsin(', 'arctan('), ('arctan(', 'arcsin(')):
        for m in re.finditer(re.escape(a), s):
            if m.start() == 0 or not s[m.start() - 1].isalpha():
                out.append(('swap', s[:m.start()] + b + s[m.end():]))
    for m in list(re.finditer(r'(?<![\w.])\d+(?![\w.]*\()', s))[:5]:
        n = int(m.group())
        for v in ([n + 1, n - 1] if n > 1 else [n + 1]):
            out.append(('num', s[:m.start()] + str(v) + s[m.end():]))
    sl = _top(s, '/')
    if len(sl) == 1:
        A, B = s[:sl[0]], s[sl[0] + 1:]
        out.append(('flip', '(' + B.strip() + ')/(' + A.strip() + ')'))
        if B.strip().endswith('^2'):
            out.append(('flip', A + '/' + B.strip()[:-2]))
    for m in re.finditer(r'\^2(?!\d)', s):
        out.append(('pow', s[:m.start()] + s[m.end():]))
    for a, b2 in (('sinh(', 'cosh('), ('cosh(', 'sinh('), ('sqrt(', '(')):
        for m in re.finditer(re.escape(a), s):
            out.append(('swap', s[:m.start()] + b2 + s[m.end():]))
    tops = [i for i in _top(s, '+-') if i > 0 and s[i - 1] not in '(^*/']
    if tops:                                   # a whole term forgotten
        out += [('term', s[:tops[-1]]), ('term', s[tops[0] + 1:] if s[tops[0]] == '+' else s[tops[0]:])]
    for m in re.finditer(r"(?<=[a-z])'", s):   # a prime left off
        out.append(('term', s[:m.start()] + s[m.end():]))
    if s.startswith('-'):
        out.append(('neg', s[1:].lstrip()))
    elif not [i for i in _top(s, '+-') if i > 0]:
        out.append(('neg', '-' + s))
    seen, res = {s}, []
    for k, c in out:
        c = c.strip()
        if c and c not in seen and c.count('(') == c.count(')'):
            seen.add(c); res.append((k, c))
    return res


def exprs(q, acc, key=None):
    key = q.get('id') or key
    if q.get('type') == 'expr' and not q.get('template'):
        a = q['answer'] if isinstance(q['answer'], str) else q['answer'][0]
        if len(a.replace(' ', '')) >= LIMIT:
            acc.append((key, q))
    for i, st in enumerate(q.get('steps', []), 1):
        exprs(st, acc, '%s.%d' % (key, i))


decks, todo = {}, []
for f in sorted(glob.glob(os.path.join(ROOT, 'decks', '*.json'))):
    d = json.load(open(f)); decks[f] = d
    items = [s for L in [d.get('lesson')] + list(d.get('lessons', [])) if L for s in L['slides']] + [q for dr in d['drills'].values() for q in dr['questions']]
    for q in items:
        acc = []; exprs(q, acc)
        todo += [(d['id'] + '|' + k, e) for k, e in acc]
jobs = {}
for dk, q in todo:
    a = q['answer'] if isinstance(q['answer'], str) else q['answer'][0]
    cs = cands(a)
    jobs[dk] = {'answer': a, 'vars': q.get('vars'), 'ranges': q.get('ranges'), 'upToC': bool(q.get('upToC')), 'cands': [c for _, c in cs], 'kinds': [k for k, _ in cs]}
with tempfile.TemporaryDirectory() as tmp:
    jp, op = os.path.join(tmp, 'j.json'), os.path.join(tmp, 'o.json')
    json.dump(jobs, open(jp, 'w'))
    subprocess.run(['node', os.path.join(os.path.dirname(__file__), 'shorten_check.js'), jp, op], check=True)
    res = json.load(open(op))
done, skipped = 0, []
ORDER = ['drop', 'sign', 'swap', 'num', 'pow', 'flip', 'term', 'neg']
for dk, q in todo:
    key = dk; j, r = jobs[key], res[key]
    good = r.get('good', [])
    if len(good) < 3:
        skipped.append((key, j['answer'], r.get('err') or len(good))); continue
    rng = random.Random(key)
    by = {}
    for i in good:
        by.setdefault(j['kinds'][i], []).append(j['cands'][i])
    for v in by.values():
        rng.shuffle(v)
    pick = []
    while len(pick) < 3:
        for k in ORDER:
            if by.get(k) and len(pick) < 3:
                pick.append(by[k].pop())
    tail = ' + C' if q.get('upToC') else ''
    opt = lambda s: mk(s)[:-1] + tail + '$'
    t, label = (q.get('text') or '').rstrip(), (q.get('label') or '').strip()
    core = label.rstrip('=').strip().strip('$')
    if label and core and core not in t:
        t = (t + '\n' if t else '') + label
    t = re.sub(r"\s*\(?Type \$[^.]*\.\)?", '', t).strip()
    keep = {k: q[k] for k in ('id', 'level', 'hint', 'explain', 'work', 'graph', 'title', 'topic') if k in q}
    q.clear()
    q.update(keep, type='mc', text=t, options=[opt(j['answer'])] + [opt(c) for c in pick], answer=0)
    done += 1
print('long typed answers:', len(todo), '-> multiple choice:', done, '| left alone:', len(skipped))
for s in skipped:
    print('  ', s)
if '-n' not in sys.argv:
    for f, d in decks.items():
        with open(f, 'w') as fh:
            json.dump(d, fh, indent=1, ensure_ascii=False); fh.write('\n')
