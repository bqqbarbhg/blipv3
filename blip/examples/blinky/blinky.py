from amaranth import *
from amaranth.build import Platform
from blip.example import Example

class Blinky(Example):
    def __init__(self):
        pass

    def elaborate(self, platform: Platform):
        m = Module()

        counter = Signal(16)
        led = self.board.get_led(0)

        m.d.sync += [
            counter.eq(counter + 1),
        ]

        m.d.comb += [
            led.eq(counter[-1]),
        ]

        return m


