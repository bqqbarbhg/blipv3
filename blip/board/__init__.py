from blip.arch import Arch
from amaranth.build import Platform
from amaranth.lib.io import Pin
from amaranth.sim import Simulator
from abc import ABC, abstractmethod
from typing import Optional
from blip.component import ComponentSpec, BoardSpec
import os

_boards: dict[str, "Board"] = { }

def board_definition(name):
    def decorator(func):
        _boards[name] = func
        return func
    return decorator

def search_board(name: str):
    filename = name
    if not filename.lower().endswith(".toml"):
        filename = f"{filename}.toml"

    self_path = os.path.dirname(__file__)
    specs_path = os.path.join(self_path, "..", "specs")
    specs_path = os.path.normpath(specs_path)
    boards_path = os.path.join(specs_path, "board")

    for root, dirs, files in os.walk(boards_path):
        for file in files:
            if file == filename:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, specs_path)
                yield rel_path.replace("\\", "/")

def resolve_board_path(name: str):
    if "/" in name:
        return name
    else:
        boards = list(search_board(name))
        assert boards, f"no board found for name '{name}'"
        assert len(boards) <= 1, f"found conflicting boards: {", ".join(boards)}"
        return boards[0]

class Board(ABC):
    arch: Arch
    spec: BoardSpec
    platform: Optional[type]

    @abstractmethod
    def get_led(self, index: int) -> Pin:
        ...

    def create(spec: BoardSpec, *, sim=False) -> "Board":
        if sim:
            from blip.board.sim import sim_board
            return sim_board(spec)
        else:
            board_fn = _boards[spec.board]
            return board_fn(spec)

    def load(path: str, *, sim=False) -> "Board":
        spec = ComponentSpec.load(resolve_board_path(path))
        assert isinstance(spec, BoardSpec)
        return Board.create(spec, sim=sim)

    def simulate(self, m, *, engine="pysim") -> Simulator:
        sim = Simulator(m, engine=engine)
        self.arch.setup_simulator(sim)
        return sim

import blip.board.ulx3s
