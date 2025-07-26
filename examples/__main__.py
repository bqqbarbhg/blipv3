import argparse
import os
import types
import importlib.util
import dataclasses
import tomllib
import subprocess
from blip import Board
from examples import all_examples
from amaranth.sim import Simulator

g_config = { }

def import_examples():
    self_path = os.path.dirname(__file__)
    for root, dirs, files in os.walk(self_path):
        rel_root = os.path.relpath(root, self_path)
        if rel_root == ".":
            continue

        for file in files:
            path = os.path.join(root, file)
            name = os.path.basename(file)
            spec = importlib.util.spec_from_file_location(name, path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

def get_config(example_type, argv_s):
    config_type = None
    if hasattr(example_type, "Config"):
        config_type = example_type.Config

    config_fields = dataclasses.fields(config_type)
    config_fields = { f.name: f for f in config_fields }

    s_values = { }
    for s in argv_s:
        s_name, s_value = s.split("=", maxsplit=1)
        s_field = config_fields[s_name]
        if s_field.type == int:
            s_values[s_name] = int(s_value)
        elif s_field.type == float:
            s_values[s_name] = float(s_value)
    config = config_type(**s_values)
    return config

def cmd_sim(argv):
    example_name = argv.name

    vcd_path = argv.o
    if not vcd_path:
        vcd_path = os.path.join("build", "sim", f"{example_name}.vcd")
    os.makedirs(os.path.dirname(vcd_path), exist_ok=True)

    board_name = argv.board
    if not board_name:
        board_name = g_config.get("sim_board")
        assert board_name, "no default sim_board set"
    board: Board = Board.load(board_name, sim=True)

    example_type = all_examples.get(example_name)
    assert example_type, f"no example found for name '{example_name}'"
    config = get_config(example_type, argv.s)

    example = example_type(board, config)

    t_ck = 1.0 / board.spec.clk_freq

    sim = board.simulate(example)
    sim.add_clock(t_ck)
    with sim.write_vcd(vcd_path):
        sim.run_until(t_ck * argv.duration)

def do_build(argv, example_name):
    build_path = argv.o
    if not build_path:
        build_path = os.path.join("build", "build", example_name)
    os.makedirs(build_path, exist_ok=True)

    board_name = argv.board
    if not board_name:
        board_name = g_config.get("build_board")
        assert board_name, "no default build_board set"
    board: Board = Board.load(board_name)

    print(f"Building {example_name} for {board.spec.info.name}")

    example_type = all_examples.get(example_name)
    assert example_type, f"no example found for name '{example_name}'"
    config = get_config(example_type, argv.s)

    example = example_type(board, config)

    platform = board.platform
    assert platform, "attempting to run without a platform"

    platform.build(example, build_dir=build_path)

def cmd_build(argv):
    if argv.name:
        assert not argv.all
        do_build(argv, argv.name)
    elif argv.all:
        assert not argv.o, "-o not supported with --all"
        assert not argv.s, "-s not supported with --all"
        for example in all_examples:
            do_build(argv, example)
    else:
        raise RuntimeError("Either specify example to build or --all")

def cmd_run(argv):
    example_name = argv.name

    build_path = argv.o
    if not build_path:
        build_path = os.path.join("build", "run", example_name)
    os.makedirs(build_path, exist_ok=True)

    board_name = argv.board
    if not board_name:
        board_name = g_config.get("run_board")
        assert board_name, "no default run_board set"
    board: Board = Board.load(board_name)

    example_type = all_examples.get(example_name)
    assert example_type, f"no example found for name '{example_name}'"
    config = get_config(example_type, argv.s)

    example = example_type(board, config)

    platform = board.platform
    assert platform, "attempting to run without a platform"

    program_tool = g_config.get("program_tool")
    if program_tool:
        def toolchain_program(self, products, name):
            with products.extract("{}.bit".format(name)) as bitstream_filename:
                subprocess.check_call([program_tool, bitstream_filename])
        platform.toolchain_program = types.MethodType(toolchain_program, platform)

    platform.build(example, do_program=True, build_dir=build_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("examples")
    parser.add_argument("--config", help="Configuration path to use")

    subparsers = parser.add_subparsers(dest="cmd", help="Commands")

    sim_parser = subparsers.add_parser("simulate", aliases=["sim"], help="Simulate an example")
    sim_parser.add_argument("name", help="Example name to simulate")
    sim_parser.add_argument("--board", help="Board to use")
    sim_parser.add_argument("-s", nargs="*", default=[], action="extend", help="Set configuration")
    sim_parser.add_argument("-o", metavar="path.vcd", help="VXD output path")
    sim_parser.add_argument("--duration", type=int, default=100, help="Number of clock cycles to run")
    sim_parser.set_defaults(cmd=cmd_sim)

    sim_parser = subparsers.add_parser("build", help="Build an example")
    sim_parser.add_argument("name", nargs="?", help="Example name to build")
    sim_parser.add_argument("--board", help="Board to use")
    sim_parser.add_argument("-s", nargs="*", default=[], action="extend", help="Set configuration")
    sim_parser.add_argument("-o", metavar="build/path", help="Output build path")
    sim_parser.add_argument("--all", action="store_true", help="Build all examples")
    sim_parser.set_defaults(cmd=cmd_build)

    sim_parser = subparsers.add_parser("run", help="Run an example")
    sim_parser.add_argument("name", help="Example name to run")
    sim_parser.add_argument("--board", help="Board to use")
    sim_parser.add_argument("-s", nargs="*", default=[], action="extend", help="Set configuration")
    sim_parser.add_argument("-o", metavar="build/path", help="Output build path")
    sim_parser.set_defaults(cmd=cmd_run)

    argv = parser.parse_args()

    import_examples()

    self_path = os.path.dirname(__file__)
    config_local_path = os.path.join(self_path, "config.local.toml")
    config_default_path = os.path.join(self_path, "config.default.toml")

    if argv.config:
        config_path = argv.config
    elif os.path.exists(config_local_path):
        config_path = config_local_path
    else:
        config_path = config_default_path

    with open(config_path, "rb") as f:
        g_config = tomllib.load(f)

    argv.cmd(argv)
