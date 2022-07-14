import os
import sys
import argparse
import dill
import numpy as np
import pandas as pd

import expAna

from natsort import natsorted


def main(
    select=None,
    experiment_list=None,
    ignore_list=None,
    eco_mode=True,
    specimen_width=12.0,
    specimen_thickness=3.0,
    use_poissons_ratio=False,
    poissons_ratio_through_thickness=0.35,
    tensile_direction=None,
    avg_coords=None,
):
    work_dir = os.getcwd()
    expAna_docu_dir = os.path.join(work_dir, "expAna_docu", "python")
    expAna_data_dir = os.path.join(work_dir, "expAna_data")
    istra_acquisition_dir = os.path.join(work_dir, "data_istra_acquisition")
    istra_evaluation_dir = os.path.join(work_dir, "data_istra_evaluation")

    os.makedirs(expAna_data_dir, exist_ok=True)

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

    if ignore_list is not None:
        for experiment in ignore_list:
            experiment_list.remove(experiment)

    experiment_list = natsorted(experiment_list)

    for test_dir in experiment_list:
        # load or create experiment object
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
            Document your experiments properly using the expDoc package.
            """
            )

        if select is not None:
            if str(experiment.documentation_data[select[0]]) == str(select[1]):
                pass
            else:
                continue
        else:
            pass

        experiment.read_istra_evaluation(istra_acquisition_dir, istra_evaluation_dir)

        if tensile_direction is None:
            direction_selector = expAna.gui.TensileDirection(experiment.ref_image)
            direction_selector.__gui__()
            experiment.tensile_direction = direction_selector.direction
        else:
            experiment.tensile_direction = tensile_direction

        if experiment.tensile_direction == "x":
            x_idx = 0
            y_idx = 1
        else:
            x_idx = 1
            y_idx = 0

        # get strains from evaluation
        # pixel gradients are treated as elements of the deformation gradient
        true_strain = expAna.gauge.get_true_strain(experiment.def_grad)
        true_strain[:, :, :, :][experiment.mask[:, :, :, 0] == 0] = np.nan

        if avg_coords is None:
            strain_gauge = expAna.gui.RectangleCoordinates(
                input_image_x_strain=true_strain[
                    int(0.8 * experiment.image_count), :, :, x_idx
                ],
                input_image_y_strain=true_strain[
                    int(0.8 * experiment.image_count), :, :, y_idx
                ],
            )
            strain_gauge.__gui__()

            [x_min, y_min, x_max, y_max] = [int(i) for i in strain_gauge.coordinates]
        else:
            [x_min, y_min, x_max, y_max] = avg_coords

        # image coordinates assume x-axis horizontal (i.e. columns)
        # and y-axis vertical (i.e. rows)
        true_strain_gauge = true_strain[:, y_min:y_max, x_min:x_max, :]

        true_strain_mean = np.nanmean(true_strain_gauge, axis=(1, 2))

        if specimen_thickness is None:
            specimen_thickness = experiment.documentation_data["specimen_thickness"]
        else:
            pass
        if specimen_width is None:
            specimen_width = experiment.documentation_data["specimen_width"]
        else:
            pass

        if use_poissons_ratio is True:
            true_stress_in_MPa = expAna.gauge.get_true_stress_2(
                force_in_N=experiment.reaction_force * 1000.0,
                true_strain_parallel=true_strain_mean[:, x_idx].reshape(
                    (experiment.image_count, 1)
                ),
                true_strain_perpendicular=true_strain_mean[:, y_idx].reshape(
                    (experiment.image_count, 1)
                ),
                poissons_ratio_through_thickness=poissons_ratio_through_thickness,
                specimen_cross_section_in_mm2=specimen_width * specimen_thickness,
            )
            volume_strain = (
                (1.0 - poissons_ratio_through_thickness) * true_strain_mean[:, x_idx]
                + true_strain_mean[:, y_idx]
            ).reshape(experiment.image_count, 1)
        else:
            true_stress_in_MPa = expAna.gauge.get_true_stress(
                force_in_N=experiment.reaction_force * 1000.0,
                true_strain_perpendicular=true_strain_mean[:, y_idx].reshape(
                    (experiment.image_count, 1)
                ),
                specimen_cross_section_in_mm2=specimen_width * specimen_thickness,
            )
            volume_strain = (
                true_strain_mean[:, x_idx] + 2.0 * true_strain_mean[:, y_idx]
            ).reshape(experiment.image_count, 1)

        poissons_ratio = np.vstack(
            [
                np.array([0.0]),
                (-true_strain_mean[1:, y_idx] / true_strain_mean[1:, x_idx]).reshape(
                    experiment.image_count - 1, 1
                ),
            ]
        )

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

        # test_results_dir = os.path.join(istra_evaluation_dir, experiment.name + "CORN1")
        experiment.gauge_results.to_csv(
            os.path.join(expAna_data_dir, experiment.name + "CORN1_gauge_results.csv")
        )

        # export experiment data
        if eco_mode is True:
            experiment.slenderise()
        with open(
            os.path.join(expAna_data_dir, experiment.name + "CORN1_expAna.pickle"),
            "wb",
        ) as myfile:
            dill.dump(experiment, myfile)


def update_true_stress(
    select=None, experiment_list=None, ignore_list=None, update_reviewed=True
):

    """
    function with the purpose to update true stress values after thickness or width have been updated in documentation_data
    """

    work_dir = os.getcwd()
    expAna_docu_dir = os.path.join(work_dir, "expAna_docu", "python")
    expAna_data_dir = os.path.join(work_dir, "expAna_data")
    istra_evaluation_dir = os.path.join(work_dir, "data_istra_evaluation")
    vis_export_dir = os.path.join(work_dir, "expAna_plots", "istra")

    if experiment_list is None:
        experiment_list = list()
        print(
            f"No experiment names passed. Will search for folders named `Test*CORN1` in {istra_evaluation_dir}."
        )
        for path, directories, files in os.walk(istra_evaluation_dir):
            for test_dir in directories:
                if str(test_dir[:5] == "Test"):
                    experiment_list.append(test_dir[:-5])
    else:
        pass

    if ignore_list is not None:
        for experiment in ignore_list:
            experiment_list.remove(experiment)

    experiment_list = natsorted(experiment_list)

    for test_dir in experiment_list:
        # load documentation data with updated information
        with open(
            os.path.join(expAna_docu_dir, test_dir + "_docu.pickle"), "rb",
        ) as myfile:
            expAna_docu = dill.load(myfile)

        with open(
            os.path.join(expAna_data_dir, test_dir + "CORN1_expAna.pickle",), "rb",
        ) as myfile:
            exp_eval = dill.load(myfile)

        if select is not None:
            if str(expAna_docu.documentation_data[select[0]]) == str(select[1]):
                pass
            else:
                continue
        else:
            pass

        # replace outdated documentation_data of exp_eval
        exp_eval.documentation_data = expAna_docu.documentation_data

        # with strain gauge data from gauge results recalculate true stress
        true_stress_in_MPa = expAna.gauge.get_true_stress(
            force_in_N=exp_eval.gauge_results["reaction_force_in_kN"] * 1000.0,
            true_strain_perpendicular=exp_eval.gauge_results["true_strain_image_y"],
            specimen_cross_section_in_mm2=exp_eval.documentation_data["specimen_width"]
            * exp_eval.documentation_data["specimen_thickness"],
        )
        exp_eval.gauge_results.update({"true_stress_in_MPa": true_stress_in_MPa})

        # export updated data
        # test_results_dir = os.path.join(istra_evaluation_dir, exp_eval.name + "CORN1")
        exp_eval.gauge_results.to_csv(
            os.path.join(expAna_data_dir, exp_eval.name + "CORN1_gauge_results.csv")
        )

        with open(
            os.path.join(expAna_data_dir, exp_eval.name + "CORN1_expAna.pickle"), "wb",
        ) as myfile:
            dill.dump(exp_eval, myfile)

        exp_eval.plot_true_stress(out_dir=vis_export_dir)
        exp_eval.plot_volume_strain(out_dir=vis_export_dir)
