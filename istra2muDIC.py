import os
import sys
import argparse
import dill
import numpy as np
import muDIC as dic

from natsort import natsorted

import istra2muDIC_functions as funcs

funcs.print_remarks()

filepath = os.path.abspath(os.path.dirname(__file__))

test_reports_dir_python = os.path.join(filepath, "..", "test_reports", "python")
export2tif_dir = os.path.join(filepath, "..", "data_export2tif")
dic_results_dir = os.path.join(filepath, "..", "data_muDIC")
istra_acquisition_dir = os.path.join(filepath, "..", "data_istra_acquisition")

os.makedirs(export2tif_dir, exist_ok=True)
os.makedirs(dic_results_dir, exist_ok=True)

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

if passed_args.experiments == None:
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

project_mesher = dic.Mesher()

current_project = funcs.Project(
    "project_name", istra_acquisition_dir, export2tif_dir, dic_results_dir
)

for test_dir in experiment_list:
    try:
        with open(
            os.path.join(test_reports_dir_python, test_dir + "_experiment_data.p"),
            "rb",
        ) as myfile:
            experiment = dill.load(myfile)
    except:
        experiment = funcs.Experiment(name=test_dir)
        print(
            f"""
        Warning:
        No documentation data found for {test_dir}!
        Document your experiments properly using instron2doc.
        """
        )

    experiment.read_and_convert_istra_images(
        current_project.istra_acquisition_dir, current_project.export2tif_dir,
    )
    current_project.add_experiment(experiment)

# muDIC
# read only first image in each test folder to create the mesh with GUI
for exp_name, experiment in current_project.experiments.items():
    # create a mesh on the reference image and save to experiment
    experiment.mesh = project_mesher.mesh(
        images=dic.image_stack_from_list([experiment.ref_image])
    )

# perform digital image correlation
for exp_name, experiment in current_project.experiments.items():
    # create the image stack
    image_stack = dic.image_stack_from_folder(
        os.path.join(current_project.export2tif_dir, exp_name), file_type=".tif"
    )
    # apply filter to image_stack
    image_stack.set_filter(dic.filters.lowpass_gaussian, sigma=1.0)

    # define inputs for DIC
    inputs = dic.DICInput(
        experiment.mesh,
        image_stack,
        ref_update_frames=np.arange(0, experiment.image_count, 50).tolist(),
        noconvergence="ignore",
    )
    # create a digital image correlation analysis object with the inputs
    experiment.dic_job = dic.DICAnalysis(inputs)

for exp_name, experiment in current_project.experiments.items():
    # run digital image correlation job
    results = experiment.dic_job.run()
    # make the results accessible later
    experiment.results = dic.Fields(results)

    # export the results
    experiment.test_results_dir = os.path.join(dic_results_dir, experiment.name)
    os.makedirs(experiment.test_results_dir, exist_ok=True)

    dic.IO.save(
        results, os.path.join(experiment.test_results_dir, experiment.name + "_muDIC")
    )

    # extract the true strain field from the results
    true_strain = experiment.results.true_strain()
    # export the true strain field
    np.save(
        os.path.join(experiment.test_results_dir, experiment.name + "_true_strain"),
        true_strain,
    )

    # save experiment data
    with open(
        os.path.join(
            experiment.test_results_dir, experiment.name + "_experiment_data.p"
        ),
        "wb",
    ) as myfile:
        dill.dump(experiment, myfile)
