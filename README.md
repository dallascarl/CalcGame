# CalcGame

A practice game for Calculus 1. Students walk a map, and each stop has a lesson and drills. Points come from a minigame that students earn by answering questions.

## Where things live

| File | What it is |
| --- | --- |
| `worlds.json` | The list of world map files, in order |
| `maps/*.json` | One map per world: every stop, where it sits, what it requires, and which deck it opens |
| `decks/*.json` | One file per stop: its graphs, lesson steps, and drill questions |
| `js/app.js` | The game engine. Does not change when content changes |
| `js/items.js` | More item types (formulas, intervals, multi-part problems, sketching, explorers) |
| `js/config.js` | Server settings (Supabase URL and public key). Empty = no accounts |
| `js/backend.js`, `js/account.js`, `js/avatars.js` | Accounts, syncing, feedback, leaderboard, codes, and the 21 characters |
| `instructor.html`, `js/instructor.js` | The instructor page (desktop) |
| `supabase/schema.sql`, `supabase/SETUP.md` | The database and how to turn accounts on |
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

A stop is cleared when every drill at it is **passed** (see Game rules). Lessons are recommended but never lock anything.

### Deck files

A deck has `id` (must match the file name), `title`, `graphs`, an optional `lesson`, and `drills`.

For a stop with more than one lesson, use `lessons` instead of `lesson`: a list of `{"id", "title", "slides"}`. The stop shows them as Lesson 1, Lesson 2, … with each title underneath. Everything is open from the start; the stop panel suggests an order ("best after Lesson 1"). See `decks/maxmin.json`.

Text markup: `$...$` is math, `\\$` is a plain dollar sign (money), `lim[x->2^-]` draws a limit, `**bold**`, and `\n` starts a new line. Inside math, `x_0` or `x_(n-1)` is a subscript and `frac{top}{bottom}` is a stacked fraction. In a word bank (`bank`), `frac{___}{___}` in the plain text puts blanks in a stacked fraction.

Students can type answers as decimals or as fractions (the fraction key), so `7/4` and `1.75` are both accepted. A fraction is drawn stacked while it is typed.

**Multiple choice is shuffled.** Write the right answer anywhere (first is fine). Students see the choices in random order, except: `"fixed": true` keeps the order; single-letter choices (A, B, C) and the "Both / max only / min only / Neither" family keep their order; choices like "Does not exist", "None of these", "Neither" stay last; and lists of plain numbers are shown smallest first.

Item types: `info`, `explore`, `extrema`, `newton`, `bisect`, `mvt`, `linear`, `diff`, `optim`, `rr`, `curvex` and `ratio` (lesson only), `graph`, `mc`, `tf`, `bank`, `num`, `crit`, `multi`, `match`, `pick`, `expr`, `interval`, `order`, `steps`, `sketch`, `tap`. See the files in `decks/` for examples.

- `tap`: the student taps a spot on a graph (for example, roughly where the root is). Needs `graph`, `answers` (the x-values that count) and `tol` (how close, default 0.15); optional `howto`. The deck test checks that the graph crosses the x-axis at each answer; set `"root": false` when the spot is not a root (e.g. where a tangent line crosses).

