import os
import sys
import argparse
import numpy as np
import matplotlib.pyplot as plt

import expAna
from expAna.misc import InputError


def main(
    compare,
    select=None,
    experiment_list=None,
    ignore_list=None,
    dic_system="istra",
):
    work_dir = os.getcwd()
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

    os.makedirs(vis_export_dir, exist_ok=True)

    analysis = expAna.vis.analysis.Analysis(type="stress")
    analysis.setup(
        exp_data_dir=exp_data_dir,
        compare=compare,
        select=select,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
    )
    ####################################################################################
    # COMPUTE AVERAGE CURVES, ETC.
    ####################################################################################

    analysis.compute_data_stress()

    ####################################################################################
    # EXPORT ANALYSIS
    ####################################################################################

    expAna.data_trans.export_analysis(
        analysis.dict,
        out_dir=vis_export_dir,
        out_filename=f"analysis_dict_{analysis.export_prefix}.pickle",
    )

    ####################################################################################
    # PLOT
    ####################################################################################
    # plot individual curves and averaged curves in one plot for each analysis value
    for compare_value in analysis.compare_values:
        # remove spaces in string before export
        if type(compare_value) == str:
            export_value = compare_value.replace(" ", "_")
        else:
            export_value = str(compare_value)

        expAna.data_trans.export_one_curve_as_df(
            x_vals=analysis.dict[compare_value]["mean_strain"][
                : len(analysis.dict[compare_value]["mean_stress"])
            ],
            y_vals=analysis.dict[compare_value]["mean_stress"],
            out_dir=vis_export_dir,
            out_filename=f"curve_avg_{analysis.export_prefix}_{export_value}.pickle",
        )

        # stress strain behaviour
        fig_1, axes_1 = expAna.vis.plot.style_true_stress(
            x_lim=1.0,
            y_lim=1.5 * analysis.dict[compare_value]["max_stress"],
            width=6,
            height=4,
        )

        expAna.vis.plot.add_curves_same_value(
            fig=fig_1,
            axes=axes_1,
            x_mean=analysis.dict[compare_value]["mean_strain"][
                : len(analysis.dict[compare_value]["mean_stress"])
            ],
            y_mean=analysis.dict[compare_value]["mean_stress"],
            xs=np.array(analysis.dict[compare_value]["strains"], dtype=object)[
                analysis.dict[compare_value]["stress_indices"]
            ],
            ys=np.array(analysis.dict[compare_value]["stresses"], dtype=object)[
                analysis.dict[compare_value]["stress_indices"]
            ],
            value=compare_value,
        )

        axes_1.legend(loc="upper left")

        fig_1.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{analysis.export_prefix}_{export_value}.pgf",
            )
        )
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{analysis.export_prefix}_{export_value}_small.png",
            )
        )

        fig_1.set_size_inches(12, 9)
        fig_1.suptitle(
            f"{analysis.material}, {analysis.title_key}: {compare_value}", fontsize=12
        )
        fig_1.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{analysis.export_prefix}_{export_value}_large.png",
            )
        )
        plt.close()
    ####################################################################################
    # plot mean and std curves in one plot for each "compare_value"
    for compare_value in analysis.compare_values:
        fig_2, axes_2 = expAna.vis.plot.style_true_stress(
            x_lim=1.0,
            y_lim=1.5 * analysis.dict[compare_value]["max_stress"],
            width=6,
            height=4,
        )

        # remove spaces in string before export
        if type(compare_value) == str:
            export_value = compare_value.replace(" ", "_")
        else:
            export_value = str(compare_value)

        expAna.data_trans.export_one_curve_as_df(
            x_vals=analysis.dict[compare_value]["mean_strain"][
                : len(analysis.dict[compare_value]["sem_stress"])
            ],
            y_vals=analysis.dict[compare_value]["sem_stress"],
            out_dir=vis_export_dir,
            out_filename=f"curve_sem_{analysis.export_prefix}_{export_value}.pickle",
        )

        expAna.vis.plot.add_mean_and_sem(
            fig=fig_2,
            axes=axes_2,
            x_mean=analysis.dict[compare_value]["mean_strain"][
                : len(analysis.dict[compare_value]["mean_stress"])
            ],
            y_mean=analysis.dict[compare_value]["mean_stress"],
            y_error=1.96 * analysis.dict[compare_value]["sem_stress"],
            value=compare_value,
        )

        axes_2.legend(loc="upper left")

        fig_2.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{analysis.export_prefix}_{export_value}_with_error.pgf",
            )
        )
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{analysis.export_prefix}_{export_value}_with_error_small.png",
            )
        )

        fig_2.set_size_inches(12, 9)
        fig_2.suptitle(
            f"{analysis.material}, {analysis.title_key}: {compare_value}", fontsize=12
        )
        fig_2.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{analysis.export_prefix}_{export_value}_with_error_large.png",
            )
        )
        plt.close()

    ####################################################################################
    # comparison plot with mean and individual curves

    # get maximum y value for upper y-axis limit
    max_stress = max(
        analysis.dict[compare_value]["max_stress"]
        for compare_value in analysis.compare_values
    )
    # comparison plot
    # stress strain behaviour
    fig_3, axes_3 = expAna.vis.plot.style_true_stress(
        x_lim=1.0,
        y_lim=1.5 * max_stress,
        width=6,
        height=4,
    )

    for compare_value in analysis.compare_values:
        expAna.vis.plot.add_curves_same_value(
            fig=fig_3,
            axes=axes_3,
            x_mean=analysis.dict[compare_value]["mean_strain"][
                : len(analysis.dict[compare_value]["mean_stress"])
            ],
            y_mean=analysis.dict[compare_value]["mean_stress"],
            xs=np.array(analysis.dict[compare_value]["strains"], dtype=object)[
                analysis.dict[compare_value]["stress_indices"]
            ],
            ys=np.array(analysis.dict[compare_value]["stresses"], dtype=object)[
                analysis.dict[compare_value]["stress_indices"]
            ],
            value=compare_value,
        )

    axes_3.legend(loc="upper left")

    fig_3.tight_layout()
    plt.savefig(
        os.path.join(vis_export_dir, f"{analysis.export_prefix}_comparison.pgf")
    )
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{analysis.export_prefix}_comparison_small.png",
        )
    )
    fig_3.set_size_inches(12, 9)
    fig_3.suptitle(
        f"{analysis.material}, comparison: {analysis.title_key}", fontsize=12
    )
    fig_3.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{analysis.export_prefix}_comparison_large.png",
        )
    )
    plt.close()

    ####################################################################################
    # comparison plot with mean and std curve
    fig_4, axes_4 = expAna.vis.plot.style_true_stress(
        x_lim=1.0,
        y_lim=1.5 * max_stress,
        width=6,
        height=4,
    )

    for compare_value in analysis.compare_values:
        expAna.vis.plot.add_mean_and_sem(
            fig=fig_4,
            axes=axes_4,
            x_mean=analysis.dict[compare_value]["mean_strain"][
                : len(analysis.dict[compare_value]["mean_stress"])
            ],
            y_mean=analysis.dict[compare_value]["mean_stress"],
            y_error=1.96 * analysis.dict[compare_value]["sem_stress"],
            value=compare_value,
        )

    axes_4.legend(loc="upper left")

    fig_4.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{analysis.export_prefix}_comparison_with_error.pgf",
        )
    )
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{analysis.export_prefix}_comparison_with_error_small.png",
        )
    )
    fig_4.set_size_inches(12, 9)
    fig_4.suptitle(
        f"{analysis.material}, comparison: {analysis.title_key}", fontsize=12
    )
    fig_4.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{analysis.export_prefix}_comparison_with_error_large.png",
        )
    )
    plt.close()

    expAna.data_trans.export_analysis(
        analysis.dict,
        out_dir=vis_export_dir,
        out_filename=f"analysis_dict_{analysis.export_prefix}.pickle",
    )


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="This utility makes plots of stress strain curves of experiment files in the corresponding directory filtered by a criterion."
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
            compare=passed_args.compare[0],
            select=passed_args.select,
            experiment_list=passed_args.experiments,
            ignore_list=passed_args.ignore,
            dic_system=passed_args.dic,
        )
    )
