"""World 0 (The Toolkit): the review world for the first six class days.
   python3 tools/gen/world0.py            writes every World 0 deck and the formula manifest
   python3 tools/gen/world0.py t-factor   writes just that deck (the manifest is then partial: run it all before verify.js)
The decks are a starting point. Once one is hand-edited, do not regenerate it."""
import sys
from lib import write_manifest
import world0a

DECKS = {'t-notation': world0a.deck_notation, 't-domain': world0a.deck_domain, 't-factor': world0a.deck_factor, 't-rational': world0a.deck_rational}
try:
    import world0b
    DECKS.update(world0b.DECKS)
except ImportError:
    pass
try:
    import world0c
    DECKS.update(world0c.DECKS)
except ImportError:
    pass

if __name__ == '__main__':
    want = sys.argv[1:] or list(DECKS)
    for k in want:
        DECKS[k]()
        print('wrote', k)
    if not sys.argv[1:]:
        write_manifest('world0')
