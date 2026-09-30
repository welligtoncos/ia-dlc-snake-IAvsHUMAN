"""Pygame loop: translate events, run session, execute commands, draw (D58)."""

from __future__ import annotations

import sys
from pathlib import Path

import pygame

from snake_vs_machine.agents.base import Agent
from snake_vs_machine.agents.human import HumanAgent
from snake_vs_machine.agents.registry import build_agent
from snake_vs_machine.agents.tree import ModelLoadError, TreeExplanation
from snake_vs_machine.core import engine
from snake_vs_machine.core.setup import new_match
from snake_vs_machine.core.state import CoreConfig, Outcome, Side, SnakeId, State
from snake_vs_machine.services.match import tick_with_results
from snake_vs_machine.ui.config import UiConfig, load, parse_args
from snake_vs_machine.ui.policies import PolicyId, spec_for
from snake_vs_machine.ui.pygame_keys import alias_for
from snake_vs_machine.ui.screens import paint
from snake_vs_machine.ui.session import (
    Command,
    ConfirmStart,
    Key,
    LoadFailed,
    LoadPolicies,
    MatchMode,
    MatchOver,
    PoliciesReady,
    PushAbsolute,
    QuitApp,
    RequestTick,
    Screen,
    SessionState,
    SetMode,
    SetPolicyB,
    TickDt,
    handle,
    new_session,
)


def _outcome_winner(state: State) -> str:
    result = engine.outcome(state)
    if result is Outcome.win_a:
        return "a"
    if result is Outcome.win_b:
        return "b"
    return "draw"


def _overlay_text(session: SessionState, match_state: State) -> str:
    winner = _outcome_winner(match_state)
    if session.mode is MatchMode.human_vs_ai:
        if winner == "a":
            return "vitória do jogador"
        if winner == "b":
            return "vitória da máquina"
        return "empate"
    from snake_vs_machine.ui.policies import label

    if winner == "draw":
        return "empate"
    name = label(session.policy_a if winner == "a" else session.policy_b)
    if session.policy_a == session.policy_b:
        side = "(NO)" if winner == "a" else "(SE)"
        return f"vitória do {name} {side}"
    return f"vitória do {name}"


def _load_agents(session: SessionState, models_dir: Path) -> tuple[Agent, Agent, HumanAgent | None]:
    if session.mode is MatchMode.human_vs_ai:
        human = HumanAgent()
        tree = build_agent(spec_for(session.policy_b, models_dir))
        return human, tree, human
    agent_a = build_agent(spec_for(session.policy_a, models_dir))
    agent_b = build_agent(spec_for(session.policy_b, models_dir))
    return agent_a, agent_b, None


def _execute(
    session: SessionState,
    commands: tuple[Command, ...],
    *,
    models_dir: Path,
    config: UiConfig,
    match_state: State | None,
    agent_a: Agent | None,
    agent_b: Agent | None,
    human: HumanAgent | None,
    explain: TreeExplanation | None,
) -> tuple[
    SessionState,
    State | None,
    Agent | None,
    Agent | None,
    HumanAgent | None,
    TreeExplanation | None,
    bool,
]:
    running = True
    for command in commands:
        if isinstance(command, QuitApp):
            running = False
        elif isinstance(command, PushAbsolute) and human is not None:
            human.push_absolute(command.direction)
        elif isinstance(command, LoadPolicies):
            try:
                agent_a, agent_b, human = _load_agents(session, models_dir)
                match_state = new_match(
                    CoreConfig(
                        width=config.width,
                        height=config.height,
                        obstacle_count=config.obstacle_count,
                    ),
                    session.match_seed,
                    {SnakeId.A: Side.NW, SnakeId.B: Side.SE},
                )
                explain = None
                session, extra = handle(session, PoliciesReady())
                session, match_state, agent_a, agent_b, human, explain, running = _execute(
                    session,
                    extra,
                    models_dir=models_dir,
                    config=config,
                    match_state=match_state,
                    agent_a=agent_a,
                    agent_b=agent_b,
                    human=human,
                    explain=explain,
                )
            except ModelLoadError as exc:
                print(f"{exc.reason}", file=sys.stderr)
                session, extra = handle(session, LoadFailed(exc.reason))
                session, match_state, agent_a, agent_b, human, explain, running = _execute(
                    session,
                    extra,
                    models_dir=models_dir,
                    config=config,
                    match_state=match_state,
                    agent_a=agent_a,
                    agent_b=agent_b,
                    human=human,
                    explain=explain,
                )
        elif isinstance(command, RequestTick) and match_state is not None and agent_a and agent_b:
            match_state, result_a, result_b = tick_with_results(match_state, agent_a, agent_b)
            payload = result_a.explanation or result_b.explanation
            if isinstance(payload, TreeExplanation):
                explain = payload
            if engine.is_terminal(match_state):
                session, extra = handle(session, MatchOver(_outcome_winner(match_state)))
                session, match_state, agent_a, agent_b, human, explain, running = _execute(
                    session,
                    extra,
                    models_dir=models_dir,
                    config=config,
                    match_state=match_state,
                    agent_a=agent_a,
                    agent_b=agent_b,
                    human=human,
                    explain=explain,
                )
    return session, match_state, agent_a, agent_b, human, explain, running


