import os
import sys
import argparse
import dill

import expAna

from natsort import natsorted


def main(
    experiment_list=None, keep_offset=True, set_failure=False,
):

    work_dir = os.getcwd()
    expDoc_data_dir = os.path.join(work_dir, "data_expDoc", "python")
    instron_data_dir = os.path.join(work_dir, "data_instron")
    vis_export_dir = os.path.join(work_dir, "visualisation")
    os.makedirs(vis_export_dir, exist_ok=True)

    if experiment_list is None:
        experiment_list = list()
        print(
            f"No experiments passed. Will search for folders named `Test*` in {instron_data_dir}."
        )
        for path, directories, files in os.walk(instron_data_dir):
            for test_dir in directories:
                if str(test_dir[:5] == "Test"):
                    experiment_list.append(test_dir)
    else:
        pass

    experiment_list = natsorted(experiment_list)

    for test_dir in experiment_list:
        # search for input data created with expDoc
        try:
            with open(
                os.path.join(expDoc_data_dir, test_dir + "_expDoc.p"), "rb",
            ) as myfile:
                experiment = dill.load(myfile)
        except:
            print(
                f"""
            Warning:
            No documentation data found for {test_dir}!
            Document your experiments properly using expDoc before using expAna.
            """
            )
            assert False

        # search for expAna data
        try:
            with open(
                os.path.join(vis_export_dir, test_dir + "_expAna.p"), "rb",
            ) as myfile:
                experiment = dill.load(myfile)
        except:
            with open(
                os.path.join(vis_export_dir, test_dir + "_expAna.p"), "wb",
            ) as myfile:
                dill.dump(experiment, myfile)

        if not keep_offset:
            expAna.vis.plot.remove_offsets(experiment)
        else:
            pass

        if set_failure:
            fail_location = expAna.gui.FailureLocator()
            fail_location.__gui__(experiment)
            # export truncated data
            with open(
                os.path.join(vis_export_dir, test_dir + "_expAna.p"), "wb",
            ) as myfile:
                dill.dump(experiment, myfile)
        else:
            pass

        # expAna.vis.plot.set_plt_backend()

    for test_dir in experiment_list:
        with open(
            os.path.join(vis_export_dir, test_dir + "_expAna.p"), "rb",
        ) as myfile:
            experiment = dill.load(myfile)

        experiment.plot_force_disp(out_dir=vis_export_dir)


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
