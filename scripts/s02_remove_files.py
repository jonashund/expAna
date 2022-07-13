import os
import shutil
import pathlib

# remove created directories
shutil.rmtree(
    pathlib.Path(os.path.dirname(__file__), "..", "data", "test_core", "data_expDoc")
)
shutil.rmtree(
    pathlib.Path(os.path.dirname(__file__), "..", "data", "test_core", "visualisation")
)
os.remove(
    pathlib.Path(
        os.path.dirname(__file__),
        "..",
        "data",
        "test_core",
        "data_istra_evaluation",
        "Test8CORN1",
        "Test8CORN1_expAna.pickle",
    )
)
os.remove(
    pathlib.Path(
        os.path.dirname(__file__),
        "..",
        "data",
        "test_core",
        "data_istra_evaluation",
        "Test8CORN1",
        "Test8CORN1_gauge_results.csv",
    )
)

