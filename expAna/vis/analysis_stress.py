import os
import sys
import argparse
import dill
import numpy as np
import matplotlib.pyplot as plt

import expAna
from expAna.misc import InputError

from natsort import natsorted

work_dir = os.getcwd()


def main(
    filter_key,
    filter_value=None,
    experiment_list=None,
    ignore_list=None,
    dic_system="istra",
):
    if dic_system == "istra":
        exp_data_dir = os.path.join(work_dir, "data_istra_evaluation")
        vis_export_dir = os.path.join(work_dir, "visualisation", "istra")
    elif dic_system == "muDIC":
        exp_data_dir = os.path.join(work_dir, "data_muDIC")
        vis_export_dir = os.path.join(work_dir, "visualisation", "muDIC")
    else:
        raise InputError(
            "-dic", f"`{dic_system}` is not a valid value for argument `dic_system`"
        )

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

    analysis_dict = {}
    analysis_project = expAna.data_trans.Project(name=f"analysis_{filter_key}")

    # load the experiments
    for test_dir in experiment_list:
        with open(
            os.path.join(exp_data_dir, test_dir, test_dir + "_expAna.p"), "rb",
        ) as myfile:
            experiment = dill.load(myfile)

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
        true_strains = []
        true_stresses = []
        vol_strains = []
        # create list of arrays with x and y values
        for experiment_name in analysis_dict[filter_value]["experiment_list"]:
            true_strains.append(
                analysis_project.experiments[experiment_name]
                .gauge_results["true_strain_image_x"]
                .to_numpy()
            )
            true_stresses.append(
                analysis_project.experiments[experiment_name]
                .gauge_results["true_stress_in_MPa"]
                .to_numpy()
            )
            vol_strains.append(
                analysis_project.experiments[experiment_name]
                .gauge_results["volume_strain"]
                .to_numpy()
            )

        # mean_strain, mean_stress = expAna.calc.get_mean_curves(true_strains, true_stresses)
        # mean_strain, mean_vol_strain = expAna.calc.get_mean_curves(true_strains, vol_strains)

        # interpolate every stress strain curve to an x-axis with equally spaced points
        # set spacing dependent on maximum x-value found in all x arrays

        max_x = max([max(true_strains[i]) for i in range(len(true_strains))])
        interval = max_x / 500
        mean_strain = np.arange(start=0.0, stop=max_x, step=interval)
        for i, strain in enumerate(true_strains):
            true_strains[i], true_stresses[i] = expAna.calc.interpolate_curve(
                strain, true_stresses[i], interval
            )
            foo, vol_strains[i] = expAna.calc.interpolate_curve(
                strain, vol_strains[i], interval
            )
        # compute the mean curve as long as at least three values are available
        mean_stress, stress_indices = expAna.calc.mean_curve(true_stresses)
        mean_vol_strain, vol_strain_indices = expAna.calc.mean_curve(vol_strains)

        analysis_dict[filter_value]["mean_strain"] = mean_strain
        analysis_dict[filter_value]["mean_stress"] = mean_stress
        analysis_dict[filter_value]["stress_indices"] = stress_indices
        analysis_dict[filter_value]["mean_vol_strain"] = mean_vol_strain
        analysis_dict[filter_value]["vol_strain_indices"] = vol_strain_indices
        analysis_dict[filter_value]["strains"] = true_strains
        analysis_dict[filter_value]["stresses"] = true_stresses
        analysis_dict[filter_value]["vol_strains"] = vol_strains

        analysis_dict[filter_value].update(
            {
                "max_stress": np.array(true_stresses, dtype=object)[stress_indices][
                    -1
                ].max()
            }
        )
        analysis_dict[filter_value].update(
            {
                "max_vol_strain": np.array(vol_strains, dtype=object)[
                    vol_strain_indices
                ][-1].max()
            }
        )
    # some string replacement for underscores in filenames
    title_key = filter_key.replace("_", " ")
    material = analysis_project.experiments[experiment_name].documentation_data[
        "material"
    ]
    export_material = material.replace(" ", "_")

    # plot individual curves and averaged curves in one plot for each analysis value
    for filter_value in filter_values:
        # stress strain behaviour
        fig_1, axes_1 = expAna.vis.plot.style_true_stress(
            x_lim=1.0,
            y_lim=1.5 * analysis_dict[filter_value]["max_stress"],
            width=6,
            height=4,
        )

        expAna.vis.plot.add_curves_same_value(
            fig=fig_1,
            axes=axes_1,
            x_mean=analysis_dict[filter_value]["mean_strain"][
                : len(analysis_dict[filter_value]["mean_stress"])
            ],
            y_mean=analysis_dict[filter_value]["mean_stress"],
            xs=np.array(analysis_dict[filter_value]["strains"], dtype=object)[
                analysis_dict[filter_value]["stress_indices"]
            ],
            ys=np.array(analysis_dict[filter_value]["stresses"], dtype=object)[
                analysis_dict[filter_value]["stress_indices"]
            ],
            value=filter_value,
        )

        axes_1.legend(loc="upper left")

        # remove spaces in string before export
        export_value = filter_value.replace(" ", "_")

        fig_1.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_material}_stress_{filter_key}_{export_value}.pgf",
            )
        )
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_material}_stress_{filter_key}_{export_value}_small.png",
            )
        )

        fig_1.set_size_inches(12, 9)
        fig_1.suptitle(f"{material}, {title_key}: {filter_value}", fontsize=12)
        fig_1.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_material}_stress_{filter_key}_{export_value}_large.png",
            )
        )
        plt.close()

        # volume strain behaviour
        fig_2, axes_2 = expAna.vis.plot.style_vol_strain(
            x_lim=1.0,
            y_lim=1.5 * analysis_dict[filter_value]["max_vol_strain"],
            width=6,
            height=4,
        )

        expAna.vis.plot.add_curves_same_value(
            fig=fig_2,
            axes=axes_2,
            x_mean=analysis_dict[filter_value]["mean_strain"][
                : len(analysis_dict[filter_value]["mean_vol_strain"])
            ],
            y_mean=analysis_dict[filter_value]["mean_vol_strain"],
            xs=np.array(analysis_dict[filter_value]["strains"], dtype=object)[
                analysis_dict[filter_value]["vol_strain_indices"]
            ],
            ys=np.array(analysis_dict[filter_value]["vol_strains"], dtype=object)[
                analysis_dict[filter_value]["vol_strain_indices"]
            ],
            value=filter_value,
        )

        axes_2.legend(loc="upper left")

        # remove spaces in string before export
        export_value = filter_value.replace(" ", "_")

        fig_2.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_material}_vol_strain_{filter_key}_{export_value}.pgf",
            )
        )
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_material}_vol_strain_{filter_key}_{export_value}_small.png",
            )
        )

        fig_2.set_size_inches(12, 9)
        fig_2.suptitle(f"{material}, {title_key}: {filter_value}", fontsize=12)
        fig_2.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_material}_vol_strain_{filter_key}_{export_value}_large.png",
            )
        )
        plt.close()

    max_stress = max(
        analysis_dict[filter_value]["max_stress"] for filter_value in filter_values
    )
    max_vol_strain = max(
        analysis_dict[filter_value]["max_vol_strain"] for filter_value in filter_values
    )
    # comparison plot
    # stress strain behaviour
    fig_3, axes_3 = expAna.vis.plot.style_true_stress(
        x_lim=1.0, y_lim=1.5 * max_stress, width=6, height=4,
    )

    for filter_value in filter_values:
        expAna.vis.plot.add_curves_same_value(
            fig=fig_3,
            axes=axes_3,
            x_mean=analysis_dict[filter_value]["mean_strain"][
                : len(analysis_dict[filter_value]["mean_stress"])
            ],
            y_mean=analysis_dict[filter_value]["mean_stress"],
            xs=np.array(analysis_dict[filter_value]["strains"], dtype=object)[
                analysis_dict[filter_value]["stress_indices"]
            ],
            ys=np.array(analysis_dict[filter_value]["stresses"], dtype=object)[
                analysis_dict[filter_value]["stress_indices"]
            ],
            value=filter_value,
        )

    axes_3.legend(loc="upper left")

    fig_3.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir, f"{export_material}_stress_{filter_key}_comparison.pgf"
        )
    )
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_material}_stress_{filter_key}_comparison_small.png",
        )
    )
    fig_3.set_size_inches(12, 9)
    fig_3.suptitle(f"{material}, comparison: {title_key}", fontsize=12)
    fig_3.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_material}_stress_{filter_key}_comparison_large.png",
        )
    )
    plt.close()

    # volume strain behaviour
    fig_4, axes_4 = expAna.vis.plot.style_vol_strain(
        x_lim=1.0, y_lim=1.5 * max_vol_strain, width=6, height=4,
    )

    for filter_value in filter_values:
        expAna.vis.plot.add_curves_same_value(
            fig=fig_4,
            axes=axes_4,
            x_mean=analysis_dict[filter_value]["mean_strain"][
                : len(analysis_dict[filter_value]["mean_vol_strain"])
            ],
            y_mean=analysis_dict[filter_value]["mean_vol_strain"],
            xs=np.array(analysis_dict[filter_value]["strains"], dtype=object)[
                analysis_dict[filter_value]["vol_strain_indices"]
            ],
            ys=np.array(analysis_dict[filter_value]["vol_strains"], dtype=object)[
                analysis_dict[filter_value]["vol_strain_indices"]
            ],
            value=filter_value,
        )

    axes_4.legend(loc="upper left")

    fig_4.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir, f"{export_material}_vol_strain_{filter_key}_comparison.pgf",
        )
    )
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_material}_vol_strain_{filter_key}_comparison_small.png",
        )
    )
    fig_4.set_size_inches(12, 9)
    fig_4.suptitle(f"{material}, comparison: {title_key}", fontsize=12)
    fig_4.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_material}_vol_strain_{filter_key}_comparison_large.png",
        )
    )
    plt.close()


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="This utility makes plots of stress strain and volume strain curves of experiment files in the corresponding directory filtered by a criterion."
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

    arg_parser.add_argument(
        "-d",
        "--dic",
        default="istra",
        help="Specify DIC software with which the results were obtained. Options: `istra` (default) or `muDIC`.",
    )

    # TO DO: add -t, --type (simple_tension, sent)

    passed_args = arg_parser.parse_args()
    sys.exit(
        main(
            filter_key=passed_args.key[0],
            filter_value=passed_args.value,
            experiment_list=passed_args.experiments,
            ignore_list=passed_args.ignore,
            dic_system=passed_args.dic,
        )
    )
