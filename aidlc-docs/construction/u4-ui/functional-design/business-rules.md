# U4 UI — Business Rules

## Loop and clock (Q8=A)

| ID | Rule |
| --- | --- |
| BR-CLK-1 | The display loop targets **60 FPS**. Simulation advances at `tick_rate` (default 10). |
| BR-CLK-2 | At most **one** `MatchService.tick` per frame. |
| BR-CLK-3 | The time accumulator is **capped at one tick period** (`1/tick_rate`). Late frames slow the match; they do **not** bank debt or skip ticks. |
| BR-CLK-4 | While `paused` is true, the accumulator does not run and `tick` is not called, except **N** (BR-KEY-4). |
| BR-CLK-5 | `MatchService` is never given a clock. Sleep / frame timing lives only in `ui`. |

## Keys (Q2=A, Q3=X)

| ID | Rule |
| --- | --- |
| BR-KEY-1 | Arrows **and** WASD map to the same four absolute `Direction` values (↑/W = N, →/D = E, ↓/S = S, ←/A = W). |
| BR-KEY-2 | In `human_vs_ai` and **not** paused: each mapped key calls `HumanAgent.push_absolute`. Spectator never pushes movement. |
| BR-KEY-3 | **Esc** on match or end-overlay → menu (match abandoned if still playing). |
| BR-KEY-4 | **P** toggles `paused`. While paused, **N** runs exactly one `tick`. Movement keys while paused are **ignored** (not pushed). |
| BR-KEY-5 | **R** during match (paused or not) starts a new match: same mode and policies, `match_index += 1`, new seed. |
| BR-KEY-6 | **H** toggles `panel_visible` on the match screen (RF05). |
| BR-KEY-7 | On the erro-4 screen, **any key** returns to the menu (Q5). |
| BR-KEY-8 | On the end overlay: **Enter** rematch (same mode, `match_index += 1`); **Esc** menu (Q6=B). |

## Menu and load (RF09, RF02, RF03)

| ID | Rule |
| --- | --- |
| BR-MEN-1 | Menu offers: humano vs. IA (picker Fácil/Médio/Difícil), espectador (two `PolicyId` pickers, same policy twice allowed), sair. |
| BR-MEN-2 | Starting a match that needs a tree calls `TreeAgent.from_joblib`. Failure → erro-4 screen, never a traceback on the HUD. |
| BR-MEN-3 | Technical detail (`reason`, path, exception text) is written to **stderr / console only** (Q5). |
| BR-MEN-4 | Human vs. IA: A = human NW, B = chosen tree SE. Spectator: A = policy A NW, B = policy B SE. |

## Erro 4 copy (Portuguese, D06)

Title always `Erro 4`. Body first line: `Nao foi possivel carregar o modelo da IA.` Then exactly one reason line:

| `reason` | Line |
| --- | --- |
| `missing` | `O arquivo do modelo nao foi encontrado.` |
| `sklearn` | `A versao do scikit-learn e incompatível com o modelo.` |
| `numpy` | `A versao do numpy e incompatível com o modelo.` |
| `schema` | `O esquema de features do modelo e incompatível.` |

(ASCII-safe in code; UI may use `ã`/`í` in the real strings — CG uses the same four `reason` keys.)

## HUD (RF04)

| ID | Rule |
| --- | --- |
| BR-HUD-1 | Every tick (and every paused frame) the HUD shows: names of A and B, lengths, ticks remaining (`max_ticks - tick`), alive/dead. |
| BR-HUD-2 | Human vs. IA names: `Jogador` and the difficulty label. Spectator names: the two policy labels. |
| BR-HUD-3 | All HUD strings are Portuguese. |

## Explanation stub (Q7=B)

| ID | Rule |
| --- | --- |
| BR-XPL-1 | The right-column strip is reserved even when hidden. **H** only hides/shows it. |
| BR-XPL-2 | When visible, U4 draws at most: `proposta`, `executada`, `vetado: sim` or `vetado: nao` from the last `TreeExplanation` of the tree snake. No `path`, no English feature names. |
| BR-XPL-3 | If the last tree result is missing (both sides random/expert), the stub shows `sem explicacao`. |
| BR-XPL-4 | U7 replaces this stub; it must not require a different rectangle. |

## End overlay (Q6=B)

| ID | Rule |
| --- | --- |
| BR-END-1 | Human vs. IA outcome: `vitoria do jogador` / `vitoria da maquina` / `empate`. |
| BR-END-2 | Spectator outcome: `vitoria do {label}` using the winning policy label; if both labels are equal, append the side `(NO)` / `(SE)`. Empate: `empate`. |
| BR-END-3 | Overlay also shows `end_reason` in PT (`morte` / `tempo esgotado`) and both lengths. |
| BR-END-4 | The board under the overlay is the terminal state (not cleared). |

## Rendering

| ID | Rule |
| --- | --- |
| BR-REN-1 | Drawing **must not** mutate `State` (P-COPY / P-UI-FROZEN). |
| BR-REN-2 | Cells are squares of `cell_px`. Origin of the board pane is top-left = cell `(0,0)`. |
| BR-REN-3 | A and B use distinct solid colours; food and obstacles are distinct from both. No sprites required. |

## Seeds

| ID | Rule |
| --- | --- |
| BR-SED-1 | Match seeds come only from `core/rng.py` (`ui_match_seed(session_seed, match_index)`, tag `6_000_003`). No `time.time()` as a seed. |
| BR-SED-2 | First match of a session uses `match_index = 0`. **R** and rematch increment the index. |
| BR-SED-3 | If `session_seed` is **absent** from config, the session draws `secrets.randbits(31)` once and prints it on stderr (D55). An explicit `0` is a real seed. |

## Layering

| ID | Rule |
| --- | --- |
| BR-LAY-1 | `ui` does not import `training` or `evaluation`. |
| BR-LAY-2 | pygame stays inside `ui/` and `scripts/jogo.py`. |
