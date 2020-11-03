import os
import sys
import argparse
import dill
import numpy as np
import pandas as pd
import gui_funcs
import plot_funcs
import dic_post_funcs
import istra2muDIC_functions as funcs

from natsort import natsorted

filepath = os.path.abspath(os.path.dirname(__file__))

istra_evaluation_dir = os.path.join(filepath, "..", "data_istra_evaluation")

arg_parser = argparse.ArgumentParser(
    description="istra2true_stress offers `gauge` element functionality based on Python."
)
arg_parser.add_argument(
    "-e",
    "--experiments",
    nargs="*",
    default=None,
    help="experiment folder name(s) located in ../data_istra_acquisition/",
)

passed_args = arg_parser.parse_args()

if passed_args.experiments is None:
    experiment_list = list()
    print(
        f"No experiments passed. Will search for folders named `Test*` in {istra_acquisition_dir}."
    )
    for path, directories, files in os.walk(istra_acquisition_dir):
        for test_dir in directories:
            if str(test_dir[:5] == "Test"):
                experiment_list.append(test_dir)
else:
    experiment_list = passed_args.experiments

experiment_list = natsorted(experiment_list)

# what should the plot util do?
# - plot averaged stress strain curves that match criterion like "orientation"= "parallel to flow"
# - plot stress strain curves of experiments that match criterion like "orientation"= "parallel to flow" with reduced alpha in same plot
# - plot averaged stress strain curves of experiments that differ in a feature like "orientation" for comparison
#
#
# input arguments:
#   - selection feature (string) experiment.documentation_data[<key>], i.e. experiment.documentation_data["specimen_orientation"]
#   - selection criterion (string) value (or part of value) of experiment.documentation_data[<key>]
#   - plot original curves (boolean)

# from istraCORN2true_stress
for test_dir in experiment_list:
    with open(
        os.path.join(
            istra_evaluation_dir,
            test_dir + "CORN1",
            test_dir + "CORN1_experiment_data.p",
        ),
        "rb",
    ) as myfile:
        experiment = dill.load(myfile)

    # plot results to file
    plot_funcs.remove_offsets(experiment)

    fail_location = gui_funcs.FailureLocator()
    fail_location.__gui__(experiment)

    plot_funcs.plot_true_stress_strain(experiment=experiment, out_dir=vis_export_dir)
    plot_funcs.plot_volume_strain(experiment=experiment, out_dir=vis_export_dir)

    gui_funcs.set_gui_backend()

    # export experiment data
    with open(
        os.path.join(
            experiment.test_results_dir, experiment.name + "CORN1_experiment_data.p"
        ),
        "wb",
    ) as myfile:
        dill.dump(experiment, myfile)

# from muDIC2true_stress
for test_dir in experiment_list:
    with open(
        os.path.join(dic_results_dir, test_dir, test_dir + "_true_strain.npy"), "rb",
    ) as myfile:
        true_strain = np.load(myfile)
    with open(
        os.path.join(dic_results_dir, test_dir, test_dir + "_experiment_data.p"), "rb",
    ) as myfile:
        experiment = dill.load(myfile)

    # plot results to file
    plot_funcs.remove_offsets(experiment)

    fail_location = gui_funcs.FailureLocator()
    fail_location.__gui__(experiment)

    plot_funcs.plot_true_stress_strain(experiment=experiment, out_dir=vis_export_dir)
    plot_funcs.plot_volume_strain(experiment=experiment, out_dir=vis_export_dir)

    gui_funcs.set_gui_backend()

    # export experiment data
    with open(
        os.path.join(
            experiment.test_results_dir, experiment.name + "_experiment_data.p"
        ),
        "wb",
    ) as myfile:
        dill.dump(experiment, myfile)
