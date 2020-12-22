import os
import sys
import argparse
import dill

import expAna

from natsort import natsorted


def main(
    select=None,
    experiment_list=None,
    displ_shift=None,
    set_failure=False,
):

    work_dir = os.getcwd()
    expDoc_data_dir = os.path.join(work_dir, "data_expDoc", "python")
    instron_data_dir = os.path.join(work_dir, "data_instron")
    vis_export_dir = os.path.join(work_dir, "visualisation")
    os.makedirs(vis_export_dir, exist_ok=True)

    if experiment_list is None:
        experiment_list = list()
        print(
            f"No experiments passed. Will search for folders named `Test*` in {instron_data_dir}."
        )
        for path, directories, files in os.walk(instron_data_dir):
            for test_dir in directories:
                if str(test_dir[:5] == "Test"):
                    experiment_list.append(test_dir)
    else:
        pass

    experiment_list = natsorted(experiment_list)

    for test_dir in experiment_list:
        # search for input data created with expDoc
        try:
            with open(
                os.path.join(expDoc_data_dir, test_dir + "_expDoc.pickle"),
                "rb",
            ) as myfile:
                experiment = dill.load(myfile)
        except:
            print(
                f"""
            Warning:
            No documentation data found for {test_dir}!
            Document your experiments properly using expDoc before using expAna.
            """
            )
            assert False

        if select is not None:
            if str(experiment.documentation_data[select[0]]) == str(select[1]):
                pass
            else:
                continue
        else:
            pass

        # search for expAna data
        try:
            with open(
                os.path.join(vis_export_dir, test_dir + "_expAna.pickle"),
                "rb",
            ) as myfile:
                experiment = dill.load(myfile)
        except:
            with open(
                os.path.join(vis_export_dir, test_dir + "_expAna.pickle"),
                "wb",
            ) as myfile:
                dill.dump(experiment, myfile)

        if displ_shift is not None:
            experiment.data_instron = expAna.vis.plot.shift_columns(
                experiment.data_instron, "displacement_in_mm", displ_shift
            )
            # export truncated data
            with open(
                os.path.join(vis_export_dir, test_dir + "_expAna.pickle"),
                "wb",
            ) as myfile:
                dill.dump(experiment, myfile)
        else:
            pass

        if set_failure:
            fail_location = expAna.gui.FailureLocator()
            fail_location.__gui__(experiment)
            # export truncated data
            with open(
                os.path.join(vis_export_dir, test_dir + "_expAna.pickle"),
                "wb",
            ) as myfile:
                dill.dump(experiment, myfile)
        else:
            pass

        # expAna.vis.plot.set_plt_backend()

    for test_dir in experiment_list:
        with open(
            os.path.join(vis_export_dir, test_dir + "_expAna.pickle"),
            "rb",
        ) as myfile:
            experiment = dill.load(myfile)

        experiment.plot_force_disp(out_dir=vis_export_dir)
