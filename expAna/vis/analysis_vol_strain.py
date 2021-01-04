import os
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

    analysis = expAna.vis.analysis.Analysis(type="vol_strain")
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

    analysis.compute_data_vol_strain()

    ####################################################################################
    # EXPORT ANALYSIS
    ####################################################################################

    expAna.data_trans.export_analysis(
        analysis.dict,
        out_dir=vis_export_dir,
        out_filename=f"analysis_dict_{analysis.analysis.export_prefix}.pickle",
    )

    ####################################################################################
    # PLOT
    ####################################################################################
    # plot individual curves and averaged curves in one plot for each analysis value
    for compare_value in analysis.compare_values:
        # volume strain behaviour
        fig_2, axes_2 = expAna.vis.plot.style_vol_strain(
            x_lim=1.0,
            y_lim=1.5 * analysis.dict[compare_value]["max_vol_strain"],
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
                : len(analysis.dict[compare_value]["mean_vol_strain"])
            ],
            y_vals=analysis.dict[compare_value]["mean_vol_strain"],
            out_dir=vis_export_dir,
            out_filename=f"curve_avg_{analysis.export_prefix}_{export_value}.pickle",
        )

        expAna.vis.plot.add_curves_same_value(
            fig=fig_2,
            axes=axes_2,
            x_mean=analysis.dict[compare_value]["mean_strain"][
                : len(analysis.dict[compare_value]["mean_vol_strain"])
            ],
            y_mean=analysis.dict[compare_value]["mean_vol_strain"],
            xs=np.array(analysis.dict[compare_value]["strains"], dtype=object)[
                analysis.dict[compare_value]["vol_strain_indices"]
            ],
            ys=np.array(analysis.dict[compare_value]["vol_strains"], dtype=object)[
                analysis.dict[compare_value]["vol_strain_indices"]
            ],
            value=compare_value,
        )

        axes_2.legend(loc="upper left")

        fig_2.tight_layout()
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

        fig_2.set_size_inches(12, 9)
        fig_2.suptitle(
            f"{analysis.material}, {analysis.title_key}: {compare_value}", fontsize=12
        )
        fig_2.tight_layout()
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
        # volume strain behaviour
        fig_3, axes_3 = expAna.vis.plot.style_vol_strain(
            x_lim=1.0,
            y_lim=1.5 * analysis.dict[compare_value]["max_vol_strain"],
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
                : len(analysis.dict[compare_value]["sem_vol_strain"])
            ],
            y_vals=analysis.dict[compare_value]["sem_vol_strain"],
            out_dir=vis_export_dir,
            out_filename=f"curve_sem_{analysis.export_prefix}_{export_value}.pickle",
        )

        expAna.vis.plot.add_mean_and_sem(
            fig=fig_3,
            axes=axes_3,
            x_mean=analysis.dict[compare_value]["mean_strain"][
                : len(analysis.dict[compare_value]["mean_vol_strain"])
            ],
            y_mean=analysis.dict[compare_value]["mean_vol_strain"],
            y_error=1.96 * analysis.dict[compare_value]["sem_vol_strain"],
            value=compare_value,
        )

        axes_3.legend(loc="upper left")

        fig_3.tight_layout()
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

        fig_3.set_size_inches(12, 9)
        fig_3.suptitle(
            f"{analysis.material}, {analysis.title_key}: {compare_value}", fontsize=12
        )
        fig_3.tight_layout()
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
    max_vol_strain = max(
        analysis.dict[compare_value]["max_vol_strain"]
        for compare_value in analysis.compare_values
    )

    fig_4, axes_4 = expAna.vis.plot.style_vol_strain(
        x_lim=1.0,
        y_lim=1.5 * max_vol_strain,
        width=6,
        height=4,
    )

    for compare_value in analysis.compare_values:
        expAna.vis.plot.add_curves_same_value(
            fig=fig_4,
            axes=axes_4,
            x_mean=analysis.dict[compare_value]["mean_strain"][
                : len(analysis.dict[compare_value]["mean_vol_strain"])
            ],
            y_mean=analysis.dict[compare_value]["mean_vol_strain"],
            xs=np.array(analysis.dict[compare_value]["strains"], dtype=object)[
                analysis.dict[compare_value]["vol_strain_indices"]
            ],
            ys=np.array(analysis.dict[compare_value]["vol_strains"], dtype=object)[
                analysis.dict[compare_value]["vol_strain_indices"]
            ],
            value=compare_value,
        )

    axes_4.legend(loc="upper left")

    fig_4.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{analysis.export_prefix}_comparison.pgf",
        )
    )
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{analysis.export_prefix}_comparison_small.png",
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
            f"{analysis.export_prefix}_comparison_large.png",
        )
    )
    plt.close()

    ####################################################################################
    # comparison plot with mean and std curve
    fig_5, axes_5 = expAna.vis.plot.style_vol_strain(
        x_lim=1.0,
        y_lim=1.5 * max_vol_strain,
        width=6,
        height=4,
    )

    for compare_value in analysis.compare_values:
        expAna.vis.plot.add_mean_and_sem(
            fig=fig_5,
            axes=axes_5,
            x_mean=analysis.dict[compare_value]["mean_strain"][
                : len(analysis.dict[compare_value]["mean_vol_strain"])
            ],
            y_mean=analysis.dict[compare_value]["mean_vol_strain"],
            y_error=1.96 * analysis.dict[compare_value]["sem_vol_strain"],
            value=compare_value,
        )

    axes_5.legend(loc="upper left")

    fig_5.tight_layout()
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
    fig_5.set_size_inches(12, 9)
    fig_5.suptitle(
        f"{analysis.material}, comparison: {analysis.title_key}", fontsize=12
    )
    fig_5.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{analysis.export_prefix}_comparison_with_error_large.png",
        )
    )
    plt.close()
