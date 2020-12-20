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
):
    work_dir = os.getcwd()
    expDoc_data_dir = os.path.join(work_dir, "data_expDoc", "python")
    istra_acquisition_dir = os.path.join(work_dir, "data_istra_acquisition")
    istra_evaluation_dir = os.path.join(work_dir, "data_istra_evaluation")

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
                os.path.join(expDoc_data_dir, test_dir + "_expDoc.pickle"),
                "rb",
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

        direction_selector = expAna.gui.TensileDirection(experiment.ref_image)
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
        true_strain = expAna.gauge.get_true_strain(experiment.def_grad)
        true_strain[:, :, :, :][experiment.mask[:, :, :, 0] == 0] = np.nan

        strain_gauge = expAna.gui.RectangleCoordinates(
            input_image=true_strain[int(0.8 * experiment.image_count), :, :, x_idx]
        )
        strain_gauge.__gui__()

        [x_min, y_min, x_max, y_max] = [int(i) for i in strain_gauge.coordinates]

        # image coordinates assume x-axis horizontal (i.e. columns)
        # and y-axis vertical (i.e. rows)
        true_strain_gauge = true_strain[:, y_min:y_max, x_min:x_max, :]

        true_strain_mean = np.nanmean(true_strain_gauge, axis=(1, 2))

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
        test_results_dir = os.path.join(istra_evaluation_dir, experiment.name + "CORN1")
        experiment.gauge_results.to_csv(
            os.path.join(test_results_dir, experiment.name + "CORN1_gauge_results.csv")
        )

        # export experiment data
        if eco_mode is True:
            experiment.slenderise()
        with open(
            os.path.join(test_results_dir, experiment.name + "CORN1_expAna.pickle"),
            "wb",
        ) as myfile:
            dill.dump(experiment, myfile)


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="eval2stress offers `gauge` element functionality based on Python. From Istra4D evaluation files the true stress strain and volume strain behaviour is computed over a defined part of the whole DIC image."
    )
    arg_parser.add_argument(
        "-e",
        "--experiments",
        nargs="*",
        default=None,
        help="experiment folder name(s) located in ../data_istra_acquisition/",
    )

    arg_parser.add_argument(
        "-i",
        "--ignore",
        nargs="*",
        default=None,
        help="experiment folder name(s) to ignore",
    )

    #   - selection criterion (string) value (or part of value) of experiment.documentation_data[<key>]
    arg_parser.add_argument(
        "-s",
        "--select",
        metavar="experiment.documentation_data[`key`]: <value>",
        nargs=2,
        default=None,
        help="List [key, value] from experiment.documentation_data.",
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

    arg_parser.add_argument(
        "--use-poissons_ratio",
        default=True,
        help="Use the specified Poisson's ratio for the through thickness direction instead of the assumption of equal in-plane and through-thickness Poisson's ratios.",
    )

    arg_parser.add_argument(
        "--poissons_ratio",
        default=None,
        help="Through-thickness Poisson's ratio.",
    )

    passed_args = arg_parser.parse_args()

    sys.exit(
        main(
            select=passed_args.select,
            experiment_list=passed_args.experiments,
            ignore_list=passed_args.ignore,
            eco_mode=passed_args.eco,
            specimen_width=passed_args.geometry[0],
            specimen_thickness=passed_args.geometry[0],
            use_poissons_ratio=passed_args.use_poissons_ratio,
            poissons_ratio_through_thickness=passed_args.poissons_ratio,
        )
    )
