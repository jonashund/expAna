import os
import sys
import argparse
import dill
import numpy as np
import matplotlib.pyplot as plt

import expAna

from natsort import natsorted


def main(
    filter_key,
    filter_value=None,
    experiment_list=None,
    ignore_list=None,
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

    if ignore_list is not None:
        for experiment in ignore_list:
            experiment_list.remove(experiment)

    experiment_list = natsorted(experiment_list)

    analysis_dict = {}
    analysis_project = expAna.data_trans.Project(name=f"analysis_{filter_key}")

    # read the experiment files
    for test_dir in experiment_list:
        # search for input data created with expDoc
        try:
            with open(
                os.path.join(expDoc_data_dir, test_dir + "_expDoc.pkl"),
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
        # search for expAna data
        try:
            with open(
                os.path.join(vis_export_dir, test_dir + "_expAna.p"),
                "rb",
            ) as myfile:
                experiment = dill.load(myfile)
        except:
            pass

        analysis_project.add_experiment(experiment)

    # compile list of different values for key or just filter experiments for given key
    if filter_value is None:
        filter_values = []
        for experiment_name, experiment_data in analysis_project.experiments.items():
            filter_values.append(experiment_data.documentation_data[filter_key])
        # remove experiments with no value for given key
        filter_values = list(filter(None, filter_values))
        for filter_value in set(filter_values):
            value_count = filter_values.count(filter_value)
            if value_count < 3:
                for i in range(value_count):
                    filter_values.remove(filter_value)
            else:
                pass
        # remove duplicates from list
        filter_values = set(filter_values)
    else:
        filter_values = [filter_value[0]]

    for filter_value in filter_values:
        analysis_dict[filter_value] = {}
        analysis_dict[filter_value]["experiment_list"] = []
        for experiment_name, experiment_data in analysis_project.experiments.items():
            if experiment_data.documentation_data[filter_key] == filter_value:
                analysis_dict[filter_value]["experiment_list"].append(experiment_name)

    # expAna.calculate average curves for every filter_value
    for filter_value in filter_values:
        displacements = []
        forces = []
        # create list of arrays with x and y values
        for experiment_name in analysis_dict[filter_value]["experiment_list"]:
            displacements.append(
                analysis_project.experiments[experiment_name]
                .data_instron["displacement_in_mm"]
                .to_numpy()
            )
            forces.append(
                analysis_project.experiments[experiment_name]
                .data_instron["force_in_kN"]
                .to_numpy()
            )

        # interpolate every force displacement curve to an x-axis with equally spaced points
        # set spacing dependent on maximum x-value found in all x arrays

        max_x = max([max(displacements[i]) for i in range(len(displacements))])
        interval = max_x / 500
        mean_disp = np.arange(start=0.0, stop=max_x, step=interval)
        for i, strain in enumerate(displacements):
            displacements[i], forces[i] = expAna.calc.interpolate_curve(
                strain, forces[i], interval
            )

        # compute the mean curve as long as at least three values are available
        mean_force, force_indices = expAna.calc.mean_curve(forces)

        analysis_dict[filter_value]["mean_disp"] = mean_disp
        analysis_dict[filter_value]["mean_force"] = mean_force
        analysis_dict[filter_value]["force_indices"] = force_indices
        analysis_dict[filter_value]["displacements"] = displacements
        analysis_dict[filter_value]["forces"] = forces

        analysis_dict[filter_value].update(
            {"max_force": np.array(forces, dtype=object)[force_indices][-1].max()}
        )
    # some string replacement for underscores in filenames
    title_key = filter_key.replace("_", " ")
    material = analysis_project.experiments[experiment_name].documentation_data[
        "material"
    ]
    export_material = material.replace(" ", "_")

    # plot individual curves and averaged curves in one plot for each analysis value
    for filter_value in filter_values:
        fig_1, axes_1 = expAna.vis.plot.style_force_disp(
            x_lim=5.0,
            y_lim=1.5 * analysis_dict[filter_value]["max_force"],
            width=6,
            height=4,
        )

        expAna.vis.plot.add_curves_same_value(
            fig=fig_1,
            axes=axes_1,
            x_mean=analysis_dict[filter_value]["mean_disp"][
                : len(analysis_dict[filter_value]["mean_force"])
            ],
            y_mean=analysis_dict[filter_value]["mean_force"],
            xs=np.array(analysis_dict[filter_value]["displacements"], dtype=object)[
                analysis_dict[filter_value]["force_indices"]
            ],
            ys=np.array(analysis_dict[filter_value]["forces"], dtype=object)[
                analysis_dict[filter_value]["force_indices"]
            ],
            value=filter_value,
        )

        axes_1.legend(loc="upper left")

        # remove spaces in string before export
        if type(filter_value) == str:
            export_value = filter_value.replace(" ", "_")
        else:
            export_value = str(filter_value)

        fig_1.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_material}_force_disp_{filter_key}_{export_value}.pgf",
            )
        )
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_material}_force_disp_{filter_key}_{export_value}_small.png",
            )
        )

        fig_1.set_size_inches(12, 9)
        fig_1.suptitle(f"{material}, {title_key}: {filter_value}", fontsize=12)
        fig_1.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_material}_force_disp_{filter_key}_{export_value}_large.png",
            )
        )
        plt.close()

    # comparison plot
    max_force = max(
        analysis_dict[filter_value]["max_force"] for filter_value in filter_values
    )
    fig_3, axes_3 = expAna.vis.plot.style_force_disp(
        x_lim=5.0,
        y_lim=1.5 * max_force,
        width=6,
        height=4,
    )

    for filter_value in filter_values:
        expAna.vis.plot.add_curves_same_value(
            fig=fig_3,
            axes=axes_3,
            x_mean=analysis_dict[filter_value]["mean_disp"][
                : len(analysis_dict[filter_value]["mean_force"])
            ],
            y_mean=analysis_dict[filter_value]["mean_force"],
            xs=np.array(analysis_dict[filter_value]["displacements"], dtype=object)[
                analysis_dict[filter_value]["force_indices"]
            ],
            ys=np.array(analysis_dict[filter_value]["forces"], dtype=object)[
                analysis_dict[filter_value]["force_indices"]
            ],
            value=filter_value,
        )

    axes_3.legend(loc="upper left")

    fig_3.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir, f"{export_material}_force_disp_{filter_key}_comparison.pgf"
        )
    )
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_material}_force_disp_{filter_key}_comparison_small.png",
        )
    )
    fig_3.set_size_inches(12, 9)
    fig_3.suptitle(f"{material}, comparison: {title_key}", fontsize=12)
    fig_3.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_material}_force_disp_{filter_key}_comparison_large.png",
        )
    )
    plt.close()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="This utility force displacement curves of experiment files in the corresponding directory filtered by a criterion."
    )
    arg_parser.add_argument(
        "-e",
        "--experiments",
        nargs="*",
        default=None,
        help="Include specified experiments in analysis., e.g. Test1CORN1 TEST9CORN1",
    )

    arg_parser.add_argument(
        "-i",
        "--ignore",
        nargs="*",
        default=None,
        help="Ignore experiments specified in analysis, e.g. Test5CORN1",
    )

    #   - selection feature (string) experiment.documentation_data[<key>], i.e. experiment.documentation_data["specimen_orientation"]
    arg_parser.add_argument(
        "-k",
        "--key",
        metavar="experiment.documentation_data[<key>]",
        required=True,
        nargs=1,
        type=str,
        help="Dictionary key of dictionary experiment.documentation_data.",
    )

    #   - selection criterion (string) value (or part of value) of experiment.documentation_data[<key>]
    arg_parser.add_argument(
        "-v",
        "--value",
        metavar="experiment.documentation_data[`key`]: <value>",
        nargs=1,
        default=None,
        help="Value for given --key argument of dictionary experiment.documentation_data.",
    )

    #   - plot original curves (boolean)
    # arg_parser.add_argument(
    #     "-a",
    #     "--all",
    #     metavar="plot_all_curves",
    #     type=bool,
    #     nargs=1,
    #     default=True,
    #     help="If `True` all curves are plotted as opposed to only the averaged curves if `False`.",
    # )

    passed_args = arg_parser.parse_args()
    sys.exit(
        main(
            filter_key=passed_args.key[0],
            filter_value=passed_args.value,
            experiment_list=passed_args.experiments,
            ignore_list=passed_args.ignore,
        )
    )
