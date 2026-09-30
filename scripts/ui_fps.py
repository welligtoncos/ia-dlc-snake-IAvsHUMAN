"""Measure mean/min FPS over 600 frames, spectator hard vs hard (D55)."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pygame

from snake_vs_machine.ui.app import _execute
from snake_vs_machine.ui.config import load
from snake_vs_machine.ui.policies import PolicyId
from snake_vs_machine.ui.screens import paint
from snake_vs_machine.ui.session import (
    ConfirmStart,
    MatchMode,
    Screen,
    TickDt,
    handle,
    new_session,
)


def main() -> int:
    config = load(Path("config.yaml"), bits=lambda n: 1)
    try:
        pygame.display.init()
        pygame.font.init()
        window_w = config.width * config.cell_px + config.hud_width
        window_h = config.height * config.cell_px
        screen = pygame.display.set_mode((window_w, window_h))
    except pygame.error as exc:
        print("Não foi possível abrir a janela.")
        print(str(exc))
        return 1

    session = replace(
        new_session(1, config.tick_rate),
        mode=MatchMode.spectator,
        policy_a=PolicyId.hard,
        policy_b=PolicyId.hard,
        panel_visible=True,
    )
    session, commands = handle(session, ConfirmStart())
    match_state = None
    agent_a = agent_b = human = explain = None
    session, match_state, agent_a, agent_b, human, explain, _ = _execute(
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
    clock = pygame.time.Clock()
    frames = 600
    dts: list[float] = []
    for _ in range(frames):
        dt = clock.tick(60)
        dts.append(dt)
        if session.screen is Screen.match:
            session, commands = handle(session, TickDt(dt / 1000.0))
            session, match_state, agent_a, agent_b, human, explain, _ = _execute(
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
        paint(
            screen,
            session,
            match_state,
            explain,
            config.cell_px,
            config.hud_width,
            None,
        )
        pygame.display.flip()
    pygame.quit()
    fps = [1000.0 / d if d else 0.0 for d in dts]
    mean = sum(fps) / len(fps)
    print(f"mean_fps={mean:.2f} min_fps={min(fps):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