def _menu_event(key: int, session: SessionState) -> object | None:
    if key == pygame.K_RETURN:
        return ConfirmStart()
    if key == pygame.K_TAB:
        mode = (
            MatchMode.spectator
            if session.mode is MatchMode.human_vs_ai
            else MatchMode.human_vs_ai
        )
        return SetMode(mode)
    mapping = {pygame.K_1: PolicyId.easy, pygame.K_2: PolicyId.medium, pygame.K_3: PolicyId.hard}
    if key in mapping:
        return SetPolicyB(mapping[key])
    alias = alias_for(key)
    if alias is not None:
        return Key(alias)
    return None


def run(config: UiConfig) -> int:
    try:
        pygame.display.init()
        pygame.font.init()
        window_w = config.width * config.cell_px + config.hud_width
        window_h = config.height * config.cell_px
        screen = pygame.display.set_mode((window_w, window_h))
    except pygame.error as exc:
        print("Não foi possível abrir a janela.", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1

    pygame.display.set_caption("Snake vs. Máquina")
    clock = pygame.time.Clock()
    session = new_session(config.session_seed, config.tick_rate)
    match_state: State | None = None
    agent_a: Agent | None = None
    agent_b: Agent | None = None
    human: HumanAgent | None = None
    explain: TreeExplanation | None = None
    running = True

    while running:
        dt_ms = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                incoming: object | None
                if session.screen is Screen.menu:
                    incoming = _menu_event(event.key, session)
                else:
                    alias = alias_for(event.key)
                    incoming = Key(alias) if alias else None
                if incoming is not None:
                    session, commands = handle(session, incoming)  # type: ignore[arg-type]
                    session, match_state, agent_a, agent_b, human, explain, running = _execute(
                        session,
                        commands,
                        models_dir=config.models_dir,
                        config=config,
                        match_state=match_state,
                        agent_a=agent_a,
                        agent_b=agent_b,
                        human=human,
                        explain=explain,
                    )
        if session.screen is Screen.match:
            session, commands = handle(session, TickDt(dt_ms / 1000.0))
            session, match_state, agent_a, agent_b, human, explain, running = _execute(
                session,
                commands,
                models_dir=config.models_dir,
                config=config,
                match_state=match_state,
                agent_a=agent_a,
                agent_b=agent_b,
                human=human,
                explain=explain,
            )
        overlay = None
        if session.screen is Screen.end and match_state is not None:
            overlay = _overlay_text(session, match_state)
        paint(
            screen,
            session,
            match_state,
            explain,
            config.cell_px,
            config.hud_width,
            overlay,
        )
        pygame.display.flip()

    pygame.quit()
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    path = Path(args.config)
    warnings: list[str] = []
    config = load(path, warn=warnings.append)
    for message in warnings:
        print(message, file=sys.stderr)
    return run(config)
