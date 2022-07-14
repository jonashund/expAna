import os
import shutil
import pathlib

# remove created directories
shutil.rmtree(
    pathlib.Path(
        os.path.dirname(__file__), "..", "data", "test_analysis", "expAna_plots"
    )
)
