import argparse

parser = argparse.ArgumentParser("blip")
subparsers = parser.add_subparsers(dest="cmd", help="Commands")
check_parser = subparsers.add_parser("example", help="Run an example")
check_parser.add_argument("name", nargs="*")
check_parser.add_argument("--list", action="store_true", default=False)
argv = parser.parse_args()

print(argv)
