import os
import pathlib
import shutil
import expAna

project_name = "test_core"

# copy tex directory for documentation
from_dir = pathlib.Path(os.path.dirname(__file__), "..", "docu_templates", "tex")
to_dir = pathlib.Path(os.path.dirname(__file__), "..", "data", "test_core", "tex")
shutil.copytree(from_dir, to_dir)

# Run expDoc for documentation purposes from the ./tex directory
docu_dir = pathlib.Path(os.path.dirname(__file__), "..", "data", "test_core", "tex")
os.chdir(docu_dir)
expAna.docu.main(project_name, skip_tex=True)
os.chdir("..")

# Stress computation
expAna.eval2stress.main(tensile_direction="x", avg_coords=[101, 47, 121, 75])
# Basic visualisation of the results for checking and spotting errors
# Stress-strain curves for each experiment and DIC system used
expAna.review.stress(skip_tex=True)
# Force-displacement curves for each experiment and DIC system used
expAna.review.force(skip_tex=True)
# Plot of the DIC deformation field as an overlay on the raw image data
expAna.plot.dic_strains(
    experiment_name="Test8",
    displacement=1,
    strain_component="x",
    max_triang_len=50,
    skip_tex=True,
)
