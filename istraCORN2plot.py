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
dic_results_dir = os.path.join(filepath, "..", "data_istra_evaluation")
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

test_dict = {}

for test_dir in experiment_list:
    # create experiment object
    current_test = funcs.Experiment(name=test_dir)
    current_test.read_istra_data(istra_acquisition_dir, dic_results_dir)

    exit()

    direction_selector = gauge_funcs.TensileDirection(experiment.ref_image)
    direction_selector.__gui__()
    experiment.tensile_direction = direction_selector.direction

    test_dict.update({current_test.name: current_test})
    if experiment.tensile_direction == "x":
        x_idx = 0
        y_idx = 1
    else:
        x_idx = 1
        y_idx = 0

# get array with strains in y and y directions for all frames
# istra_strains[frame_id, x_id, y_id, strain_id]
# strain_id: 0=xx, 1=yy, 2=xy
# istra4D uses Langrangian strains [mm/m] for normal strains
lagrange_strain = current_test.eps[:, :, :, 0:2] / 1000
lagrange_strain[:, :, :, :][istra_reader.export.mask[:, :, :, 0] is False] = np.nan

# convert to logarithmic strains
# true_strain = 1/2 * log(2 * lagrange_strains + 1)
true_strain = 1.0 / 2.0 * np.log(2.0 * lagrange_strain + 1.0)

gauge = gauge_funcs.RectangleCoordinates(input_image=log_strains[9, :, :, 0])
mask.__gui__()

[x_min, y_min, x_max, y_max] = [int(i) for i in gauge.coordinates]

# image coordinates assume x-axis horizontal (i.e. columns)
# and y-axis vertical (i.e. rows)
true_strain_gauge = log_strain[:, y_min:y_max, x_min:x_max, :]

true_strain_mean = np.nanmean(true_strain_gauge, axis=(1, 2))

specimen_width = 12.0  # mm
specimen_thickness = 3.0  # mm

tensile_direction_in_image_cos = "y"

true_stress_in_MPa = funcs.get_true_stress(
    force_in_N=current_test.reaction_force * 1000.0,
    log_strain_perpendicular=log_strains_mean[:, 0].reshape((10, 1)),
    specimen_cross_section_in_mm2=specimen_width * specimen_thickness,
)

# poissons_ratio = -log_strains_perpendicular/log_strains_tensile

dataframe = pd.DataFrame(
    data=np.concatenate(
        (
            self.traverse_displ,
            current_test.reaction_force,
            log_strains_mean[:, 0].reshape((10, 1)),
            log_strains_mean[:, 1].reshape((10, 1)),
            true_stress_in_MPa,
            # poissons_ratio,
            # volume_strain
        ),
        axis=1,
    ),
    columns=[
        "displ_in_mm",
        "reaction_force_in_kN",
        "log_strain_image_x",
        "log_strain_image_y",
        "true_stress_in_MPa",
    ],
)
