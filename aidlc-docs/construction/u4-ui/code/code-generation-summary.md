# U4 UI — Code Generation Summary

**Unit**: `u4-ui`  
**Plan**: `aidlc-docs/construction/plans/u4-ui-code-generation-plan.md`  
**Decisions**: D53–D58

## Created

```
src/snake_vs_machine/ui/__init__.py
src/snake_vs_machine/ui/{config,keys,clock,policies,erro4,session,pygame_keys,screens,app}.py
src/snake_vs_machine/ui/render.py
src/snake_vs_machine/ui/fonts/{__init__.py,NotoSans-Regular.ttf,OFL.txt}
assets/fonts/{NotoSans-Regular.ttf,OFL.txt}
config.yaml
scripts/{jogo.py,ui_fps.py}
tests/ui/{__init__,test_keys,test_clock,test_config,test_policies,test_erro4,test_session,test_pygame_keys,test_smoke,test_ui_pbt}.py
```

## Modified

```
src/snake_vs_machine/core/rng.py          # D56 + ui_match_seed
src/snake_vs_machine/services/match.py    # public tick_with_results
tests/core/test_rng.py
tests/services/test_match.py
pyproject.toml                            # [ui] extra, coverage, mypy, package-data
```

## Quality

| Gate | Result |
| --- | --- |
| ruff | clean on U4 paths |
| mypy strict (`ui/` + rest) | clean; pygame 2.6.1 stubs used; `yaml` `ignore_missing_imports` |
| pytest default | **243 passed**, 2 deselected, **6m58s**, branch **86.16%** (`render.py` omitted) |
| FPS script | mean **60.78** (OK vs 55) |

## D56

`SeedSequence([5])` equals `SeedSequence([5, 0])` (**True**). Tags unique; `ui_match_seed` tag `6_000_003`.

## D57

`pygame==2.6.1`, `PyYAML==6.0.3`.

## Notes

- `app.py` is thin (D58) and not unit-tested beyond the dummy smoke; coverage overall still ≥ 80%.
- Session TDD tests were written in the same turn as `session.py` (implementation landed before the red run finished).
- Play: `pip install -e ".[ui]"` then `python scripts/jogo.py`.
