import os
import sys
import argparse
import dill
import numpy as np
import pandas as pd
import plot_funcs
import gui_funcs
import dic_post_funcs

from natsort import natsorted

filepath = os.path.abspath(os.path.dirname(__file__))

dic_results_dir = os.path.join(filepath, "..", "data_muDIC")

arg_parser = argparse.ArgumentParser(
    description="istra2true_stress offers `gauge` element functionality based on Python."
)
arg_parser.add_argument(
    "-e",
    "--experiments",
    nargs="*",
    default=None,
    help="experiment folder name(s) located in ../data_muDIC/",
)

arg_parser.add_argument(
    "-eco",
    default=True,
    help="Save space through not exporting the local strain fields but only the mean results from the gauge element.",
)

arg_parser.add_argument(
    "-g",
    "--geometry",
    nargs=2,
    metavar=("specimen_width", "specimen_thickness"),
    type=float,
    default=[12.0, 3.0],
    help="Specimen width and thickness in mm to compute cross section in DIC area.",
)

passed_args = arg_parser.parse_args()

if passed_args.experiments is None:
    experiment_list = list()
    print(
        f"No experiments passed. Will search for folders named `Test*` in {dic_results_dir}."
    )
    for path, directories, files in os.walk(dic_results_dir):
        for test_dir in directories:
            if str("Test" in test_dir):
                experiment_list.append(test_dir)
else:
    experiment_list = passed_args.experiments

experiment_list = natsorted(experiment_list)

for test_dir in experiment_list:
    with open(
        os.path.join(dic_results_dir, test_dir, test_dir + "_true_strain.npy"), "rb",
    ) as myfile:
        true_strain = np.load(myfile)
    with open(
        os.path.join(dic_results_dir, test_dir, test_dir + "_experiment_data.p"), "rb",
    ) as myfile:
        experiment = dill.load(myfile)

    direction_selector = gui_funcs.TensileDirection(experiment.ref_image)
    direction_selector.__gui__()
    experiment.tensile_direction = direction_selector.direction

    if experiment.tensile_direction == "x":
        x_idx = 0
        y_idx = 1
    else:
        x_idx = 1
        y_idx = 0

    true_strain_x = true_strain[0, x_idx, x_idx, :, :, :]
    experiment.muDIC_image_count = true_strain.shape[-1]
    plot_frame = int(0.8 * experiment.muDIC_image_count)

    mask = gui_funcs.RectangleCoordinates(input_image=true_strain_x[:, :, plot_frame].T)
    mask.__gui__()

    [x_min, y_min, x_max, y_max] = [int(i) for i in mask.coordinates]

    # image coordinates assume x-axis horizontal (i.e. columns)
    # and y-axis vertical (i.e. rows)
    true_strain_gauge = true_strain[0, :, :, x_min:x_max, y_min:y_max, :]

    true_strain_mean = np.nanmean(true_strain_gauge, axis=(2, 3))
    displacement_in_mm = experiment.traverse_displ[: experiment.muDIC_image_count, :]
    reaction_force_in_kN = experiment.reaction_force[: experiment.muDIC_image_count, :]

    specimen_width = passed_args.geometry[0]
    specimen_thickness = passed_args.geometry[1]

    true_stress_in_MPa = dic_post_funcs.get_true_stress(
        force_in_N=reaction_force_in_kN * 1000.0,
        true_strain_perpendicular=true_strain_mean[y_idx, y_idx, :].reshape(
            (experiment.muDIC_image_count, 1)
        ),
        specimen_cross_section_in_mm2=specimen_width * specimen_thickness,
    )

    poissons_ratio = np.vstack(
        [
            np.array([0.0]),
            (
                -true_strain_mean[y_idx, y_idx, 1:] / true_strain_mean[x_idx, x_idx, 1:]
            ).reshape(experiment.muDIC_image_count - 1, 1),
        ]
    )

    volume_strain = (
        true_strain_mean[x_idx, x_idx, :] + 2.0 * true_strain_mean[y_idx, y_idx, :]
    ).reshape(experiment.muDIC_image_count, 1)

    experiment.gauge_results = pd.DataFrame(
        data=np.concatenate(
            (
                displacement_in_mm,
                reaction_force_in_kN,
                true_strain_mean[x_idx, x_idx, :].reshape(
                    (experiment.muDIC_image_count, 1)
                ),
                true_strain_mean[y_idx, y_idx, :].reshape(
                    (experiment.muDIC_image_count, 1)
                ),
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

    test_results_dir = os.path.join(dic_results_dir, experiment.name)

    experiment.gauge_results.to_csv(
        os.path.join(test_results_dir, experiment.name + "_gauge_results.csv")
    )

    # export experiment data
    if passed_args.eco is True:
        experiment.slenderise()

    with open(
        os.path.join(test_results_dir, experiment.name + "_experiment_data.p"), "wb",
    ) as myfile:
        dill.dump(experiment, myfile)
