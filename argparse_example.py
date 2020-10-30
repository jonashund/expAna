import argparse

import os
import sys

# create the parser
arg_parser = argparse.ArgumentParser(
    description="istra2true_stress offers `gauge` element functionality based on Python."
)

# add the arguments
arg_parser.add_argument(
    "-e",
    "--experiments",
    nargs="*",
    default=None,
    help="experiment folder name(s) located in ../data_istra_acquisition/",
)

passed_args = arg_parser.parse_args()

print(f"{passed_args.experiments == None}")
print(f"{passed_args.experiments[0]}")
