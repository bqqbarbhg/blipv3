from . import Board, board_definition
from amaranth.build import Platform
from blip.arch.ecp5 import Ecp5Arch
from blip.component import BoardSpec

class Ulx3sBoard(Board):
    def __init__(self, platform: Platform, spec: BoardSpec):
        self.arch = Ecp5Arch()
        self.platform = platform
        self.spec = spec

    def get_led(self, index: int):
        assert 0 <= index < 8
        return self.platform.request("led", index)

@board_definition("ulx3s_85f")
def ulx3s_85f(spec: BoardSpec):
    from amaranth_boards.ulx3s import ULX3S_85F_Platform
    return Ulx3sBoard(ULX3S_85F_Platform(), spec)
