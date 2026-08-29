from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Tuple


@dataclass
class TargetPig:
    x: float
    y: float
    radius: float = 22.0
    hp: int = 100
    points: int = 5000


@dataclass
class PhysicsBlock:
    x: float
    y: float
    width: float
    height: float
    material: str = "wood"  # wood, ice, stone
    durability: float = 100.0


@dataclass
class GameLevelData:
    level_id: int
    name: str
    pigs: List[TargetPig] = field(default_factory=list)
    blocks: List[PhysicsBlock] = field(default_factory=list)
    par_score: int = 15000


class CustomLevelGenerator:
    """
    Original custom level generator for VisionBird.
    Generates procedural structures, pig targets, and score mechanics.
    """

    @staticmethod
    def generate_level(level_id: int) -> GameLevelData:
        if level_id == 0:
            return GameLevelData(
                level_id=0,
                name="Training Grounds",
                pigs=[
                    TargetPig(950.0, 480.0, hp=100),
                    TargetPig(1010.0, 480.0, hp=100),
                ],
                blocks=[
                    PhysicsBlock(920.0, 500.0, 20.0, 85.0, material="wood"),
                    PhysicsBlock(980.0, 500.0, 20.0, 85.0, material="wood"),
                    PhysicsBlock(950.0, 440.0, 100.0, 20.0, material="stone"),
                ],
                par_score=10000,
            )
        elif level_id == 1:
            return GameLevelData(
                level_id=1,
                name="Fortress Assault",
                pigs=[
                    TargetPig(900.0, 480.0, hp=100),
                    TargetPig(980.0, 480.0, hp=100),
                    TargetPig(940.0, 390.0, hp=120),
                ],
                blocks=[
                    PhysicsBlock(880.0, 510.0, 20.0, 100.0, material="stone"),
                    PhysicsBlock(960.0, 510.0, 20.0, 100.0, material="stone"),
                    PhysicsBlock(920.0, 420.0, 120.0, 20.0, material="wood"),
                ],
                par_score=20000,
            )
        else:
            # Procedural level generation for higher levels
            pigs = [
                TargetPig(880.0 + i * 60.0, 480.0, hp=100 + level_id * 10)
                for i in range(min(4, level_id + 1))
            ]
            blocks = [
                PhysicsBlock(850.0 + i * 50.0, 500.0, 20.0, 90.0, material="ice")
                for i in range(min(5, level_id + 2))
            ]
            return GameLevelData(
                level_id=level_id,
                name=f"Procedural Challenge {level_id}",
                pigs=pigs,
                blocks=blocks,
                par_score=15000 + level_id * 5000,
            )
