import os
import sys
import argparse
import dill
import numpy as np
import pandas as pd
import gui_funcs
import plot_funcs
import istra2muDIC_functions as funcs
import utils
import matplotlib.pyplot as plt

from natsort import natsorted

filepath = os.path.abspath(os.path.dirname(__file__))

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
arg_parser.add_argument(
    "-a",
    "--all",
    metavar="plot_all_curves",
    type=bool,
    nargs=1,
    default=True,
    help="If `True` all curves are plotted as opposed to only the averaged curves if `False`.",
)

arg_parser.add_argument(
    "-d",
    "--dic",
    default="istra",
    help="Specify DIC software with which the results were obtained. Options: `istra` (default) or `muDIC`.",
)

passed_args = arg_parser.parse_args()

if passed_args.dic == "istra":
    exp_data_dir = os.path.join(filepath, "..", "data_istra_evaluation")
    vis_export_dir = os.path.join(filepath, "..", "visualisation_istra")
elif passed_args.dic == "muDIC":
    exp_data_dir = os.path.join(filepath, "..", "data_muDIC")
    vis_export_dir = os.path.join(filepath, "..", "visualisation_muDIC")
else:
    raise InputError(
        "-dic", f"`{passed_args.dic}` is not a valid value for argument `-dic`"
    )

if passed_args.experiments is None:
    experiment_list = list()
    print(
        f"No experiments passed. Will search for folders named `Test*` in {exp_data_dir}."
    )
    for path, directories, files in os.walk(exp_data_dir):
        for test_dir in directories:
            if str(test_dir[:5] == "Test"):
                experiment_list.append(test_dir)
else:
    experiment_list = passed_args.experiments

if not passed_args.ignore is None:
    for experiment in passed_args.ignore:
        experiment_list.remove(experiment)

# get the list of experiments that are part of the analysis
experiment_list = natsorted(experiment_list)


# load all experiments and count the different values for given key
# compile a list of different values for given key
# create a dictionary that has every found value as key and a list of experiments with that value as list
# calculate the averages for each value
# plot average result for one value in a separate plot
# plot average results for all values in a plot
analysis_key = passed_args.key[0]
analysis_dict = {}
analysis_project = funcs.Project(name=f"analysis_{analysis_key}")

# load the experiments
for test_dir in experiment_list:
    with open(
        os.path.join(exp_data_dir, test_dir, test_dir + "_experiment_data.p"), "rb",
    ) as myfile:
        experiment = dill.load(myfile)

        analysis_project.add_experiment(experiment)

# compile list of different values for key or just filter experiments for given key
if passed_args.value is None:
    analysis_values = []
    for experiment_name, experiment_data in analysis_project.experiments.items():
        analysis_values.append(experiment_data.documentation_data[analysis_key])
    # remove experiments with no value for given key
    analysis_values = list(filter(None, analysis_values))
    # remove duplicates from list
    analysis_values = set(analysis_values)
else:
    analysis_values = [analysis_value[0]]

for analysis_value in analysis_values:
    analysis_dict[analysis_value] = {}
    analysis_dict[analysis_value]["experiment_list"] = []
    for experiment_name, experiment_data in analysis_project.experiments.items():
        if experiment_data.documentation_data[analysis_key] == analysis_value:
            analysis_dict[analysis_value]["experiment_list"].append(experiment_name)

