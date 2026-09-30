# U4 UI — Domain Entities

Technology-agnostic except where a type is already fixed (`State`, `Direction`, `MatchService`, `ModelLoadError`). Pygame types stay out of this document; they appear in NFR Design / Code Generation.

## Package layout

```text
src/snake_vs_machine/
├── core/          # consumed
├── agents/        # HumanAgent, registry, TreeAgent
├── services/      # MatchService.tick
├── ui/            # this unit
│   ├── app.py     # screen stack + 60 FPS loop
│   ├── config.py  # load config.yaml
│   ├── screens.py # menu, match, error, end
│   ├── render.py  # board, HUD, explanation stub
│   └── keys.py    # keycode → Direction
├── training/      # must not be imported
└── evaluation/    # must not be imported
config.yaml        # workspace root (RF10)
scripts/jogo.py    # entry: python scripts/jogo.py
```

`ui` depends on `core`, `agents`, `services`. It does not import `training` or `evaluation`.

## UiConfig

Loaded from `config.yaml` with documented defaults if the file is missing or a field is invalid (scenario 5: log warning, keep defaults).

| Field | Default | Meaning |
| --- | --- | --- |
| `width` / `height` | 20 / 20 | Board cells; passed to `CoreConfig` |
| `tick_rate` | 10 | Simulation ticks per wall-clock second |
| `cell_px` | 24 | Pixel size of one board cell (Q10=B) |
| `hud_width` | 280 | Right column width in pixels |
| `obstacle_count` | 0 | Passed to `CoreConfig` |
| `panel_key` | `H` | Toggle explanation strip (RF05) |
| `session_seed` | optional | If the key is **absent**, `secrets.randbits(31)` at session start (stderr). If **present**, that int (D55) |
| `models_dir` | `models` | Directory of `.joblib` files, resolved vs the config file's parent (D55) |

Window size is **derived**, not user-resizable (Q10=B):

`window_w = width * cell_px + hud_width`  
`window_h = height * cell_px`

Default: 480 + 280 = **760 × 480**.

## ScreenId

`menu` | `match` | `error4` | `end`

The app holds exactly one current screen. `end` is an overlay on the last match frame (Q6=B).

## MatchMode

| Mode | Agent A (NW) | Agent B (SE) |
| --- | --- | --- |
| `human_vs_ai` | `HumanAgent` | tree of the chosen difficulty |
| `spectator` | policy A | policy B |

## PolicyId

Menu labels in Portuguese; specs in English.

| Id | Label | `AgentSpec` |
| --- | --- | --- |
| `random` | Aleatório | `("random", {})` |
| `expert` | Especialista | `("expert", {})` |
| `easy` | Fácil | `("tree", {path: bc_depth3, safety_mask: false})` |
| `medium` | Médio | `("tree", {path: bc_depth6, safety_mask: false})` |
| `hard` | Difícil | `("tree", {path: bc_depth8, safety_mask: true})` |

## MatchSession

| Field | Meaning |
| --- | --- |
| `mode` | `human_vs_ai` or `spectator` |
| `policy_a` / `policy_b` | `PolicyId` (human mode: A is implicit human, B is the difficulty) |
| `seed` | From `ui_match_seed(session_seed, match_index)` |
| `state` | Current `State` |
| `paused` | Tick clock stopped; frames still draw (Q3) |
| `panel_visible` | Default **true**; **H** toggles |
| `last_explain` | Last `TreeExplanation` from the tree side, or `None` |
| `match_index` | Increments on rematch / **R** |

## Erro4View

| Field | Meaning |
| --- | --- |
| `reason` | `missing` / `sklearn` / `numpy` / `schema` |
| `path` | Joblib path that failed (stderr only, Q5) |

## Layout (Q1=A)

```text
[ board | HUD stacked over explanation stub ]
 left     right column, same height as the board
```

Board occupies the left square of `width * cell_px`. The right column (`hud_width`) stacks the HUD above the reserved RF05 strip.

## Out of this unit

U7 replaces the stub with the Portuguese path (max 3 conditions). `TimedAgent` stays U7. pygame pin is a Code Generation decision (Q9=A).
