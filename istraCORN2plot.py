import os
import sys
import argparse
import dill
import numpy as np
import pandas as pd
import gauge_funcs
import plot_funcs
import istra2muDIC_functions as funcs

from natsort import natsorted

filepath = os.path.abspath(os.path.dirname(__file__))

istra_acquisition_dir = os.path.join(filepath, "..", "data_istra_acquisition")
istra_evaluation_dir = os.path.join(filepath, "..", "data_istra_evaluation")
vis_export_dir = os.path.join(filepath, "..", "visualisation_istra")

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
        f"No experiments passed. Will search for folders named `Test*` in {current_project.istra_acquisition_dir}."
    )
    for path, directories, files in os.walk(current_project.istra_acquisition_dir):
        for test_dir in directories:
            if str(test_dir[:5] == "Test"):
                experiment_list.append(test_dir)
else:
    experiment_list = passed_args.experiments

experiment_list = natsorted(experiment_list)

for test_dir in experiment_list:
    # create experiment object
    current_test = funcs.Experiment(name=test_dir)
    current_test.read_istra_evaluation(istra_acquisition_dir, istra_evaluation_dir)

    direction_selector = gauge_funcs.TensileDirection(current_test.ref_image)
    direction_selector.__gui__()
    current_test.tensile_direction = direction_selector.direction

    if current_test.tensile_direction == "x":
        x_idx = 0
        y_idx = 1
    else:
        x_idx = 1
        y_idx = 0

    # get strains from evaluation
    # pixel gradients are treated as elements of the deformation gradient
    true_strain = gauge_funcs.get_true_strain(current_test.def_grad)
    true_strain[:, :, :, :][current_test.mask[:, :, :, 0] == 0] = np.nan

    gauge = gauge_funcs.RectangleCoordinates(
        input_image=true_strain[int(0.75 * current_test.image_count), :, :, x_idx]
    )
    gauge.__gui__()

    [x_min, y_min, x_max, y_max] = [int(i) for i in gauge.coordinates]

    # image coordinates assume x-axis horizontal (i.e. columns)
    # and y-axis vertical (i.e. rows)
    true_strain_gauge = true_strain[:, y_min:y_max, x_min:x_max, :]

    true_strain_mean = np.nanmean(true_strain_gauge, axis=(1, 2))

    specimen_width = 12.0  # mm
    specimen_thickness = 3.0  # mm

    true_stress_in_MPa = gauge_funcs.get_true_stress(
        force_in_N=current_test.reaction_force * 1000.0,
        true_strain_perpendicular=true_strain_mean[:, y_idx].reshape(
            (current_test.image_count, 1)
        ),
        specimen_cross_section_in_mm2=specimen_width * specimen_thickness,
    )

    poissons_ratio = np.vstack(
        [
            np.array([0.0]),
            (-true_strain_mean[1:, y_idx] / true_strain_mean[1:, x_idx]).reshape(
                current_test.image_count - 1, 1
            ),
        ]
    )

    volume_strain = (
        true_strain_mean[:, x_idx] + 2.0 * true_strain_mean[:, y_idx]
    ).reshape(current_test.image_count, 1)

    current_test.gauge_results = pd.DataFrame(
        data=np.concatenate(
            (
                current_test.traverse_displ,
                current_test.reaction_force,
                true_strain_mean[:, x_idx].reshape((current_test.image_count, 1)),
                true_strain_mean[:, y_idx].reshape((current_test.image_count, 1)),
                true_stress_in_MPa,
                poissons_ratio,
                volume_strain,
            ),
            axis=1,
        ),
        columns=[
            "displacement_in_mm",
            "reaction_force_in_kN",
            "true_strain_image_x",
            "true_strain_image_y",
            "true_stress_in_MPa",
            "poissons_ratio",
            "volume_strain",
        ],
    )
    # export dataframe with results as .csv
    current_test.test_results_dir = os.path.join(
        istra_evaluation_dir, current_test.name + "CORN1"
    )
    current_test.gauge_results.to_csv(
        os.path.join(
            current_test.test_results_dir, current_test.name + "CORN1_gauge_results.csv"
        )
    )

    # export experiment data
    with open(
        os.path.join(
            current_test.test_results_dir, current_test.name + "CORN1_experiment_data.p"
        ),
        "wb",
    ) as myfile:
        dill.dump(current_test, myfile)

for test_dir in experiment_list:
    with open(
        os.path.join(
            istra_evaluation_dir,
            current_test.name + "CORN1",
            current_test.name + "CORN1_experiment_data.p",
        ),
        "rb",
    ) as myfile:
        current_test = dill.load(myfile)

    # plot results to file
    plot_funcs.plot_true_stress_strain(experiment=current_test, out_dir=vis_export_dir)
    plot_funcs.plot_volume_strain(experiment=current_test, out_dir=vis_export_dir)