# calculate average curves for every analysis_value
for analysis_value in analysis_values:
    true_strains = []
    true_stresses = []
    vol_strains = []
    # create list of arrays with x and y values
    for experiment_name in analysis_dict[analysis_value]["experiment_list"]:
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

    # mean_strain, mean_stress = utils.get_mean_curves(true_strains, true_stresses)
    # mean_strain, mean_vol_strain = utils.get_mean_curves(true_strains, vol_strains)

    # interpolate every stress strain curve to an x-axis with equally spaced points
    # set spacing dependent on maximum x-value found in all x arrays

    max_x = max([max(true_strains[i]) for i in range(len(true_strains))])
    interval = max_x / 500
    mean_strain = np.arange(start=0.0, stop=max_x, step=interval)
    for i, strain in enumerate(true_strains):
        true_strains[i], true_stresses[i] = utils.interpolate_curve(
            strain, true_stresses[i], interval
        )
        foo, vol_strains[i] = utils.interpolate_curve(strain, vol_strains[i], interval)
    # compute the mean curve as long as at least three values are available
    mean_stress, stress_indices = utils.get_mean_axis(true_stresses)
    mean_vol_strain, vol_strain_indices = utils.get_mean_axis(vol_strains)

    analysis_dict[analysis_value]["mean_strain"] = mean_strain
    analysis_dict[analysis_value]["mean_stress"] = mean_stress
    analysis_dict[analysis_value]["stress_indices"] = stress_indices
    analysis_dict[analysis_value]["mean_vol_strain"] = mean_vol_strain
    analysis_dict[analysis_value]["vol_strain_indices"] = vol_strain_indices
    analysis_dict[analysis_value]["strains"] = true_strains
    analysis_dict[analysis_value]["stresses"] = true_stresses
    analysis_dict[analysis_value]["vol_strains"] = vol_strains

    analysis_dict[analysis_value].update(
        {"max_stress": np.array(true_stresses, dtype=object)[stress_indices][-1].max()}
    )
    analysis_dict[analysis_value].update(
        {
            "max_vol_strain": np.array(vol_strains, dtype=object)[vol_strain_indices][
                -1
            ].max()
        }
    )
# some string replacement for underscores in filenames
title_key = analysis_key.replace("_", " ")
material = analysis_project.experiments[experiment_name].documentation_data["material"]
export_material = material.replace(" ", "_")

# plot individual curves and averaged curves in one plot for each analysis value
for analysis_value in analysis_values:
    # stress strain behaviour
    fig_1, axes_1 = plot_funcs.style_true_stress(
        x_lim=1.0,
        y_lim=1.5 * analysis_dict[analysis_value]["max_stress"],
        width=6,
        height=4,
    )

    plot_funcs.add_curves_same_value(
        fig=fig_1,
        axes=axes_1,
        x_mean=analysis_dict[analysis_value]["mean_strain"][
            : len(analysis_dict[analysis_value]["mean_stress"])
        ],
        y_mean=analysis_dict[analysis_value]["mean_stress"],
        xs=np.array(analysis_dict[analysis_value]["strains"], dtype=object)[
            analysis_dict[analysis_value]["stress_indices"]
        ],
        ys=np.array(analysis_dict[analysis_value]["stresses"], dtype=object)[
            analysis_dict[analysis_value]["stress_indices"]
        ],
        value=analysis_value,
    )

    axes_1.legend(loc="upper left")

    # remove spaces in string before export
    export_value = analysis_value.replace(" ", "_")

    fig_1.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_material}_stress_{analysis_key}_{export_value}.pgf",
        )
    )
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_material}_stress_{analysis_key}_{export_value}_small.png",
        )
    )

    fig_1.set_size_inches(12, 9)
    fig_1.suptitle(f"{material}, {title_key}: {analysis_value}", fontsize=12)
    fig_1.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_material}_stress_{analysis_key}_{export_value}_large.png",
        )
    )
    plt.close()

    # volume strain behaviour
    fig_2, axes_2 = plot_funcs.style_vol_strain(
        x_lim=1.0,
        y_lim=1.5 * analysis_dict[analysis_value]["max_vol_strain"],
        width=6,
        height=4,
    )

    plot_funcs.add_curves_same_value(
        fig=fig_2,
        axes=axes_2,
        x_mean=analysis_dict[analysis_value]["mean_strain"][
            : len(analysis_dict[analysis_value]["mean_vol_strain"])
        ],
        y_mean=analysis_dict[analysis_value]["mean_vol_strain"],
        xs=np.array(analysis_dict[analysis_value]["strains"], dtype=object)[
            analysis_dict[analysis_value]["vol_strain_indices"]
        ],
        ys=np.array(analysis_dict[analysis_value]["vol_strains"], dtype=object)[
            analysis_dict[analysis_value]["vol_strain_indices"]
        ],
        value=analysis_value,
    )

    axes_2.legend(loc="upper left")

    # remove spaces in string before export
    export_value = analysis_value.replace(" ", "_")

    fig_2.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_material}_vol_strain_{analysis_key}_{export_value}.pgf",
        )
    )
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_material}_vol_strain_{analysis_key}_{export_value}_small.png",
        )
    )

    fig_2.set_size_inches(12, 9)
    fig_2.suptitle(f"{material}, {title_key}: {analysis_value}", fontsize=12)
    fig_2.tight_layout()
    plt.savefig(
        os.path.join(
            vis_export_dir,
            f"{export_material}_vol_strain_{analysis_key}_{export_value}_large.png",
        )
    )
    plt.close()

