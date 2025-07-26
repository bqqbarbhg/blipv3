from . import Board, board_definition
from amaranth.build import Platform
from blip.arch.ecp5 import Ecp5Arch

class Ulx3sBoard(Board):
    def __init__(self, platform: Platform):
        self.arch = Ecp5Arch()
        self.platform = platform

    def get_led(self, index: int):
        assert 0 <= index < 8
        self.platform.request(f"led{index}")

@board_definition
def ulx3s_85f():
    from amaranth_boards.ulx3s import ULX3S_85F_Platform
    return Ulx3sBoard(ULX3S_85F_Platform)
