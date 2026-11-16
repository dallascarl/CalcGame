"""Second layout pass, from Dallas's review notes of Nov 15-16, 2026 ("cluttered", "math looks bad inline",
"separate out the math on its own line", "less is more"):
  * a sentence that is only formulas ("$lim f = 2$ and $lim f = 5$.") becomes a boxed display, one formula per line
  * a sentence that ends in a big formula ("Find $lim[x->0] frac{..}{..}$.") puts that formula in a box under the words
  * "From class:" is dropped
Options, labels, hints and explanations are left alone. Safe to run again.   python3 tools/fix/layout2.py"""
import json, glob, re, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BIG = re.compile(r'frac\{|lim\[|int\[|sum\[|cases\{')
n = {'facts': 0, 'tail': 0, 'fromclass': 0}
SHOW = '-v' in sys.argv


def sentences(t):
    """split a line into sentences, never inside $...$"""
    out, cur, inm, i = [], '', False, 0
    while i < len(t):
        c = t[i]
        if c == '$':
            inm = not inm
        cur += c
        if not inm and c in '.?!:' and (i + 1 == len(t) or t[i + 1] == ' '):
            out.append(cur)
            cur = ''
            i += 1
            while i < len(t) and t[i] == ' ':
                i += 1
            continue
        i += 1
    if cur.strip():
        out.append(cur)
    return out


def big(m):
    return bool(BIG.search(m)) or len(m) >= 22


def one(sent):
    """a sentence -> list of blocks: ('t', text) or ('d', display math)"""
    s = sent.strip()
    parts = re.split(r'(\$[^$]+\$)', s)
    maths = [p[1:-1] for p in parts if p.startswith('$') and p.endswith('$') and len(p) > 2]
    words = ''.join(p for p in parts if not (p.startswith('$') and p.endswith('$') and len(p) > 2))
    # only formulas, joined by and / but / commas
    if maths and re.fullmatch(r'[\s,.;:]*((and|but|or|with|where|while)[\s,]*)*[\s,.;:]*', re.sub(r'\b(and|but|or|with|where|while)\b', r'\1', words).strip() or '') and any(big(m) or '=' in m for m in maths) and (len(maths) > 1 or big(maths[0])):
        if all(len(m) <= 60 for m in maths):
            n['facts'] += 1
            lead = 'but' in words.split()
            return [('d', ' ;; '.join(maths))] if not lead else [('d', ' ;; '.join(maths[:-1])), ('t', 'but'), ('d', maths[-1])] if len(maths) > 1 else [('d', maths[0])]
    # ends in one big formula
    m = re.fullmatch(r'(.*?\S)\s*\$([^$]+)\$\s*([.?:]?)', s, re.S)
    if m and big(m.group(2)) and '$$' not in s and not re.search(r'\$[^$]*$', m.group(1).replace('\\$', '')) and len(m.group(1)) >= 3:
        lead = m.group(1)
        if not lead.rstrip().endswith(('=', '(', ',')) and lead.count('$') % 2 == 0:
            n['tail'] += 1
            end = '' if m.group(3) in ('', '.', ':') else ''
            return [('t', lead + end), ('d', m.group(2))]
    return [('t', s)]


def text(t):
    if not isinstance(t, str) or '{{' in t:
        return t
    t2 = re.sub(r'^From class: (\w)', lambda m: m.group(1).upper(), t)
    if t2 != t:
        n['fromclass'] += 1
        t = t2
    lines = []
    for line in t.split('\n'):
        if '$$' in line or '$' not in line:
            lines.append(line)
            continue
        cur = ''
        for s in sentences(line):
            for kind, v in one(s):
                if kind == 't':
                    cur = (cur + ' ' + v).strip()
                else:
                    if cur:
                        lines.append(cur)
                        cur = ''
                    lines.append('$$' + v + '$$')
        if cur:
            lines.append(cur)
    out = '\n'.join(lines)
    out = re.sub(r'\$\$\n\$\$', ' ;; ', out) if False else out
    if SHOW and out != t:
        print('-', t.replace('\n', ' / ')); print('+', out.replace('\n', ' / ')); print()
    return out


def item(q):
    if isinstance(q.get('text'), str) and q.get('type') not in ('bank', 'info'):
        q['text'] = text(q['text'])
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
    if json.dumps(d, sort_keys=True) != before and '-n' not in sys.argv:
        with open(f, 'w') as fh:
            json.dump(d, fh, indent=1, ensure_ascii=False)
            fh.write('\n')
print(n)
