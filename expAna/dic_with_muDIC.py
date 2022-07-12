import os
import sys
import argparse
import dill
import muDIC
import numpy as np

import expAna

from natsort import natsorted
from expAna.misc import print_remarks_muDIC


def main(project_name="project", experiment_list=None, ignore_list=None, select=None):
    work_dir = os.getcwd()

    export2tif_dir = os.path.join(work_dir, "data_export2tif")
    dic_results_dir = os.path.join(work_dir, "data_muDIC")
    os.makedirs(dic_results_dir, exist_ok=True)

    # open project file located in export2tif_dir
    with open(
        os.path.join(export2tif_dir, project_name + "_expAna.pickle"), "rb",
    ) as myfile:
        current_project = dill.load(myfile)

    if experiment_list is None:
        experiment_names_list = list()
        print(
            f"No experiments passed. Performing DIC analysis for all experiments in project_expAna.pickle located in {export2tif_dir}."
        )
        for experiment_name in current_project.experiments.keys():
            experiment_names_list.append(experiment_name)
    else:
        experiment_names_list = experiment_list

    experiment_names_list = natsorted(experiment_names_list)

    if ignore_list is not None:
        for experiment in ignore_list:
            experiment_names_list.remove(experiment)

    # create experiment list from names list
    experiment_list = list()
    for exp_name in experiment_names_list:
        if select is None:
            experiment_list.append(current_project.experiments[exp_name])
        else:
            experiment = current_project.experiments[exp_name]
            if str(experiment.documentation_data[select[0]]) == str(select[1]):
                experiment_list.append(current_project.experiments[exp_name])
            else:
                pass

    # muDIC
    print_remarks_muDIC()
    project_mesher = muDIC.Mesher()

    # read only first image in each test folder to create the mesh with GUI
    for experiment in experiment_list:
        exp_name = experiment.name
        # create a mesh on the reference image and save to experiment
        experiment.mesh = project_mesher.mesh(
            images=muDIC.image_stack_from_list([experiment.ref_image])
        )

    # perform digital image correlation
    for experiment in experiment_list:
        exp_name = experiment.name
        # create the image stack
        image_stack = muDIC.image_stack_from_folder(
            os.path.join(current_project.export2tif_dir, exp_name), file_type=".tif"
        )
        # apply filter to image_stack
        image_stack.set_filter(muDIC.filtering.lowpass_gaussian, sigma=1.0)

        # define inputs for DIC
        inputs = muDIC.DICInput(
            experiment.mesh,
            image_stack,
            ref_update_frames=np.arange(0, experiment.image_count, 50).tolist(),
            noconvergence="ignore",
        )
        # create a digital image correlation analysis object with the inputs
        experiment.dic_job = muDIC.DICAnalysis(inputs)

    for experiment in experiment_list:
        exp_name = experiment.name
        # run digital image correlation job
        results = experiment.dic_job.run()
        # make the results accessible later
        experiment.results = muDIC.Fields(results)

        # export the results
        test_results_dir = os.path.join(dic_results_dir, experiment.name)
        os.makedirs(test_results_dir, exist_ok=True)

        muDIC.IO.save(
            results, os.path.join(test_results_dir, experiment.name + "_muDIC")
        )

        # extract the true strain field from the results
        true_strain = experiment.results.true_strain()
        # export the true strain field
        np.save(
            os.path.join(test_results_dir, experiment.name + "_true_strain"),
            true_strain,
        )

        # save experiment data
        with open(
            os.path.join(test_results_dir, experiment.name + "_expAna.pickle"), "wb",
        ) as myfile:
            dill.dump(experiment, myfile)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="Perform DIC on images exported to .tif."
    )
    arg_parser.add_argument(
        "-e",
        "--experiments",
        nargs="*",
        default=None,
        help="experiment folder name(s) located in ./data_export2tif/",
    )

    passed_args = arg_parser.parse_args()

    sys.exit(main(passed_args.experiments))
