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
import matplotlib.pyplot as plt

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
    type=str,
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
    help="If `True` all curves are plotted as opposed to only the averaged curves if `False`.",
)

arg_parser.add_argument(
    "-d",
    "--dic",
    default="istra",
    help="Specify DIC software with which the results were obtained. Options: `istra` (default) or `muDIC`.",
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

# get the list of experiments that are part of the analysis
experiment_list = natsorted(experiment_list)


# load all experiments and count the different values for given key
# compile a list of different values for given key
# create a dictionary that has every found value as key and a list of experiments with that value as list
# calculate the averages for each value
# plot average result for one value in a separate plot
# plot average results for all values in a plot
analysis_key = passed_args.key[0]
analysis_dict = {}
analysis_project = funcs.Project(name=f"analysis_{analysis_key}")

# load the experiments
for test_dir in experiment_list:
    with open(
        os.path.join(exp_data_dir, test_dir, test_dir + "_experiment_data.p"), "rb",
    ) as myfile:
        experiment = dill.load(myfile)

        analysis_project.add_experiment(experiment)

# compile list of different values for key or just filter experiments for given key
if passed_args.value is None:
    analysis_values = []
    for experiment_name, experiment_data in analysis_project.experiments.items():
        analysis_values.append(experiment_data.documentation_data[analysis_key])
    # remove experiments with no value for given key
    analysis_values = list(filter(None, analysis_values))
    # remove duplicates from list
    analysis_values = set(analysis_values)
else:
    analysis_values = [analysis_value[0]]

for analysis_value in analysis_values:
    analysis_dict[analysis_value] = {}
    analysis_dict[analysis_value]["experiment_list"] = []
    for experiment_name, experiment_data in analysis_project.experiments.items():
        if experiment_data.documentation_data[analysis_key] == analysis_value:
            analysis_dict[analysis_value]["experiment_list"].append(experiment_name)

# calculate average curves for every analysis_value
for analysis_value in analysis_values:
    true_strains = []
    true_stresses = []
    vol_strains = []
    # create list of arrays with x and y values
    for experiment_name in analysis_dict[analysis_value]["experiment_list"]:
        true_strains.append(
            analysis_project.experiments[experiment_name]
            .gauge_results["true_strain_image_x"]
            .to_numpy()
        )
        true_stresses.append(
            analysis_project.experiments[experiment_name]
            .gauge_results["true_stress_in_MPa"]
            .to_numpy()
        )
        vol_strains.append(
            analysis_project.experiments[experiment_name]
            .gauge_results["volume_strain"]
            .to_numpy()
        )

    mean_strain, mean_stress = utils.get_mean_curves(true_strains, true_stresses)

    mean_strain, mean_vol_strain = utils.get_mean_curves(true_strains, vol_strains)

    analysis_dict[analysis_value]["mean_strain"] = mean_strain
    analysis_dict[analysis_value]["mean_stress"] = mean_stress
    analysis_dict[analysis_value]["strains"] = true_strains
    analysis_dict[analysis_value]["stresses"] = true_stresses
    analysis_dict[analysis_value]["vol_strains"] = vol_strains

# plot individual curves and averaged curves in one plot for each analysis value
for analysis_value in analysis_values:
    pass

# plot averaged curves for all analysis values in one comparison plot
for analysis_value in analysis_values:
    plt.plot(
        analysis_dict[analysis_value]["mean_strain"],
        analysis_dict[analysis_value]["mean_stress"],
    )
    plt.show()
    plt.plot(
        analysis_dict[analysis_value]["strains"],
        analysis_dict[analysis_value]["stresses"],
    )
    plt.show()
