from blip import Board
from examples.pll.triple_blinky import TripleBlinky
from amaranth.sim import Simulator
import os

def test_triple_blinky():
    board: Board = Board.load("mini3s", sim=True)
    assert board

    config = TripleBlinky.Config(
        blink_interval=2e-6,
        desync_bits=4,
    )

    t_ck = 1.0 / board.spec.clk_freq

    dut = TripleBlinky(board, config)
    sim = board.simulate(dut)
    sim.add_clock(t_ck)

    leds = [board.get_led(n) for n in range(3)]

    async def testbench(ctx):
        await ctx.delay(config.blink_interval / 2)
        while True:
            for led in leds:
                assert ctx.get(led.o) == 0
            await ctx.delay(config.blink_interval)
            for led in leds:
                assert ctx.get(led.o) == 1
            await ctx.delay(config.blink_interval)

    def desync_testbench(led, mhz):
        async def inner(ctx):
            interval = 1e-6 / mhz * (1 << (config.desync_bits - 1))
            await ctx.delay(interval / 2)
            while True:
                assert ctx.get(led.o) == 0
                await ctx.delay(interval)
                assert ctx.get(led.o) == 1
                await ctx.delay(interval)
        return inner

    sim.add_testbench(testbench)
    sim.add_testbench(desync_testbench(board.get_led(4), config.mhz_a))
    sim.add_testbench(desync_testbench(board.get_led(5), config.mhz_b))
    sim.add_testbench(desync_testbench(board.get_led(6), config.mhz_c))

    os.makedirs("build/tests", exist_ok=True)
    with sim.write_vcd("build/tests/triple_blinky.vcd"):
        sim.run_until(t_ck * 500)
