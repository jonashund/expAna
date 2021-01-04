import os
import numpy as np
import matplotlib.pyplot as plt

import expAna


def main(
    compare,
    select=None,
    experiment_list=None,
    ignore_list=None,
    x_lim=None,
    displ_shift=None,
):

    work_dir = os.getcwd()
    instron_data_dir = os.path.join(work_dir, "data_instron")
    vis_export_dir = os.path.join(work_dir, "visualisation")

    os.makedirs(vis_export_dir, exist_ok=True)

    analysis = expAna.vis.analysis.Analysis(type="force")
    analysis.setup(
        exp_data_dir=instron_data_dir,
        compare=compare,
        select=select,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
    )
    ####################################################################################
    # COMPUTE AVERAGE CURVES, ETC.
    ####################################################################################

    analysis.compute_data_force(displ_shift)

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
            x_vals=analysis.dict[compare_value]["mean_displ"][
                : len(analysis.dict[compare_value]["mean_force"])
            ],
            y_vals=analysis.dict[compare_value]["mean_force"],
            out_dir=vis_export_dir,
            out_filename=f"curve_avg_{analysis.export_prefix}_{export_value}.pickle",
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
            x_mean=analysis.dict[compare_value]["mean_displ"][
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
    # plot mean and CI curves in one plot for each "compare_value"
    for compare_value in analysis.compare_values:
        # remove spaces in string before export
        if type(compare_value) == str:
            export_value = compare_value.replace(" ", "_")
        else:
            export_value = str(compare_value)

        expAna.data_trans.export_one_curve_as_df(
            x_vals=analysis.dict[compare_value]["mean_displ"][
                : len(analysis.dict[compare_value]["sem_force"])
            ],
            y_vals=analysis.dict[compare_value]["sem_force"],
            out_dir=vis_export_dir,
            out_filename=f"curve_sem_{analysis.export_prefix}_{export_value}.pickle",
        )

        fig_2, axes_2 = expAna.vis.plot.style_force_displ(
            x_lim=x_lim,
            y_lim=1.5 * analysis.dict[compare_value]["max_force"],
            width=6,
            height=4,
        )

        expAna.vis.plot.add_mean_and_sem(
            fig=fig_2,
            axes=axes_2,
            x_mean=analysis.dict[compare_value]["mean_displ"][
                : len(analysis.dict[compare_value]["mean_force"])
            ],
            y_mean=analysis.dict[compare_value]["mean_force"],
            y_error=1.96 * analysis.dict[compare_value]["sem_force"],
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
            x_mean=analysis.dict[compare_value]["mean_displ"][
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

    expAna.data_trans.export_analysis(
        analysis.dict,
        out_dir=vis_export_dir,
        out_filename=f"analysis_dict_{analysis.export_prefix}.pickle",
    )

    ####################################################################################
    # comparison plot with mean and std curve

    fig_4, axes_4 = expAna.vis.plot.style_force_displ(
        x_lim=x_lim,
        y_lim=1.5 * max_force,
        width=6,
        height=4,
    )

    for compare_value in analysis.compare_values:
        expAna.vis.plot.add_mean_and_sem(
            fig=fig_4,
            axes=axes_4,
            x_mean=analysis.dict[compare_value]["mean_displ"][
                : len(analysis.dict[compare_value]["mean_force"])
            ],
            y_mean=analysis.dict[compare_value]["mean_force"],
            y_error=1.96 * analysis.dict[compare_value]["sem_force"],
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