max_stress = max(
    analysis_dict[analysis_value]["max_stress"] for analysis_value in analysis_values
)
max_vol_strain = max(
    analysis_dict[analysis_value]["max_vol_strain"]
    for analysis_value in analysis_values
)
# comparison plot
# stress strain behaviour
fig_3, axes_3 = plot_funcs.style_true_stress(
    x_lim=1.0, y_lim=1.5 * max_stress, width=6, height=4,
)

for analysis_value in analysis_values:
    plot_funcs.add_curves_same_value(
        fig=fig_3,
        axes=axes_3,
        x_mean=analysis_dict[analysis_value]["mean_strain"][
            : len(analysis_dict[analysis_value]["mean_stress"])
        ],
        y_mean=analysis_dict[analysis_value]["mean_stress"],
        xs=np.array(analysis_dict[analysis_value]["strains"], dtype=object)[
            analysis_dict[analysis_value]["stress_indices"]
        ],
        ys=np.array(analysis_dict[analysis_value]["stresses"], dtype=object)[
            analysis_dict[analysis_value]["stress_indices"]
        ],
        value=analysis_value,
    )

axes_3.legend(loc="upper left")

fig_3.tight_layout()
plt.savefig(
    os.path.join(
        vis_export_dir, f"{export_material}_stress_{analysis_key}_comparison.pgf"
    )
)
plt.savefig(
    os.path.join(
        vis_export_dir, f"{export_material}_stress_{analysis_key}_comparison_small.png"
    )
)
fig_3.set_size_inches(12, 9)
fig_3.suptitle(f"{material}, comparison: {analysis_key}", fontsize=12)
fig_3.tight_layout()
plt.savefig(
    os.path.join(
        vis_export_dir, f"{export_material}_stress_{analysis_key}_comparison_large.png"
    )
)
plt.close()

# volume strain behaviour
fig_4, axes_4 = plot_funcs.style_vol_strain(
    x_lim=1.0, y_lim=1.5 * max_vol_strain, width=6, height=4,
)

for analysis_value in analysis_values:
    plot_funcs.add_curves_same_value(
        fig=fig_4,
        axes=axes_4,
        x_mean=analysis_dict[analysis_value]["mean_strain"][
            : len(analysis_dict[analysis_value]["mean_vol_strain"])
        ],
        y_mean=analysis_dict[analysis_value]["mean_vol_strain"],
        xs=np.array(analysis_dict[analysis_value]["strains"], dtype=object)[
            analysis_dict[analysis_value]["vol_strain_indices"]
        ],
        ys=np.array(analysis_dict[analysis_value]["vol_strains"], dtype=object)[
            analysis_dict[analysis_value]["vol_strain_indices"]
        ],
        value=analysis_value,
    )

axes_4.legend(loc="upper left")

fig_4.tight_layout()
plt.savefig(
    os.path.join(
        vis_export_dir, f"{export_material}_vol_strain_{analysis_key}_comparison.pgf"
    )
)
plt.savefig(
    os.path.join(
        vis_export_dir,
        f"{export_material}_vol_strain_{analysis_key}_comparison_small.png",
    )
)
fig_4.set_size_inches(12, 9)
fig_4.suptitle(f"{material}, comparison: {analysis_key}", fontsize=12)
fig_4.tight_layout()
plt.savefig(
    os.path.join(
        vis_export_dir,
        f"{export_material}_vol_strain_{analysis_key}_comparison_large.png",
    )
)
plt.close()
