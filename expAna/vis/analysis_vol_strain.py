import os
import sys
import argparse
import dill
import numpy as np
import matplotlib.pyplot as plt

import expAna
from expAna.misc import InputError

from natsort import natsorted


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
    # calculate average curves for every "compare_value"
    for compare_value in analysis.compare_values:
        true_strains = []
        vol_strains = []
        # create list of arrays with x and y values
        for experiment_name in analysis.dict[compare_value]["experiment_list"]:
            true_strains.append(
                analysis.project.experiments[experiment_name]
                .gauge_results["true_strain_image_x"]
                .to_numpy()
            )
            vol_strains.append(
                analysis.project.experiments[experiment_name]
                .gauge_results["volume_strain"]
                .to_numpy()
            )

        # interpolate every curve to an x-axis with equally spaced points
        # set spacing dependent on maximum x-value found in all x arrays

        max_x = max([max(true_strains[i]) for i in range(len(true_strains))])
        interval = max_x / 500
        mean_strain = np.arange(start=0.0, stop=max_x, step=interval)
        for i, strain in enumerate(true_strains):
            true_strains[i], vol_strains[i] = expAna.calc.interpolate_curve(
                strain, vol_strains[i], interval
            )
        # compute the mean curve as long as at least three values are available
        (
            mean_vol_strain,
            sem_vol_strain,
            vol_strain_indices,
        ) = expAna.calc.get_mean_and_sem(vol_strains)

        analysis.dict[compare_value]["mean_strain"] = mean_strain
        analysis.dict[compare_value]["mean_vol_strain"] = mean_vol_strain
        analysis.dict[compare_value]["sem_vol_strain"] = sem_vol_strain
        analysis.dict[compare_value]["vol_strain_indices"] = vol_strain_indices
        analysis.dict[compare_value]["strains"] = true_strains
        analysis.dict[compare_value]["vol_strains"] = vol_strains

        analysis.dict[compare_value].update(
            {
                "max_vol_strain": np.array(vol_strains, dtype=object)[
                    vol_strain_indices
                ][-1].max()
            }
        )

    ####################################################################################
    # PREPARE FOR EXPORT
    ####################################################################################
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
            out_filename=f"curve_avg_{export_prefix}_{export_value}.pickle",
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
                f"{export_prefix}_{export_value}.pgf",
            )
        )
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_prefix}_{export_value}_small.png",
            )
        )

        fig_2.set_size_inches(12, 9)
        fig_2.suptitle(f"{material}, {title_key}: {compare_value}", fontsize=12)
        fig_2.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_prefix}_{export_value}_large.png",
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
            out_filename=f"curve_sem_{export_prefix}_{export_value}.pickle",
        )

        expAna.vis.plot.add_mean_and_sem(
            fig=fig_3,
            axes=axes_3,
            x_mean=analysis.dict[compare_value]["mean_strain"][
                : len(analysis.dict[compare_value]["mean_vol_strain"])
            ],
            y_mean=analysis.dict[compare_value]["mean_vol_strain"],
            y_sem=analysis.dict[compare_value]["sem_vol_strain"],
            value=compare_value,
        )

        axes_3.legend(loc="upper left")

        fig_3.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_prefix}_{export_value}_with_sem.pgf",
            )
        )
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_prefix}_{export_value}_with_sem_small.png",
            )
        )

        fig_3.set_size_inches(12, 9)
        fig_3.suptitle(f"{material}, {title_key}: {compare_value}", fontsize=12)
        fig_3.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir,
                f"{export_prefix}_{export_value}_with_sem_large.png",
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
            f"{export_prefix}_comparison.pgf",
        )
    )
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_prefix}_comparison_small.png",
        )
    )
    fig_4.set_size_inches(12, 9)
    fig_4.suptitle(f"{material}, comparison: {title_key}", fontsize=12)
    fig_4.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_prefix}_comparison_large.png",
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
            y_sem=analysis.dict[compare_value]["sem_vol_strain"],
            value=compare_value,
        )

    axes_5.legend(loc="upper left")

    fig_5.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_prefix}_comparison_with_sem.pgf",
        )
    )
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_prefix}_comparison_with_sem_small.png",
        )
    )
    fig_5.set_size_inches(12, 9)
    fig_5.suptitle(f"{material}, comparison: {title_key}", fontsize=12)
    fig_5.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_prefix}_comparison_with_sem_large.png",
        )
    )
    plt.close()

    ####################################################################################
    # EXPORT ANALYSIS
    ####################################################################################

    expAna.data_trans.export_analysis(
        analysis.dict,
        out_dir=vis_export_dir,
        out_filename=f"analysis_dict_{export_prefix}.pickle",
    )
    ####################################################################################
