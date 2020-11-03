import os
import sys
import argparse
import dill
import numpy as np
import pandas as pd
import gui_funcs
import plot_funcs
import istra2muDIC_functions as funcs

from natsort import natsorted

filepath = os.path.abspath(os.path.dirname(__file__))

arg_parser = argparse.ArgumentParser(
    description="plot utility for results obtained with istra2true_stress or muDIC2true_stress"
)
arg_parser.add_argument(
    "-e",
    "--experiments",
    nargs="*",
    default=None,
    help="experiment folder name(s) located in ../data_istra_acquisition/",
)

arg_parser.add_argument(
    "-d",
    "--dic",
    default="istra",
    help="Specify DIC software with which the results were obtained. Options: `istra` (default) or `muDIC`.",
)

arg_parser.add_argument(
    "-f",
    "--fail",
    default=False,
    help="If `True` the option to graphically determine the failure strain of each curve will be called. If `False` all data points found in `experiment_data` will be plotted to files.",
)

arg_parser.add_argument(
    "-o",
    "--offset",
    default=True,
    help="If `False` the curve offsets in terms of force and displacement are removed automatically",
)


passed_args = arg_parser.parse_args()

if passed_args.dic == "istra":
    exp_data_dir = os.path.join(filepath, "..", "data_istra_evaluation")
    vis_export_dir = os.path.join(filepath, "..", "visualisation_istra")
elif passed_args.dic == "muDIC":
    exp_data_dir = os.path.join(filepath, "..", "data_muDIC")
    vis_export_dir = os.path.join(filepath, "..", "visualisation_muDIC")

else:
    raise InputError(
        "-dic", f"`{passed_args.dic}` is not a valid value for argument `-dic`"
    )

if passed_args.experiments is None:
    experiment_list = list()
    print(
        f"No experiments passed. Will search for folders named `Test*` in {exp_data_dir}."
    )
    for path, directories, files in os.walk(exp_data_dir):
        for test_dir in directories:
            if str(test_dir[:5] == "Test"):
                experiment_list.append(test_dir)
else:
    experiment_list = passed_args.experiments

experiment_list = natsorted(experiment_list)

for test_dir in experiment_list:
    with open(
        os.path.join(exp_data_dir, test_dir, test_dir + "_experiment_data.p"), "rb",
    ) as myfile:
        experiment = dill.load(myfile)

    # plot results to file

    if not passed_args.offset:
        plot_funcs.remove_offsets(experiment)
    else:
        pass

    if passed_args.fail:
        fail_location = gui_funcs.FailureLocator()
        fail_location.__gui__(experiment)
        # export truncated data
        with open(
            os.path.join(exp_data_dir, test_dir, test_dir + "_experiment_data.p"), "wb",
        ) as myfile:
            dill.dump(experiment, myfile)
    else:
        pass

    plot_funcs.plot_true_stress_strain(experiment=experiment, out_dir=vis_export_dir)
    plot_funcs.plot_volume_strain(experiment=experiment, out_dir=vis_export_dir)

    gui_funcs.set_gui_backend()
