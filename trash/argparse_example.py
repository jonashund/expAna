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

arg_parser.add_argument(
    "-g",
    "--geometry",
    nargs=2,
    metavar=("specimen_width", "specimen_thickness"),
    type=float,
    default=[12.0, 3.0],
    help="Specimen width and thickness in mm to compute cross section in DIC area.",
)

passed_args = arg_parser.parse_args()

print(f"{passed_args.experiments == None}")

print(f"{passed_args.geometry}")

specimen_width = passed_args.geometry[0]
specimen_thickness = passed_args.geometry[1]
