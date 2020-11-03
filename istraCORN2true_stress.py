import os
import sys
import argparse
import dill
import numpy as np
import pandas as pd
import gui_funcs
import plot_funcs
import dic_post_funcs
import istra2muDIC_functions as funcs

from natsort import natsorted

filepath = os.path.abspath(os.path.dirname(__file__))

test_reports_dir_python = os.path.join(filepath, "..", "test_reports", "python")
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

arg_parser.add_argument(
    "-eco",
    default=True,
    help="Save space through not exporting the local strain fields but only the mean results from the gauge element.",
)

passed_args = arg_parser.parse_args()

if passed_args.experiments is None:
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

if passed_args.gauge is True:
    for test_dir in experiment_list:
        # load or create experiment object
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

        experiment.read_istra_evaluation(istra_acquisition_dir, istra_evaluation_dir)

        direction_selector = gui_funcs.TensileDirection(experiment.ref_image)
        direction_selector.__gui__()
        experiment.tensile_direction = direction_selector.direction

        if experiment.tensile_direction == "x":
            x_idx = 0
            y_idx = 1
        else:
            x_idx = 1
            y_idx = 0

        # get strains from evaluation
        # pixel gradients are treated as elements of the deformation gradient
        true_strain = dic_post_funcs.get_true_strain(experiment.def_grad)
        true_strain[:, :, :, :][experiment.mask[:, :, :, 0] == 0] = np.nan

        gauge = gui_funcs.RectangleCoordinates(
            input_image=true_strain[int(0.75 * experiment.image_count), :, :, x_idx]
        )
        gauge.__gui__()

        [x_min, y_min, x_max, y_max] = [int(i) for i in gauge.coordinates]

        # image coordinates assume x-axis horizontal (i.e. columns)
        # and y-axis vertical (i.e. rows)
        true_strain_gauge = true_strain[:, y_min:y_max, x_min:x_max, :]

        true_strain_mean = np.nanmean(true_strain_gauge, axis=(1, 2))

        specimen_width = 12.0  # mm
        specimen_thickness = 3.0  # mm

        true_stress_in_MPa = dic_post_funcs.get_true_stress(
            force_in_N=experiment.reaction_force * 1000.0,
            true_strain_perpendicular=true_strain_mean[:, y_idx].reshape(
                (experiment.image_count, 1)
            ),
            specimen_cross_section_in_mm2=specimen_width * specimen_thickness,
        )

        poissons_ratio = np.vstack(
            [
                np.array([0.0]),
                (-true_strain_mean[1:, y_idx] / true_strain_mean[1:, x_idx]).reshape(
                    experiment.image_count - 1, 1
                ),
            ]
        )

        volume_strain = (
            true_strain_mean[:, x_idx] + 2.0 * true_strain_mean[:, y_idx]
        ).reshape(experiment.image_count, 1)

        experiment.gauge_results = pd.DataFrame(
            data=np.concatenate(
                (
                    experiment.traverse_displ,
                    experiment.reaction_force,
                    true_strain_mean[:, x_idx].reshape((experiment.image_count, 1)),
                    true_strain_mean[:, y_idx].reshape((experiment.image_count, 1)),
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
        experiment.test_results_dir = os.path.join(
            istra_evaluation_dir, experiment.name + "CORN1"
        )
        experiment.gauge_results.to_csv(
            os.path.join(
                experiment.test_results_dir, experiment.name + "CORN1_gauge_results.csv"
            )
        )

        # export experiment data
        if passed_args.eco is True:
            experiment.slenderise()
        with open(
            os.path.join(
                experiment.test_results_dir, experiment.name + "CORN1_experiment_data.p"
            ),
            "wb",
        ) as myfile:
            dill.dump(experiment, myfile)