- `num`: the student types one number. Needs `answer`, an optional `label` for the box, and an optional `tol` (default 0.01).
- `crit`: the student builds a list of x-values (used for critical points). Needs `answers`, a list of numbers; an empty list means "there are no critical numbers" and the student has a button for that.
- `multi`: several answer boxes sharing one number pad, e.g. $f(x_0)$, $f'(x_0)$ and $x_1$. With a Newton `verify`, a picture of the curve and the tangent lines appears after the answer is checked (`"picture": false` turns it off). Needs `parts`, a list of `{"label", "answer", "tol"}` (tol defaults to 0.001). `"fail": true` adds a "Newton's method breaks down here" button; set `"fails": true` when that button is the right answer (then the part answers are not needed).
- `newton`: the tangent-line explorer. The student drags to choose $x_0$, sees where the tangent hits the axis, then steps to $x_1, x_2, …$ with zoom. The table shows $x_n$, $f(x_n)$ and $f'(x_n)$. Needs `fn` and `window`; optional `dfn` (derivative), `range` for the slider, `start`, `pick: false` to start at `start` with no slider, `tol` (default 0.0005: done when a step moves less than this), and `after`, where `{x}` is the root and `{n}` the number of steps. `"slow": true` does it one piece at a time: choose $x_0$ (no tangent shown yet), tap **Draw the tangent line**, then tap where it crosses the axis (the first `tapSteps` steps, default 2; after that a button slides down for them).
- `bisect`: the bisection game. Needs `fn`, `a`, `b` (opposite signs) and `goal` (stop when the interval is narrower than this); optional `window` and `after` (`{n}`, `{a}`, `{b}`).
- `match`: tap-to-match cards. `pairs` is a list of `["left", "right"]`; the right column is shuffled. Keep it to 6 pairs or fewer.
- `pick`: select all that apply. `options` and `answers` (a list of positions, 0 is the first).
- `crit` also takes `var` (e.g. `"c"`), `label`, and `noneText` for the "none" button, so it works for any list of x-values.
- `mvt`: drag a point until the tangent is parallel to the secant (Rolle's Theorem when the ends are level). Needs `fn`, `a`, `b`, `window` and `cs`, every c-value to find; optional `secLabel`, `start`, `found`, `after` (`{c}`). The deck test checks each c and looks for any you missed.
- `linear`: the linearization explorer for `fn` at `a`. `goal: "zoom"` (zoom in until the curve looks like its tangent; `zoomGoal`, default 16), `"target"` (drag x to `target` and compare f and L), or `"far"` (drag until the error passes `err`, then `recenter: true` lets them make a new linearization).
- `diff`: differentials for `fn` at `a`. The student first picks which segment is dy, then drags dx toward 0 until dy and Δy agree within `agree`.
- `extrema`: the walk-through widget. The student finds the critical numbers, then the app lays out every candidate with its value and the student taps the largest and the smallest. Needs `fn` (`{"expr": ..., "domain": [a, b]}`) and `crit`, the list of critical numbers.

Graph questions also take `ask: "absmax" | "absmin" | "argmax" | "argmin"`. The answer is a number, or `"NONE"` when no such point exists. Graphs can take `arrow: "L"`, `"R"` or `"LR"` on a piece to draw an arrowhead, `vlines` for dashed vertical lines, and `xstep`/`ystep` to set the tick spacing.

**The deck test checks your answer keys against the real functions.** For a `num` question add `verify: {"expr": ..., "domain": [a, b], "ask": "max"|"min"|"argmax"|"argmin"}` and it recomputes the answer. For a `crit` question add `verify: {"expr": ..., "range": [a, b], "dexpr": "the derivative"}` and it scans for critical numbers and checks your derivative formula. `extrema` items are always checked this way. For a Newton `multi` question add `verify: {"expr": ..., "x0": ...}` and give each part a `calc` such as `"x1"`, `"x2"`, `"f(x0)"` or `"f'(x1)"`; the test runs Newton's method and compares, and also checks that `fails` is set exactly when $f'(x_0)$ = 0.

Graphs: `window` is `[xmin, xmax, ymin, ymax]`. Each piece has `expr`, `from`, `to`. Write multiplication out (`2*x`, not `2x`). `holes` are open circles and `dots` are filled points. `tangents` is a list of x-values where the tangent line is drawn, and `labels` is a list of `[x, y, "text"]` (add `"big"` as a fourth entry for a large, bold label).

### Stop options (added for World 3)

- `"lessonOptional": true` on a deck: the lesson is marked Optional (used by the review side quests).
- A drill with `"after": "<lesson id>"` is listed right under that lesson.
- A lesson with `"needs": ["<drill kind>"]` shows "best after …" until those drills are passed. (Nothing locks; L'Hôpital uses this to suggest doing the 0/0 and ∞/∞ drill before Lesson 3.)
- `"stages"` on a drill runs it in parts, in order: a list of `{"id", "title", "oneOf"}`, and each question gets `"stage": "<id>"`. Three right in a row skips the rest of that part. `oneOf` (question ids) puts one of them among the first three of that part, e.g. a "Newton's method breaks down" case. Finishing all the parts passes the drill. See the Calculation drill in `decks/newton.json`.
- `"setSize": n` on a drill sets how many questions are in a set (default 8). Long multi-part drills use 2 to 4.
- `"exam": true` on a drill runs it as a practice test: no feedback until the end, then a score, a time, a score for each `topic`, and a review of every miss. Give questions a `"topic"` to get the breakdown (any drill shows it).

### More item types (js/items.js)

- `expr`: the student types a formula on a math keypad. `answer` (one string, or a list of acceptable ones) is checked by plugging random numbers into both, so any equivalent form is right. `vars` lists the variable keys (e.g. `["r", "h", "r'", "h'"]`; a prime means d/dt). `keys` adds keys such as `"pi"`, `"sqrt("`, `"sin("`, `"ln("`, `"e^("`, `"sec("`. `show` is how the answer is displayed after a miss. The deck test checks that the answer can be typed with the keys given.
- `interval`: interval notation with ( [ ] ) , ∞ ∪ keys. `answer` like `"(-inf,2)U(2,inf)"` (or a list of acceptable answers); `"none"` with a `noneText` button for "never". Endpoints may be decimals (within 0.01) or fractions.
- `order`: tap `items` into the right order (write them in the correct order; the app shuffles).
- `steps`: a word problem done one part at a time. `text` (and an optional `figure`, an inline SVG) stays at the top; `steps` is a list of ordinary items (mc, num, expr, interval, crit, sketch, …). In lessons a wrong part gets its `hint` and a second try, then the answer; in drills a wrong part shows the answer and the problem continues. The question counts as right only if every part was right the first time.
- `sketch`: the graph-sketching experience. `fn`, `window`, and `data` with `points` (`[x, y, "label"]`), `crit`, `infl`, `va`, `ha`, optional `slant`, and `lines` (the data shown to the student). Phases: place the points and asymptotes on the grid, mark each region ↗/↘ and ∪/∩ on a sign chart, then draw with a finger or mouse. The drawing is graded on key points, coverage, rising/falling, concavity and asymptote behavior, and the real graph is shown afterward. `"phases": ["draw"]` with `"prefill": true` skips straight to drawing with the data already placed.
- Explorers (lessons only): `optim` (drag $x$ and watch a scene and the quantity being optimized; `scene` type `rect` or `box`), `rr` (related-rates scenes `ladder`, `ripple`, `balloon`, `cone` with a time slider and live rates), `curvex` (slide along a curve; the tangent shows rising/falling, or the curve is colored by concavity), `ratio` (tap closer and closer to a limit and watch the two parts of an indeterminate form fight; `op` is `/`, `*`, `-` or `^`).

## Calculator

Every lesson and drill has a **Calc** button with a scientific calculator (RAD/DEG). After =, its **Use ↓** button puts the result in the answer box. To hide it for a deck, add `"calculator": false` to the deck.

## Game rules

- **Nothing at a stop is locked.** Students can open any lesson or drill. Lessons and drill sets remember where the student is, so leaving by accident picks up at the same step or question. ‹ and › move back and forward (in a drill, › on an unanswered question skips it to the end; it breaks the in-a-row count).
- **Passing a drill** (this is what clears a stop): 3 right in a row in a set (the set can end right there), or 80% on a finished set. Staged drills and practice tests pass when finished.
- **Mastering a drill** (★): 8 of the last 10 answers in that drill right.
- Finishing a lesson earns a game play the first time every step in it has been done (skipping ahead is allowed but does not earn the play).

The numbers are in the `RULES` line near the top of `js/app.js`: streak length, questions per set, the pass and mastery rules (`passRun`, `passPct`, `masterWin`, `masterPct`), plays per day, and minigame scoring.

## Answer key (instructor)

Tap a stop on the map, then **Answer key** under its buttons: every lesson step and drill question with its answer, graphs included, the right choice marked ✓. Wider on a computer (two columns).

## Accounts and the instructor page

See `supabase/SETUP.md`. Students sign up with a class code, a made-up username and a password, then pick a character. Progress syncs between devices; answers, finished lessons and drill sets, and cleared stops are logged for the instructor page, along with Feedback and "I don't understand" messages (which need at least 6 + 12 words). Cleared stops give a one-time completion code for Canvas. Open either page with `?mock=1` to try everything with a pretend server in your browser.

## Updates and browser caching

`index.html` and `instructor.html` load each script and stylesheet with `?v=<date>`. Change that number when you change a `.js` or `.css` file, or phones may keep the old copy for up to 10 minutes. (Deck and map JSON files are always fetched fresh.)

## Running it

GitHub Pages serves the site from the `main` branch. Opening `index.html` straight from a folder will not work, because the browser blocks it from reading the JSON files. To test on your computer, run `python3 -m http.server` in this folder and open `http://localhost:8000`.
