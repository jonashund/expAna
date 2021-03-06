import os
import sys
import argparse
import dill

from natsort import natsorted

import expAna


def main(experiment_list=None, ignore_list=None, select=None):
    work_dir = os.getcwd()

    expAna_docu_dir = os.path.join(work_dir, "expAna_docu", "python")
    expAna_data_dir = os.path.join(work_dir, "expAna_data")
    export2tif_dir = os.path.join(work_dir, "data_export2tif")
    istra_acquisition_dir = os.path.join(work_dir, "data_istra_acquisition")

    os.makedirs(expAna_data_dir, exist_ok=True)
    os.makedirs(export2tif_dir, exist_ok=True)

    if experiment_list is None:
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

    if ignore_list is not None:
        for experiment in ignore_list:
            experiment_list.remove(experiment)
    else:
        pass

    current_project = expAna.data_trans.Project(
        "project",
        istra_acquisition_dir=istra_acquisition_dir,
        export2tif_dir=export2tif_dir,
        expAna_data_dir=expAna_data_dir,
        expAna_docu_dir=expAna_docu_dir,
    )
    for test_dir in experiment_list:
        try:
            with open(
                os.path.join(expAna_docu_dir, test_dir + "_docu.pickle"), "rb",
            ) as myfile:
                experiment = dill.load(myfile)
        except:
            experiment = expAna.data_trans.Experiment(name=test_dir)
            print(
                f"""
            Warning:
            No documentation data found for {test_dir}!
            Document your experiments properly using expDoc.
            Analysis features can only be used with expDoc data.
            """
            )

        experiment.read_and_convert_istra_images(
            current_project.istra_acquisition_dir, current_project.export2tif_dir,
        )
        current_project.add_experiment(experiment)

        if select is not None:
            if str(experiment.documentation_data[select[0]]) == str(select[1]):
                pass
            else:
                continue
        else:
            pass

    # export project
    with open(
        os.path.join(expAna_data_dir, current_project.name + "_expAna.pickle"), "wb",
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
