import os
import shutil
import pathlib

# remove created directories
shutil.rmtree(
    pathlib.Path(os.path.dirname(__file__), "..", "data", "test_core", "expAna_data")
)
shutil.rmtree(
    pathlib.Path(os.path.dirname(__file__), "..", "data", "test_core", "expAna_docu")
)
shutil.rmtree(
    pathlib.Path(os.path.dirname(__file__), "..", "data", "test_core", "expAna_plots")
)
shutil.rmtree(pathlib.Path(os.path.dirname(__file__), "..", "data", "test_core", "tex"))
