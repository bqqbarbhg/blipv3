from blip import Board
from examples.simple.blinky import Blinky
from amaranth.sim import Simulator
import os
import itertools

def test_blinky():
    board: Board = Board.load("mini3s", sim=True)
    assert board

    config = Blinky.Config(
        counter_bits=4,
    )

    t_ck = 1.0 / board.spec.clk_freq

    dut = Blinky(board, config)
    sim = board.simulate(dut)
    sim.add_clock(t_ck)

    led = board.get_led(config.led_index)

    async def testbench(ctx):
        for n in itertools.count(0):
            ref = (n >> (config.counter_bits - 1)) & 1
            assert ctx.get(led.o) == ref
            await ctx.tick()

    sim.add_testbench(testbench)

    os.makedirs("build/tests", exist_ok=True)
    with sim.write_vcd("build/tests/blinky.vcd"):
        sim.run_until(t_ck * 100)
