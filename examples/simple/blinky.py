from amaranth import *
from amaranth.build import Platform
from examples import example
from dataclasses import dataclass
import blip

@example("blinky")
class Blinky(Elaboratable):

    @dataclass
    class Config:
        counter_bits: int = 16
        led_index: int = 0

    def __init__(self, board: blip.Board, config: Config):
        self.board = board
        self.config = config

    def elaborate(self, platform: Platform):
        m = Module()

        counter = Signal(self.config.counter_bits)
        led = self.board.get_led(self.config.led_index)

        m.d.sync += [
            counter.eq(counter + 1),
        ]

        m.d.comb += [
            led.o.eq(counter[-1]),
        ]

        return m
