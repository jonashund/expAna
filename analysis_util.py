import os
import sys
import argparse
import dill
import numpy as np
import pandas as pd
import gui_funcs
import plot_funcs
import istra2muDIC_functions as funcs
import utils

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

#   - selection feature (string) experiment.documentation_data[<key>], i.e. experiment.documentation_data["specimen_orientation"]
arg_parser.add_argument(
    "-k",
    "--key",
    metavar="experiment.documentation_data[<key>]",
    required=True,
    nargs=1,
    type=string,
    help="Dictionary key of dictionary experiment.documentation_data.",
)

#   - selection criterion (string) value (or part of value) of experiment.documentation_data[<key>]
arg_parser.add_argument(
    "-v",
    "--value",
    metavar="experiment.documentation_data[`key`]: <value>",
    nargs=1,
    default=None,
    help="Value for given --key argument of dictionary experiment.documentation_data.",
)

#   - plot original curves (boolean)
arg_parser.add_argument(
    "-a",
    "--all",
    metavar="plot_all_curves",
    type=bool,
    nargs=1,
    default=True,
    help="If `True` all curves are plotted as opposd to only the averaged curves if `False`.",
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

# get the list of experiments that are part of the analysis
experiment_list = natsorted(experiment_list)


# load all experiments and count the different values for given key
# compile a list of different values for given key
# create a dictionary that has every found value as key and a list of experiments with that value as list
# calculate the averages for each value
# plot average result for one value in a separate plot
# plot average results for all values in a plot
analysis_project = funcs.Project(name=analysis)
analysis_key = parsed_args.key
analysis_dict = {}

# load the experiments
for test_dir in experiment_list:
    with open(
        os.path.join(exp_data_dir, test_dir, test_dir + "_experiment_data.p"), "rb",
    ) as myfile:
        experiment = dill.load(myfile)

        analysis_project.add_experiment(experiment)

# compile list of different values for key or just filter experiments for given key
if parsed_args.value is None:
    analysis_values = []
    for experiment_name, experiment_data in analysis_project.experiments.items():
        analysis_values.append(experiment_data.documentation_data[analysis_key])
    analysis_values = set(analysis_values)
else:
    analysis_values = [analysis_key]

for analysis_value in analysis_values:
    analysis_dict[analysis_value] = {}
    analysis_dict[analysis_value]["experiment_list"] = []
    for experiment_name, experiment_data in analysis_project.experiments.items():
        if experiment_data.documentation_data[analysis_key] == analysis_value:
            analysis_dict[analysis_value]["experiment_list"].append(experiment_name)

# calculate average curves for every analasis_value
for analysis_value in analysis_values:
    true_strain_arrays = []
    true_stress_arrays = []
    # create list of arrays with x and y values
    for experiment_name in analysis_dict[analasis_value]["experiment_list"]:
        true_strain_arrays.append(
            analysis_project.experiments[experiment_name]
            .gauge_results["true_strain_image_x"]
            .to_numpy()
        )
        true_stress_arrays.append(
            analysis_project.experiments[experiment_name]
            .gauge_results["true_stress_in_MPa"]
            .to_numpy
        )

    mean_true_strain, mean_true_stress = utils.get_mean_curves(
        true_strain_arrays, true_stress_arrays
    )

    analysis_dict[analasis_value]["stress_strain_arrays"] = [
        mean_true_strain,
        mean_true_stress,
    ]

for analasis_value in analysis_values:
    plt.plot(
        analysis_dict[analysis_value]["stress_strain_arrays"][0],
        analysis_dict[analysis_value]["stress_strain_arrays"][1],
    )
    plt.show()
