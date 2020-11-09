import os
import sys
import argparse
import dill
import numpy as np
import pandas as pd

import ana_tools.gui as gui
import ana_tools.plot as plot

from natsort import natsorted


def main(experiment_list=None, keep_offset=True, set_failure=False, dic_system="istra"):
    work_dir = os.getcwd()

    if dic_system == "istra":
        exp_data_dir = os.path.join(work_dir, "data_istra_evaluation")
        vis_export_dir = os.path.join(work_dir, "visualisation_istra")
    elif dic_system == "muDIC":
        exp_data_dir = os.path.join(work_dir, "data_muDIC")
        vis_export_dir = os.path.join(work_dir, "visualisation_muDIC")
    else:
        raise InputError(
            "-dic", f"`{dic_system}` is not a valid value for argument `-dic`"
        )

    if experiment_list is None:
        experiment_list = list()
        print(
            f"No experiments passed. Will search for folders named `Test*` in {exp_data_dir}."
        )
        for path, directories, files in os.walk(exp_data_dir):
            for test_dir in directories:
                if str(test_dir[:5] == "Test"):
                    experiment_list.append(test_dir)
    else:
        pass

    experiment_list = natsorted(experiment_list)

    for test_dir in experiment_list:
        with open(
            os.path.join(exp_data_dir, test_dir, test_dir + "_experiment_data.p"), "rb",
        ) as myfile:
            experiment = dill.load(myfile)

        # plot results to file

        if not keep_offset:
            plot.remove_offsets(experiment)
        else:
            pass

        if set_failure:
            fail_location = gui.FailureLocator()
            fail_location.__gui__(experiment)
            # export truncated data
            with open(
                os.path.join(exp_data_dir, test_dir, test_dir + "_experiment_data.p"),
                "wb",
            ) as myfile:
                dill.dump(experiment, myfile)
        else:
            pass

        experiment.plot_true_stress(out_dir=vis_export_dir)
        experiment.plot_volume_strain(out_dir=vis_export_dir)

        plot.set_plot_backend()


if __name__ == "__main__":

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

    sys.exit(
        main(
            experiment_list=passed_args.experiments,
            keep_offset=passed_args.offset,
            set_failure=passed_args.fail,
            dic_system=passed_args.dic,
        )
    )
