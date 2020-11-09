import os
import sys
import argparse
import dill

from natsort import natsorted

import ana_tools.data_trans as data_trans


def main(experiment_list=None):
    work_dir = os.getcwd()

    test_reports_dir_python = os.path.join(work_dir, "test_reports", "python")
    export2tif_dir = os.path.join(work_dir, "data_export2tif")
    dic_results_dir = os.path.join(work_dir, "data_muDIC")
    istra_acquisition_dir = os.path.join(work_dir, "data_istra_acquisition")

    os.makedirs(export2tif_dir, exist_ok=True)
    os.makedirs(dic_results_dir, exist_ok=True)

    if experiment_list == None:
        experiment_list = list()
        print(
            f"No experiments passed. Will search for folders named `Test*` in {istra_acquisition_dir}."
        )
        for path, directories, files in os.walk(istra_acquisition_dir):
            for test_dir in directories:
                if str(test_dir[:5] == "Test"):
                    experiment_list.append(test_dir)
    else:
        pass

    experiment_list = natsorted(experiment_list)

    current_project = data_trans.Project(
        "project", istra_acquisition_dir, export2tif_dir, dic_results_dir
    )
    for test_dir in experiment_list:
        try:
            with open(
                os.path.join(test_reports_dir_python, test_dir + "_experiment_data.p"),
                "rb",
            ) as myfile:
                experiment = dill.load(myfile)
        except:
            experiment = data_trans.Experiment(name=test_dir)
            print(
                f"""
            Warning:
            No documentation data found for {test_dir}!
            Document your experiments properly using expDoc.
            """
            )

        experiment.read_and_convert_istra_images(
            current_project.istra_acquisition_dir, current_project.export2tif_dir,
        )
        current_project.add_experiment(experiment)

    # export project
    with open(
        os.path.join(export2tif_dir, current_project.name + "_data.p"), "wb",
    ) as myfile:
        dill.dump(current_project, myfile)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Import images from Istra4D acquisition files and export to .tif."
    )
    arg_parser.add_argument(
        "-e",
        "--experiments",
        nargs="*",
        default=None,
        help="experiment folder name(s) located in ./data_istra_acquisition/",
    )

    passed_args = arg_parser.parse_args()

    sys.exit(main(passed_args.experiments))
