from blip.arch import Arch
from amaranth.build import Platform
from amaranth.lib.io import Pin
from abc import ABC, abstractmethod

_boards: map[str, "Board"] = { }

def board_definition(func):
    _boards[func.__name__] = func

class Board(ABC):
    name: str
    arch: Arch
    platform: Platform

    @abstractmethod
    def get_led(self, index: int) -> Pin:
        ...

