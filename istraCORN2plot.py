import os
import numpy as np
import pandas as pd
import istra2py
import gauge_funcs as funcs

export2tif_dir = os.path.join(filepath, "..", "data_export2tif")

istra_reader = istra2py.Reader(
    path_dir_acquisition=os.path.join("data", "acquisition"),
    path_dir_export=os.path.join("data", "export"),
    verbose=True,
)

istra_reader.read(identify_images_export=True)

# get array with strains in y and y directions for all frames
# istra_strains[frame_id, x_id, y_id, strain_id]
# i=0: xx, i=1: yy, i=2: xy
# istra4D uses Langrangian strains [mm/m]
lagrange_strains = istra_reader.export.eps[:, :, :, 0:2] / 1000
lagrange_strains[:, :, :, :][istra_reader.export.mask[:, :, :, 0] == False] = np.nan

# convert to logarithmic strains
# log_strains = 1/2 * log(2 * lagrange_strains + 1)
log_strains = 1.0 / 2.0 * np.log(2.0 * lagrange_strains + 1.0)

mask = funcs.RectangleCoordinates(input_image=log_strains[9, :, :, 0])
mask.__gui__()

[x_min, y_min, x_max, y_max] = [int(i) for i in mask.coordinates]

# image coordinates assume x-axis horizontal (i.e. columns)
# and y-axis vertical (i.e. rows)
log_strains_gauge = log_strains[:, y_min:y_max, x_min:x_max, :]

log_strains_mean = np.nanmean(log_strains_gauge, axis=(1, 2))
displacement_in_mm = istra_reader.acquisition.traverse_displ * 10.0
reaction_force_in_kN = istra_reader.acquisition.traverse_force

specimen_width = 12.0  # mm
specimen_thickness = 3.0  # mm

tensile_direction_in_image_cos = "y"

true_stress_in_MPa = funcs.get_true_stress(
    force_in_N=reaction_force_in_kN * 1000.0,
    log_strain_perpendicular=log_strains_mean[:, 0].reshape((10, 1)),
    specimen_cross_section_in_mm2=specimen_width * specimen_thickness,
)

# poissons_ratio = -log_strains_perpendicular/log_strains_tensile

dataframe = pd.DataFrame(
    data=np.concatenate(
        (
            displacement_in_mm,
            reaction_force_in_kN,
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
