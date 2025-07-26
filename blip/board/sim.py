from amaranth.build import Platform
from amaranth.sim import Simulator
from amaranth.lib.io import SimulationPort
from blip.component import BoardSpec
from blip.board import Board, board_definition
from blip.arch.sim import SimArch

class SimBoard(Board):
    def __init__(self, spec: BoardSpec):
        self.arch = SimArch()
        self.platform = None
        self.spec = spec
        self.leds: dict[int, SimulationPort] = { }

    def get_led(self, index: int):
        led = self.leds.get(index)
        if led:
            return led
        led = SimulationPort("o", 1, name=f"led{index}")
        self.leds[index] = led
        return led

@board_definition("sim")
def sim_board(spec: BoardSpec):
    return SimBoard(spec)
