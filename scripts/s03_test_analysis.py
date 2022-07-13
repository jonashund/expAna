import os
import expDoc
import expAna
import pathlib

os.chdir(pathlib.Path(os.path.dirname(__file__), "..", "data", "test_analysis"))

# Previously,projects have been created, stresses have been computated, and curves have been clipped.
# Create an analysis object of type "stress":
my_analysis = expAna.analysis.Analysis("stress")
# Setup the analysis by selecting all experiments on PC/ABS 45/55 carried out using a crosshead speed of 0.1 mm/s and compare them regarding the impact of different specimen orientations
my_analysis.setup(
    exp_data_dir="./data_istra_evaluation",
    compare="specimen_orientation",
    select=["crosshead_speed", 0.1],
    ignore_list=["Test16CORN1", "Test13CORN1"],
)
# Perform the actual analysis
my_analysis.compute_data_stress()
# Visualise the results in a basic plot
os.makedirs("./visualisation", exist_ok=True)
my_analysis.plot_data(vis_export_dir="./visualisation")
# Export the results to a .pickle file
expAna.data_trans.export_analysis(
    my_analysis, out_filename=f"analysis_{my_analysis.export_prefix}.pickle",
)
