# Services — Snake vs. Máquina

## MatchService (U3)
**Responsibilities**: `tick` avança **um** tick lógico (`act` + `engine.step`). Não conhece relógio.  
**Rhythm**: UI espera pelo `tick_rate` (exibição) e renderiza a 60 FPS; headless itera o mais rápido possível.  
**Created in**: U3. U4 e U5/U7 só consomem.

## ConfigService
Load/validate `config.yaml`. Round-trip PBT-02.

## TrainingPipeline
Collect, split congelado, fit 3/6/8, DAgger, JSON com **versão pinada do scikit-learn**, alerta D12 (100).

## TournamentService / StressService / UiApp
Como antes. UiApp **não** instancia a política de tick no engine; usa `MatchService`.
