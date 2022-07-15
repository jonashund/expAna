import os
import dill

import expAna
from expAna.misc import InputError

from natsort import natsorted


def stress(
    select=None,
    experiment_list=None,
    ignore_list=None,
    keep_offset=True,
    set_failure=False,
    dic_system="istra",
    skip_tex=False,
):
    work_dir = os.getcwd()

    if dic_system == "istra":
        expAna_data_dir = os.path.join(work_dir, "expAna_data")
        exp_data_dir = os.path.join(work_dir, "data_istra_evaluation")
        vis_export_dir = os.path.join(work_dir, "expAna_plots", "istra")
    elif dic_system == "muDIC":
        expAna_data_dir = os.path.join(work_dir, "expAna_data")
        exp_data_dir = os.path.join(work_dir, "data_muDIC")
        vis_export_dir = os.path.join(work_dir, "expAna_plots", "muDIC")
    else:
        raise InputError(
            "-dic", f"`{dic_system}` is not a valid value for argument `-dic`"
        )

    os.makedirs(vis_export_dir, exist_ok=True)

    if experiment_list is None:
        experiment_list = list()
        print(
            f"No experiments passed. Will search for folders named `Test*` in {exp_data_dir}."
        )
        for path, directories, files in os.walk(exp_data_dir):
            for test_dir in directories:
                if str(test_dir[:5] == "Test"):
                    experiment_list.append(test_dir)
    else:
        pass

    if ignore_list is not None:
        for experiment in ignore_list:
            experiment_list.remove(experiment)

    experiment_list = natsorted(experiment_list)

    # prepare plotting to file
    for test_dir in experiment_list:
        with open(
            os.path.join(expAna_data_dir, test_dir + "_expAna.pickle"), "rb",
        ) as myfile:
            experiment = dill.load(myfile)

        if select is not None:
            if str(experiment.documentation_data[select[0]]) == str(select[1]):
                pass
            else:
                continue
        else:
            pass

        if not keep_offset:
            expAna.plot.remove_offsets(experiment, row_threshold=0.015)
        else:
            pass

        if set_failure:
            fail_location = expAna.gui.FailureLocatorStress()
            fail_location.__gui__(experiment)
            # export truncated data
            with open(
                os.path.join(expAna_data_dir, test_dir + "_expAna.pickle"), "wb",
            ) as myfile:
                dill.dump(experiment, myfile)
        else:
            pass

    for test_dir in experiment_list:
        with open(
            os.path.join(expAna_data_dir, test_dir + "_expAna.pickle"), "rb",
        ) as myfile:
            experiment = dill.load(myfile)

        experiment.plot_true_stress(out_dir=vis_export_dir, skip_tex=skip_tex)
        experiment.plot_volume_strain(out_dir=vis_export_dir, skip_tex=skip_tex)


def force(
    select=None,
    experiment_list=None,
    ignore_list=None,
    displ_shift=None,
    set_failure=False,
    skip_tex=False,
):
    work_dir = os.getcwd()
    expAna_docu_dir = os.path.join(work_dir, "expAna_docu", "python")
    expAna_data_dir = os.path.join(work_dir, "expAna_data")
    instron_data_dir = os.path.join(work_dir, "data_instron")
    vis_export_dir = os.path.join(work_dir, "expAna_plots")

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
                os.path.join(expAna_docu_dir, test_dir + "_docu.pickle"), "rb",
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

        if ignore_list is not None:
            if str(experiment.name) in ignore_list:
                pass
            else:
                continue
        else:
            pass

        # search for expAna data
        try:
            with open(
                os.path.join(expAna_data_dir, test_dir + "_expAna.pickle"), "rb",
            ) as myfile:
                experiment = dill.load(myfile)
        except:
            with open(
                os.path.join(expAna_data_dir, test_dir + "_expAna.pickle"), "wb",
            ) as myfile:
                dill.dump(experiment, myfile)

        if displ_shift is not None:
            experiment.data_instron = expAna.plot.shift_columns(
                experiment.data_instron, "displacement_in_mm", displ_shift
            )
            # export truncated data
            with open(
                os.path.join(expAna_data_dir, test_dir + "_expAna.pickle"), "wb",
            ) as myfile:
                dill.dump(experiment, myfile)
        else:
            pass

        if set_failure:
            fail_location = expAna.gui.FailureLocatorForce()
            fail_location.__gui__(experiment)
            # export truncated data
            with open(
                os.path.join(expAna_data_dir, test_dir + "_expAna.pickle"), "wb",
            ) as myfile:
                dill.dump(experiment, myfile)
        else:
            pass

    for test_dir in experiment_list:
        with open(
            os.path.join(expAna_data_dir, test_dir + "_expAna.pickle"), "rb",
        ) as myfile:
            experiment = dill.load(myfile)

        if select is not None:
            if str(experiment.documentation_data[select[0]]) == str(select[1]):
                pass
            else:
                continue
        else:
            pass

        experiment.plot_force_displ(out_dir=vis_export_dir, skip_tex=skip_tex)

