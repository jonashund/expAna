import os
import pathlib
import expDoc
import expAna

project_name = "test_core"

# Run expDoc for documentation purposes from the ./tex directory
expDoc_dir = pathlib.Path(os.path.dirname(__file__), "..", "data", "test_core", "tex")
os.chdir(expDoc_dir)
expDoc.main.main(project_name)
os.chdir("..")

# Stress computation
expAna.eval2stress.main(tensile_direction="x", avg_coords=[101, 47, 121, 75])
# Basic visualisation of the results for checking and spotting errors
# Stress-strain curves for each experiment and DIC system used
expAna.review.stress()
# Force-displacement curves for each experiment and DIC system used
expAna.review.force()
# Plot of the DIC deformation field as an overlay on the raw image data
expAna.plot.dic_strains(
    experiment_name="Test8", displacement=1, strain_component="x", max_triang_len=50
)
