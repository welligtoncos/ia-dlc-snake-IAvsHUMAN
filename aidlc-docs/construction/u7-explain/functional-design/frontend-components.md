# U7 Explain — Frontend (RF05 only)

Pygame already owns the rectangle (U4). U7 only changes **what is painted**.

## ExplanationStub (replaces U4 stub)

| | |
| --- | --- |
| Props | `TreeExplanation \| None`, `visible` |
| State | none |
| Draw | If hidden, reserved empty rect. If visible and no explanation: `sem explicação`. Else: veto lines + `explain_text.lines(explanation)` |

No pygame import in `explain_text.py` or `labels_pt.py`.

## Integration

`render.py` calls `explain_text.lines` and blits with the existing text cache (D55). Same `hud_width` strip. **H** unchanged.

## Form validation

None. Labels are a closed dictionary, not user input.
