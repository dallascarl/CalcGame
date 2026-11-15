"""One-time layout pass over every deck, from Dallas's review notes (Oct 23-28, 2026):
  * "It's better to have the question on a separate line": a question that opens with a formula
    ("$f(x) = x^2 - 3x$. Find $f(-2)$.") now shows the formula in a box on its own line ($$...$$).
  * "better notation ... for piecewise functions": "f(x) = A for x < a and f(x) = B for x >= a" becomes a
    real piecewise brace (cases{...}), also in a box.
  * "Latex not rendered": answer labels that used math markup outside $...$.
Safe to run again: text that is already converted is left alone.  python3 tools/fix/layout.py"""
import json, glob, re, os
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PW = re.compile(r'^(?:Piecewise(?: functions)?: )?\$([a-zA-Z])\(x\) = ([^$]+)\$ for \$(x [^$]+)\$ and \$\1\(x\) = ([^$]+)\$ for \$(x [^$]+)\$\. ')
DEFN = re.compile(r'^\$([a-zA-Z]\([a-z]\) = [^$]+)\$\. (?=\S)')
n = {'piecewise': 0, 'formula': 0, 'label': 0}


def text(t):
    m = PW.match(t)
    if m:
        n['piecewise'] += 1
        return f'$${m.group(1)}(x) = cases{{{m.group(2)}, {m.group(3)}; {m.group(4)}, {m.group(5)}}}$$\n' + t[m.end():]
    m = DEFN.match(t)
    if m and 'cases{' not in m.group(1):
        n['formula'] += 1
        return f'$${m.group(1)}$$\n' + t[m.end():]
    return t


def label(v):
    if re.search(r'lim\[', re.sub(r'\$[^$]*\$', '', v)):
        n['label'] += 1
        return re.sub(r'(lim\[[^\]]*\])', r'$\1$', v)
    return v


def item(q):
    if isinstance(q.get('text'), str) and q.get('type') != 'bank':
        q['text'] = text(q['text'])
    if isinstance(q.get('label'), str):
        q['label'] = label(q['label'])
    for st in q.get('steps', []):
        item(st)


for f in sorted(glob.glob(os.path.join(ROOT, 'decks', '*.json'))):
    d = json.load(open(f))
    before = json.dumps(d, sort_keys=True)
    for L in [d.get('lesson')] + list(d.get('lessons', [])):
        if L:
            for s in L['slides']:
                item(s)
    for dr in d.get('drills', {}).values():
        for q in dr['questions']:
            item(q)
    if json.dumps(d, sort_keys=True) != before:
        with open(f, 'w') as fh:
            json.dump(d, fh, indent=1, ensure_ascii=False)
            fh.write('\n')
print(n)
