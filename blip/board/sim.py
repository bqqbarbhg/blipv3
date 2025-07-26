from amaranth.build import Platform
from amaranth.sim import Simulator
from amaranth.lib.io import SimulationPort
from blip.component import BoardSpec
from blip.board import Board, board_definition
from blip.arch.ecp5 import Ecp5Arch

class SimBoard(Board):
    def __init__(self, spec: BoardSpec):
        self.arch = Ecp5Arch()
        self.platform = None
        self.spec = spec
        self.leds: dict[int, SimulationPort] = { }

    def clk_freq(self) -> float:
        return 25e6

    def get_led(self, platform: Platform, index: int):
        led = self.leds.get(index)
        if led:
            return led
        led = SimulationPort("o", 1, name=f"led{index}")
        self.leds[index] = led
        return led

@board_definition("sim")
def sim_board(spec: BoardSpec):
    return SimBoard(spec)
