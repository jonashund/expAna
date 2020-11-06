import os
import sys
import platform
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# doc funcs are located in instron2doc directory
sys.path.append("../instron2doc/")

import doc_funcs


def set_plot_backend():
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
    # plt.style.use("classic")


def remove_offsets(experiment):
    experiment.gauge_results = doc_funcs.remove_row_offset(
        experiment.gauge_results, "reaction_force_in_kN", 0.015
    )

    experiment.gauge_results = doc_funcs.remove_column_offset(
        experiment.gauge_results, "displacement_in_mm"
    )


def style_true_stress(width=None, height=None, x_lim=None, y_lim=None):

    if width and height:
        fig_1, axes_1 = create_styled_figure(width=width, height=height)
    else:
        fig_1, axes_1 = create_styled_figure()

    axes_1.set_xlabel(r"log. strain $\varepsilon$ [-]")
    axes_1.set_ylabel(r"true stress $\sigma$ [MPa]")

    if x_lim:
        axes_1.set_xlim(0, x_lim)
    else:
        pass

    if y_lim:
        axes_1.set_ylim(0, y_lim)
    else:
        pass

    return fig_1, axes_1


def style_vol_strain(width=None, height=None, x_lim=None, y_lim=None):

    if width and height:
        fig_1, axes_1 = create_styled_figure(width=width, height=height)
    else:
        fig_1, axes_1 = create_styled_figure()

    axes_1.set_xlabel(r"log. strain $\varepsilon$ [-]")
    axes_1.set_ylabel(r"volume strain $\varepsilon_{ii}$")

    if x_lim:
        axes_1.set_xlim(0, x_lim)
    else:
        pass

    if y_lim:
        axes_1.set_ylim(0, y_lim)
    else:
        pass

    return fig_1, axes_1


def create_styled_figure(width=4, height=3):
    doc_funcs.plot_style()

    fig_1, axes_1 = plt.subplots(figsize=[width, height])
    # axes styling
    axes_1.xaxis.set_minor_locator(mtick.AutoMinorLocator(2))
    # axes_1.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    axes_1.yaxis.set_minor_locator(mtick.AutoMinorLocator(2))
    axes_1.grid(color="lightgrey", linewidth=0.33, linestyle="-")

    axes_1.tick_params(direction="out", pad=5)
    axes_1.tick_params(bottom=True, left=True, top=False, right=False)

    return fig_1, axes_1


def add_curves_same_value(fig, axes, x_mean, y_mean, xs=[], ys=[], value=None):
    from cycler import cycler

    current_color = next(axes._get_lines.prop_cycler)["color"]
    axes.plot(
        x_mean,
        y_mean,
        label=f"average {value}",
        linewidth=1.5,
        zorder=1,
        color=current_color,
    )
    for i in range(len(xs)):
        if i == 0:
            axes.plot(
                xs[i],
                ys[i],
                linewidth=0.5,
                zorder=1,
                alpha=0.5,
                color=current_color,
                label=f"experiments {value}",
            )
        else:
            axes.plot(
                xs[i], ys[i], linewidth=0.5, zorder=1, alpha=0.5, color=current_color
            )

    return fig, axes
