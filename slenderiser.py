import os
import sys
import argparse
import dill
import istra2muDIC_functions as funcs

from utils import *

from natsort import natsorted

filepath = os.path.abspath(os.path.dirname(__file__))


arg_parser = argparse.ArgumentParser(
    description="Reduce file size of existing `Test*_epxeriment_data.p` files exported with istra2true_stress by only saving the metadata and gauge results."
)
arg_parser.add_argument(
    "-e",
    "--experiments",
    nargs="*",
    default=None,
    help="evaluation folder name(s) located in ../data_istra_evaluation/",
)

arg_parser.add_argument(
    "-dic",
    default="istra",
    help="Specify DIC software with which the results were obtained. Options: `istra` (default) or `muDIC`.",
)

passed_args = arg_parser.parse_args()

if passed_args.dic == "istra":
    exp_data_dir = os.path.join(filepath, "..", "data_istra_evaluation")
elif passed_args.dic == "muDIC":
    exp_data_dir = os.path.join(filepath, "..", "data_muDIC")
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
            if str("Test" in test_dir):
                experiment_list.append(test_dir)
else:
    experiment_list = passed_args.experiments

experiment_list = natsorted(experiment_list)

for test_dir in experiment_list:
    with open(
        os.path.join(exp_data_dir, test_dir, test_dir + "_experiment_data.p"), "rb",
    ) as myfile:
        experiment = dill.load(myfile)
    # try:
    #     experiment.slenderise()
    # except:
    #     new_experiment = funcs.Experiment(experiment.name)
    #     new_experiment.gauge_results = experiment.gauge_results
    #     new_experiment.documentation_data = experiment.documentation_data
    #     experiment = new_experiment
    #     print(
    #         "Data for export has been copied to `new_experiment` instance. `new_experiment` will be exported."
    #     )

    experiment.slenderise()

    with open(
        os.path.join(exp_data_dir, test_dir, test_dir + "_experiment_data.p"), "wb",
    ) as myfile:
        dill.dump(experiment, myfile)
