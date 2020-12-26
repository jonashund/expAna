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
    compare,
    select=None,
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

    os.makedirs(vis_export_dir, exist_ok=True)

    analysis = expAna.vis.analysis.Analysis(type="vol_strain")
    analysis.setup(
        exp_data_dir=exp_data_dir,
        compare=compare,
        select=select,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
    )

    # expAna.calculate average curves for every compare_value
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
        mean_vol_strain, vol_strain_indices = expAna.calc.mean_curve(vol_strains)

        analysis.dict[compare_value]["mean_strain"] = mean_strain
        analysis.dict[compare_value]["mean_vol_strain"] = mean_vol_strain
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

    max_vol_strain = max(
        analysis.dict[compare_value]["max_vol_strain"]
        for compare_value in analysis.compare_values
    )
    # comparison plot
    # volume strain behaviour
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

    expAna.data_trans.export_analysis(
        analysis.dict,
        out_dir=vis_export_dir,
        out_filename=f"analysis_dict_{export_prefix}.pickle",
    )


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(
        description="This utility makes plots of volume strain curves of experiment files in the corresponding directory filtered by a criterion."
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
