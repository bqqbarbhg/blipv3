from amaranth import *
from amaranth.build import Platform
from examples import example
from dataclasses import dataclass
import blip
from blip.arch.pll import PllClock

MHz = 1e6

@example("triple_blinky")
class TripleBlinky(Elaboratable):

    @dataclass
    class Config:
        blink_interval: float = 1.0
        desync_bits: int = 24
        mhz_a: int = 10
        mhz_b: int = 20
        mhz_c: int = 30

    def __init__(self, board: blip.Board, config: Config):
        self.board = board
        self.config = config

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        board = self.board
        arch = board.arch
        config = self.config

        m.submodules.pll = pll = arch.create_pll(board.spec.clk_freq, [
            PllClock(config.mhz_a*MHz), PllClock(config.mhz_b*MHz), PllClock(config.mhz_c*MHz)
        ])

        m.domains.a = ClockDomain("a")
        m.domains.b = ClockDomain("b")
        m.domains.c = ClockDomain("c")

        m.d.comb += [
            pll.i_clk.eq(ClockSignal()),
            ClockSignal("a").eq(pll.o_clk[0]),
            ClockSignal("b").eq(pll.o_clk[1]),
            ClockSignal("c").eq(pll.o_clk[2]),
        ]

        max_count = int(1_000_000 * self.config.blink_interval)

        ca = Signal(range(config.mhz_a * max_count + 1))
        cb = Signal(range(config.mhz_b * max_count + 1))
        cc = Signal(range(config.mhz_c * max_count + 1))
        la = Signal()
        lb = Signal()
        lc = Signal()

        m.domain.a += ca.eq(ca + 1)
        m.domain.b += cb.eq(cb + 1)
        m.domain.c += cc.eq(cc + 1)

        with m.If(ca == config.mhz_a * max_count):
            m.domain.a += ca.eq(0)
            m.domain.a += la.eq(~la)

        with m.If(cb == config.mhz_b * max_count):
            m.domain.b += cb.eq(0)
            m.domain.b += lb.eq(~lb)

        with m.If(cc == config.mhz_c * max_count):
            m.domain.c += cc.eq(0)
            m.domain.c += lc.eq(~lc)

        m.d.comb += [
            board.get_led(0).o.eq(la),
            board.get_led(1).o.eq(lb),
            board.get_led(2).o.eq(lc),
        ]

        fa = Signal(config.desync_bits)
        fb = Signal(config.desync_bits)
        fc = Signal(config.desync_bits)

        m.domain.a += fa.eq(fa + 1)
        m.domain.b += fb.eq(fb + 1)
        m.domain.c += fc.eq(fc + 1)

        m.d.comb += [
            board.get_led(4).o.eq(fa[-1]),
            board.get_led(5).o.eq(fb[-1]),
            board.get_led(6).o.eq(fc[-1]),
        ]

        return m
