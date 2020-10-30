import os
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import doc_funcs


def plot_true_stress_strain(
    experiment,
    out_dir=os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "visualisation"
    ),
):

    os.makedirs(out_dir, exist_ok=True)

    experiment.gauge_results = doc_funcs.remove_row_offset(
        experiment.gauge_results, "reaction_force_in_kN", 0.015
    )

    experiment.gauge_results = doc_funcs.remove_column_offset(
        experiment.gauge_results, "displacement_in_mm"
    )

    # experiment.gauge_results = slice_at_local_max(
    #     experiment.gauge_results, "true_stress_in_MPa", 150
    # )

    doc_funcs.plot_style()

    fig_1, axes_1 = plt.subplots(figsize=[4, 3])
    # axes styling
    axes_1.xaxis.set_minor_locator(mtick.AutoMinorLocator(2))
    # axes_1.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    axes_1.yaxis.set_minor_locator(mtick.AutoMinorLocator(2))
    axes_1.grid(color="#929591", linewidth=0.33, zorder=0)

    axes_1.set_xlim(0, 1.1 * experiment.gauge_results["log_strain_image_x"].max())
    axes_1.set_ylim(0, 1.1 * experiment.gauge_results["true_stress_in_MPa"].max())

    axes_1.set_xlabel(r"log. strain $\varepsilon$ [-]")
    axes_1.set_ylabel(r"true stress $\sigma$ [MPa]")

    axes_1.plot(
        experiment.gauge_results["log_strain_image_x"],
        experiment.gauge_results["true_stress_in_MPa"],
        label=f"{experiment.name}",
        linewidth=1.0,
    )
    fig_1.tight_layout()
    plt.savefig(os.path.join(out_dir, experiment.name + "_stress_strain.pgf",))
    plt.savefig(os.path.join(out_dir, experiment.name + "_stress_strain.png",))

    plt.close()


def plot_volume_strain(
    experiment,
    out_dir=os.path.join(
        os.path.abspath(os.path.dirname(__file__)), "..", "visualisation"
    ),
):

    os.makedirs(out_dir, exist_ok=True)

    # experiment.gauge_results = doc_funcs.remove_row_offset(
    #     experiment.gauge_results, "reaction_force_in_kN", 0.015
    # )
    #
    # experiment.gauge_results = doc_funcs.remove_column_offset(
    #     experiment.gauge_results, "displacement_in_mm"
    # )
    #
    # experiment.gauge_results = slice_at_local_max(
    #     experiment.gauge_results, "true_stress_in_MPa", 100
    # )

    doc_funcs.plot_style()

    fig_1, axes_1 = plt.subplots(figsize=[4, 3])
    # axes styling
    axes_1.xaxis.set_minor_locator(mtick.AutoMinorLocator(2))
    # axes_1.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    axes_1.yaxis.set_minor_locator(mtick.AutoMinorLocator(2))
    axes_1.grid(color="#929591", linewidth=0.33, zorder=0)

    axes_1.set_xlim(0, 1.1 * experiment.gauge_results["log_strain_image_x"].max())
    axes_1.set_ylim(0, 1.1 * experiment.gauge_results["volume_strain"].max())

    axes_1.set_xlabel(r"log. strain $\varepsilon$ [-]")
    axes_1.set_ylabel(r"volume strain $\varepsilon_{ii}$")

    axes_1.plot(
        experiment.gauge_results["log_strain_image_x"],
        experiment.gauge_results["volume_strain"],
        label=f"{experiment.name}",
        linewidth=1.0,
    )
    fig_1.tight_layout()
    plt.savefig(os.path.join(out_dir, experiment.name + "_vol_strain.pgf",))
    plt.savefig(os.path.join(out_dir, experiment.name + "_vol_strain.png",))

    plt.close()


#
# def slice_at_local_max(dataframe, column_name, ignore_idx):
#     recorded_value_count = dataframe[column_name].shape[0]
#
#     if recorded_value_count > ignore_idx:
#         for i in range(ignore_idx, recorded_value_count):
#             ref_value_1 = dataframe[column_name][i - 2]
#             ref_value_2 = dataframe[column_name][i - 1]
#             current_value = dataframe[column_name][i]
#             if (current_value < ref_value_1) and (current_value < ref_value_2):
#                 dataframe = dataframe[:i-2]
#
#     return dataframe
