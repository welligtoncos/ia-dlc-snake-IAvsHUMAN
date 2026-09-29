# AI-DLC State Tracking

## Project Information
- **Project Name**: Snake vs. Máquina (IA com Árvore de Decisão)
- **Project Type**: Greenfield
- **Start Date**: 2026-09-28T22:20:00Z
- **Current Stage**: CONSTRUCTION - U1 closed (`u1-done`); next is U2 Functional Design
- **Intent Source**: `PRD/PRD — Snake vs. Máquina (IA com Árvore de Decisão) · AI-DLC.md`
- **Approved through**: D37 (U1 Code Generation approved; Python >= 3.13)

## Execution Plan Summary
- **Total Stages (remaining inception)**: none (Inception closed)
- **Stages to Execute (construction)**: Functional Design (all units, starting U1); NFR Requirements/Design for U1–U4 only; Code Generation; Build and Test
- **Stages to Skip**: User Stories, Reverse Engineering, Infrastructure Design, NFR on U5/U7, Operations placeholder
- **Unit order**: U1 → U2 → U3 → U5 → U4 → U7

## Workspace State
- **Existing Code**: Yes (`src/snake_vs_machine/core/`)
- **Programming Languages**: Python 3.13 (D37)
- **Build System**: `pyproject.toml` (`pip install -e ".[dev]"`)
- **Project Structure**: U1 core library + tests; later units pending
- **Reverse Engineering Needed**: No
- **Workspace Root**: `d:\projetos-ia-aws\ia-dlc-snake-IAvsHUMAN`

## Code Location Rules
- **Application Code**: Workspace root (NEVER in aidlc-docs/)
- **Documentation**: aidlc-docs/ only
- **Structure patterns**: See code-generation.md Critical Rules

## Extension Configuration
| Extension | Enabled | Decided At |
|---|---|---|
| Security Baseline | No | Requirements Analysis |
| Resiliency Baseline | No | Requirements Analysis |
| Property-Based Testing | Partial (PBT-02, PBT-03, PBT-07, PBT-08, PBT-09 blocking; remaining advisory) | Requirements Analysis |

## Stage Progress
### 🔵 INCEPTION PHASE
- [x] Workspace Detection
- [x] Reverse Engineering (skipped — greenfield)
- [x] Requirements Analysis (approved 2026-09-28, D01–D29)
- [x] User Stories (skipped — user: Application Design / Units Generation)
- [x] Workflow Planning (approved D27)
- [x] Application Design (approved D29)
- [x] Units Generation (approved D30 — Inception closed)

### 🟢 CONSTRUCTION PHASE
- [ ] Per-Unit Loop
  - [x] U1 Functional Design (approved D33)
  - [x] U1 NFR Requirements (approved D34)
  - [x] U1 NFR Design (approved D35)
  - [x] U1 Code Generation (approved; tag `u1-done`)
  - [ ] U2 Functional Design (next)
- [ ] Build and Test

### 🟡 OPERATIONS PHASE
- [ ] Operations (placeholder)
