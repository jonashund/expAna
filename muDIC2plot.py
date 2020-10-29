import os
import sys
import dill
import numpy as np
import pandas as pd
import gauge_funcs
import plot_funcs

filepath = os.path.abspath(os.path.dirname(__file__))

dic_results_dir = os.path.join(filepath, "..", "data_muDIC")
vis_export_dir = os.path.join(filepath, "..", "visualisation_muDIC")

for path, directories, files in os.walk(dic_results_dir):
    for test_dir in directories:
        if str("Test" in test_dir):
            with open(
                os.path.join(dic_results_dir, test_dir, test_dir + "_true_strain.npy"),
                "rb",
            ) as myfile:
                true_strain = np.load(myfile)
            with open(
                os.path.join(
                    dic_results_dir, test_dir, test_dir + "_experiment_data.p"
                ),
                "rb",
            ) as myfile:
                experiment = dill.load(myfile)

            direction_selector = gauge_funcs.TensileDirection(experiment.ref_image)
            direction_selector.__gui__()
            experiment.tensile_direction = direction_selector.direction

            if experiment.tensile_direction == "x":
                x_idx = 0
                y_idx = 1
            else:
                x_idx = 1
                y_idx = 0

            true_strain_x = true_strain[0, x_idx, x_idx, :, :, :]
            plot_frame = int(0.9 * experiment.img_count)

            mask = gauge_funcs.RectangleCoordinates(
                input_image=true_strain_x[:, :, plot_frame]
            )
            mask.__gui__()

            [x_min, y_min, x_max, y_max] = [int(i) for i in mask.coordinates]

            # image coordinates assume x-axis horizontal (i.e. columns)
            # and y-axis vertical (i.e. rows)
            true_strain_gauge = true_strain[0, y_min:y_max, x_min:x_max, :]

            true_strain_mean = np.nanmean(true_strain_gauge, axis=(2, 3))
            displacement_in_mm = experiment.traverse_displ
            reaction_force_in_kN = experiment.reaction_force

            specimen_width = 12.0  # mm
            specimen_thickness = 3.0  # mm

            true_stress_in_MPa = gauge_funcs.get_true_stress(
                force_in_N=reaction_force_in_kN * 1000.0,
                log_strain_perpendicular=true_strain_mean[y_idx, y_idx, :].reshape(
                    (experiment.img_count, 1)
                ),
                specimen_cross_section_in_mm2=specimen_width * specimen_thickness,
            )

            poissons_ratio = np.vstack(
                [
                    np.array([0.0]),
                    (
                        -true_strain_mean[y_idx, y_idx, 1:]
                        / true_strain_mean[x_idx, x_idx, 1:]
                    ).reshape(experiment.img_count - 1, 1),
                ]
            )

            volume_strain = (
                true_strain_mean[x_idx, x_idx, :]
                + 2.0 * true_strain_mean[y_idx, y_idx, :]
            ).reshape(experiment.img_count, 1)

            experiment.gauge_results = pd.DataFrame(
                data=np.concatenate(
                    (
                        displacement_in_mm,
                        reaction_force_in_kN,
                        true_strain_mean[x_idx, x_idx, :].reshape(
                            (experiment.img_count, 1)
                        ),
                        true_strain_mean[y_idx, y_idx, :].reshape(
                            (experiment.img_count, 1)
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
                    "log_strain_image_x",
                    "log_strain_image_y",
                    "true_stress_in_MPa",
                    "poissons_ratio",
                    "volume_strain",
                ],
            )
            # export dataframe with results as .csv
            experiment.gauge_results.to_csv(
                os.path.join(
                    experiment.test_results_dir, experiment.name + "_gauge_results.csv"
                )
            )

            # export experiment data
            with open(
                os.path.join(
                    experiment.test_results_dir, experiment.name + "_experiment_data.p"
                ),
                "wb",
            ) as myfile:
                dill.dump(experiment, myfile)

            # plot results to file
            plot_funcs.plot_true_stress_strain(
                experiment=experiment, out_dir=vis_export_dir
            )
            plot_funcs.plot_volume_strain(experiment=experiment, out_dir=vis_export_dir)
