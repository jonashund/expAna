import os
import sys
import platform
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# doc funcs are located in instron2doc directory
sys.path.append("../instron2doc/")

import doc_funcs


def set_gui_backend():
    import matplotlib

    if platform.system() == "Darwin":
        matplotlib.use("macosx")
    elif platform.system() == "Linux":
        matplotlib.use("TkAgg")
    else:
        print(
            f"""
        {platform.system()} not supported (yet).
        Could you please add it in gui_funcs.set_gui_backend()?
        """
        )
        exit()

    matplotlib.rcParams.update(matplotlib.rcParamsDefault)


def remove_offsets(experiment):
    experiment.gauge_results = doc_funcs.remove_row_offset(
        experiment.gauge_results, "reaction_force_in_kN", 0.015
    )

    experiment.gauge_results = doc_funcs.remove_column_offset(
        experiment.gauge_results, "displacement_in_mm"
    )


def plot_true_stress_strain(
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
    # experiment.gauge_results = doc_funcs.remove_fail_rows(
    #     experiment.gauge_results, "reaction_force_in_kN", 0.0
    # )

    doc_funcs.plot_style()

    fig_1, axes_1 = plt.subplots(figsize=[4, 3])
    # axes styling
    axes_1.xaxis.set_minor_locator(mtick.AutoMinorLocator(2))
    # axes_1.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    axes_1.yaxis.set_minor_locator(mtick.AutoMinorLocator(2))
    axes_1.grid(color="lightgrey", linewidth=0.33, zorder=0, linestyle="-")

    axes_1.tick_params(direction="out", pad=5)
    axes_1.tick_params(bottom=True, left=True, top=False, right=False)

    # axes_1.set_xlim(0, 1.1 * experiment.gauge_results["true_strain_image_x"].max())
    axes_1.set_xlim(0, 1.0)
    axes_1.set_ylim(0, 1.1 * experiment.gauge_results["true_stress_in_MPa"].max())

    axes_1.set_xlabel(r"log. strain $\varepsilon$ [-]")
    axes_1.set_ylabel(r"true stress $\sigma$ [MPa]")

    axes_1.plot(
        experiment.gauge_results["true_strain_image_x"],
        experiment.gauge_results["true_stress_in_MPa"],
        label=f"{experiment.name}",
        linewidth=1.0,
        zorder=1,
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
    axes_1.grid(color="lightgrey", linewidth=0.33, zorder=0, linestyle="-")

    # axes_1.set_xlim(0, 1.1 * experiment.gauge_results["true_strain_image_x"].max())
    axes_1.set_xlim(0, 1.0)
    axes_1.set_ylim(0, 1.1 * experiment.gauge_results["volume_strain"].max())

    axes_1.tick_params(direction="out", pad=5)
    axes_1.tick_params(bottom=True, left=True, top=False, right=False)

    axes_1.set_xlabel(r"log. strain $\varepsilon$ [-]")
    axes_1.set_ylabel(r"volume strain $\varepsilon_{ii}$")

    axes_1.plot(
        experiment.gauge_results["true_strain_image_x"],
        experiment.gauge_results["volume_strain"],
        label=f"{experiment.name}",
        linewidth=1.0,
        zorder=1,
    )
    fig_1.tight_layout()
    plt.savefig(os.path.join(out_dir, experiment.name + "_vol_strain.pgf",))
    plt.savefig(os.path.join(out_dir, experiment.name + "_vol_strain.png",))

    plt.close()
