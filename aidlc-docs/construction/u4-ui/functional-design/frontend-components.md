# U4 UI — Frontend Components

Pygame screens, not a web tree. "Props" are constructor arguments; "state" is what the screen holds between frames.

## Hierarchy

```text
App
├── MenuScreen
├── MatchScreen
│   ├── BoardView
│   ├── HudPanel
│   └── ExplanationStub
├── Error4Screen
└── EndOverlay   (drawn on top of MatchScreen)
```

## App

| | |
| --- | --- |
| Props | `UiConfig` |
| State | `screen`, `session_seed`, `match_index` |
| Loop | 60 FPS; dispatch events; `tick` policy of the active screen; blit |

Quit: window close or menu **Sair**.

## MenuScreen

| | |
| --- | --- |
| Props | — |
| State | `mode` (humano / espectador), `difficulty` or `policy_a`/`policy_b` |
| Actions | confirm → App starts a match; invalid tree load → `Error4Screen` |

## MatchScreen

| | |
| --- | --- |
| Props | `agents`, `HumanAgent` or `None`, `MatchSession` |
| State | `state`, `paused`, `panel_visible`, `last_explain`, accumulator |
| Events | BR-KEY-* ; does not handle Enter (end overlay does) |

Integrates `services.match.tick` only. No HTTP.

## BoardView

| | |
| --- | --- |
| Props | `state`, `cell_px`, origin |
| State | none |
| Draw | grid, obstacles, food, two snakes |

Must not mutate `state`.

## HudPanel

| | |
| --- | --- |
| Props | `state`, labels A/B, `max_ticks` |
| State | none |
| Draw | RF04 strings in Portuguese |

## ExplanationStub

| | |
| --- | --- |
| Props | `last_explain` or `None`, `visible` |
| State | none |
| Draw | Q7=B stub; empty hide if `visible` is false (rectangle still reserved) |

## Error4Screen

| | |
| --- | --- |
| Props | `reason`, (path only for stderr) |
| Events | any key → `MenuScreen` |

## EndOverlay

| | |
| --- | --- |
| Props | `MatchResult` facts from terminal `state`, mode, labels |
| Events | Enter rematch; Esc menu |

## Form validation

No free-text forms. Pickers are discrete `PolicyId` / difficulty values. `config.yaml` invalid fields fall back to defaults (no blocking dialog).
