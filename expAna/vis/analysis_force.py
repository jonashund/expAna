import os
import sys
import argparse
import dill
import numpy as np
import matplotlib.pyplot as plt

import expAna

from natsort import natsorted


def main(compare, select=None, experiment_list=None, ignore_list=None, x_lim=5.0):

    work_dir = os.getcwd()
    expDoc_data_dir = os.path.join(work_dir, "data_expDoc", "python")
    instron_data_dir = os.path.join(work_dir, "data_instron")
    vis_export_dir = os.path.join(work_dir, "visualisation")

    os.makedirs(vis_export_dir, exist_ok=True)

    analysis = expAna.vis.analysis.Analysis(type="force")
    analysis.setup(
        exp_data_dir=exp_data_dir,
        compare=compare,
        select=select,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
    )

    # expAna.calculate average curves for every compare_value
    for compare_value in analysis.compare_values:
        displacements = []
        forces = []
        # create list of arrays with x and y values
        for experiment_name in analysis.dict[compare_value]["experiment_list"]:
            displacements.append(
                analysis.project.experiments[experiment_name]
                .data_instron["displacement_in_mm"]
                .to_numpy()
            )
            forces.append(
                analysis.project.experiments[experiment_name]
                .data_instron["force_in_kN"]
                .to_numpy()
            )

        # TO DO:
        # for each experiment
        # get index of last positive value in "force_in_kN"
        # cut "displacement_in_mm" and "force_in_kN" at this index
        # WHY:
        # do not plot curves after specimen failure

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

        analysis.dict[compare_value]["mean_disp"] = mean_disp
        analysis.dict[compare_value]["mean_force"] = mean_force
        analysis.dict[compare_value]["force_indices"] = force_indices
        analysis.dict[compare_value]["displacements"] = displacements
        analysis.dict[compare_value]["forces"] = forces

        analysis.dict[compare_value].update(
            {"max_force": np.array(forces, dtype=object)[force_indices][-1].max()}
        )
    # some string replacement for underscores in filenames
    title_key = compare.replace("_", " ")
    material = analysis.project.experiments[
        list(analysis.project.experiments.keys())[0]
    ].documentation_data["material"]
    export_material = material.replace(" ", "_")

    if select is None:
        export_prefix = f"{export_material}_{analysis.type}_{compare}"
    else:
        export_prefix = f"{export_material}_{analysis.type}_{analysis.select_key}_{analysis.select_value}_{compare}"

    # plot individual curves and averaged curves in one plot for each analysis value

    for compare_value in analysis.compare_values:
        # remove spaces in string before export
        if type(compare_value) == str:
            export_value = compare_value.replace(" ", "_")
        else:
            export_value = str(compare_value)

        expAna.data_trans.export_one_curve_as_df(
            x_vals=analysis.dict[compare_value]["mean_disp"][
                : len(analysis.dict[compare_value]["mean_force"])
            ],
            y_vals=analysis.dict[compare_value]["mean_force"],
            out_dir=vis_export_dir,
            out_filename=f"curve_avg_{export_prefix}_{export_value}.pickle",
        )

        fig_1, axes_1 = expAna.vis.plot.style_force_displ(
            x_lim=x_lim,
            y_lim=1.5 * analysis.dict[compare_value]["max_force"],
            width=6,
            height=4,
        )

        expAna.vis.plot.add_curves_same_value(
            fig=fig_1,
            axes=axes_1,
            x_mean=analysis.dict[compare_value]["mean_disp"][
                : len(analysis.dict[compare_value]["mean_force"])
            ],
            y_mean=analysis.dict[compare_value]["mean_force"],
            xs=np.array(analysis.dict[compare_value]["displacements"], dtype=object)[
                analysis.dict[compare_value]["force_indices"]
            ],
            ys=np.array(analysis.dict[compare_value]["forces"], dtype=object)[
                analysis.dict[compare_value]["force_indices"]
            ],
            value=compare_value,
        )
        axes_1.legend(loc="upper left")

        fig_1.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_prefix}_{export_value}.pgf",
            )
        )
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_prefix}_{export_value}_small.png",
            )
        )

        fig_1.set_size_inches(12, 9)
        fig_1.suptitle(f"{material}, {title_key}: {compare_value}", fontsize=12)
        fig_1.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_prefix}_{export_value}_large.png",
            )
        )
        plt.close()

    # comparison plot
    max_force = max(
        analysis.dict[compare_value]["max_force"]
        for compare_value in analysis.compare_values
    )
    fig_3, axes_3 = expAna.vis.plot.style_force_displ(
        x_lim=x_lim,
        y_lim=1.5 * max_force,
        width=6,
        height=4,
    )

    for compare_value in analysis.compare_values:
        expAna.vis.plot.add_curves_same_value(
            fig=fig_3,
            axes=axes_3,
            x_mean=analysis.dict[compare_value]["mean_disp"][
                : len(analysis.dict[compare_value]["mean_force"])
            ],
            y_mean=analysis.dict[compare_value]["mean_force"],
            xs=np.array(analysis.dict[compare_value]["displacements"], dtype=object)[
                analysis.dict[compare_value]["force_indices"]
            ],
            ys=np.array(analysis.dict[compare_value]["forces"], dtype=object)[
                analysis.dict[compare_value]["force_indices"]
            ],
            value=compare_value,
        )

    axes_3.legend(loc="upper left")

    fig_3.tight_layout()
    plt.savefig(os.path.join(vis_export_dir, f"{export_prefix}_comparison.pgf"))
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_prefix}_comparison_small.png",
        )
    )
    fig_3.set_size_inches(12, 9)
    fig_3.suptitle(f"{material}, comparison: {title_key}", fontsize=12)
    fig_3.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_prefix}_comparison_large.png",
        )
    )
    plt.close()

    expAna.data_trans.export_analysis(
        analysis.dict,
        out_dir=vis_export_dir,
        out_filename=f"analysis.dict_{export_prefix}.pickle",
    )


# TO DO: write function that writes whole analysis.dict to file for visualisation purposes
# filename should include information on:
#       - material
#       - type of data (stress, vol_strain, force, poissons_ratio)
#       - filter_key

# TO DO: write import function for this kind of exported data


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="This utility makes plots of force displacement curves of experiment files in the corresponding directory filtered by a criterion."
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
        "-c",
        "--compare",
        metavar="experiment.documentation_data[<key>]",
        required=True,
        nargs=1,
        type=str,
        help="Dictionary key of dictionary experiment.documentation_data.",
    )

    #   - selection criterion (string) value (or part of value) of experiment.documentation_data[<key>]
    arg_parser.add_argument(
        "-s",
        "--select",
        metavar="experiment.documentation_data[`key`]: <value>",
        nargs=2,
        default=None,
        help="List [key, value] from experiment.documentation_data.",
    )

    passed_args = arg_parser.parse_args()
    sys.exit(
        main(
            compare=passed_args.compare[0],
            select=passed_args.select,
            experiment_list=passed_args.experiments,
            ignore_list=passed_args.ignore,
            x_lim=passed_args.x_lim,
        )
    )
