# CalcGame

A practice game for Calculus 1. Students walk a map, and each stop has a lesson and drills. Points come from a minigame that students earn by answering questions.

## Where things live

| File | What it is |
| --- | --- |
| `worlds.json` | The list of world map files, in order |
| `maps/*.json` | One map per world: every stop, where it sits, what it requires, and which deck it opens |
| `decks/*.json` | One file per stop: its graphs, lesson steps, and drill questions |
| `js/app.js` | The game engine. Does not change when content changes |
| `css/app.css` | The look |
| `index.html` | The page that loads everything |

## Editing content

Edit the JSON files directly on GitHub (pencil icon) or on your computer. After a change, open the game, tap **Instructor: deck test** at the bottom of the map, and check for errors.

### maps/*.json

Add a new world by creating a map file in `maps/` and listing it in `worlds.json`. Each map has `id`, `world` (its number), `title`, `short` (tab name), `height`, optional `regions`, and `nodes`.

Each stop:

```json
{ "id": "limits", "kind": "main", "title": "Limits", "x": 50, "y": 12,
  "deck": "limits-intro", "requires": ["start"], "blurb": "One line shown under the title." }
```

- `kind`: `start`, `main` (numbered level), `review` (side quest), `extra` (optional side quest), or `boss`.
- `x` runs 0 to 100 across the screen. `y` runs 0 to `height` down the map.
- `deck`: the file name in `decks/` without `.json`, or `null` for a stop that is not built yet (shown as Coming soon).
- `requires`: stops that must be cleared first. A road is drawn from each one.
- `from` (optional): draw the road from these stops instead, without changing what is required.
- `label` (optional): a shorter name to show on the map.

A stop is cleared when its lesson is finished and one set of each drill has been completed.

### Deck files

A deck has `id` (must match the file name), `title`, `graphs`, an optional `lesson`, and `drills`.

Text markup: `$...$` is math, `lim[x->2^-]` draws a limit, `**bold**`, and `\n` starts a new line.

Item types: `info`, `explore` and `extrema` (lesson only), `graph`, `mc`, `tf`, `bank`, `num`, `crit`. See `decks/limits-intro.json` and `decks/maxmin.json` for examples.

- `num`: the student types one number. Needs `answer`, an optional `label` for the box, and an optional `tol` (default 0.01).
- `crit`: the student builds a list of x-values (used for critical points). Needs `answers`, a list of numbers; an empty list means "there are no critical numbers" and the student has a button for that.
- `extrema`: the walk-through widget. The student finds the critical numbers, then the app lays out every candidate with its value and the student taps the largest and the smallest. Needs `fn` (`{"expr": ..., "domain": [a, b]}`) and `crit`, the list of critical numbers.

Graph questions also take `ask: "absmax" | "absmin" | "argmax" | "argmin"`. The answer is a number, or `"NONE"` when no such point exists. Graphs can take `arrow: "L"`, `"R"` or `"LR"` on a piece to draw an arrowhead, `vlines` for dashed vertical lines, and `xstep`/`ystep` to set the tick spacing.

**The deck test checks your answer keys against the real functions.** For a `num` question add `verify: {"expr": ..., "domain": [a, b], "ask": "max"|"min"|"argmax"|"argmin"}` and it recomputes the answer. For a `crit` question add `verify: {"expr": ..., "range": [a, b], "dexpr": "the derivative"}` and it scans for critical numbers and checks your derivative formula. `extrema` items are always checked this way.

Graphs: `window` is `[xmin, xmax, ymin, ymax]`. Each piece has `expr`, `from`, `to`. Write multiplication out (`2*x`, not `2x`). `holes` are open circles and `dots` are filled points.

## Game rules

The numbers are in the `RULES` line near the top of `js/app.js`: streak length, questions per set, how many correct answers count as mastered, plays per day, and minigame scoring.

## Running it

GitHub Pages serves the site from the `main` branch. Opening `index.html` straight from a folder will not work, because the browser blocks it from reading the JSON files. To test on your computer, run `python3 -m http.server` in this folder and open `http://localhost:8000`.
