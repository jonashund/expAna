import platform
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


def plt_style():
    """
    Set custom style parameters for plots.
    """

    matplotlib.use("pgf")  # use the pgf backend

    # Include user defined 'phd.mplstyle' located in
    # print(matplotlib.get_configdir())
    #   * MacBook Air: ./Users/jonas/.matplolib/stylelib
    #   * ifmpc84: /home/jonas/.config/matplotlib/stylelib
    # The style file can also be located in any directory.
    # For invoking it the path has to be specified then.
    # For details see
    # https://matplotlib.org/tutorials/introductory/customizing.html
    try:
        plt.style.use("phd")
    except:
        # in case someone different than me will ever use this
        plt.style.use("seaborn_dark_palette")

    # Overwrite default settings in rcParams if necessary.
    # For matplotlibrc.template file see
    # <python_installation_dir>/site-packages/matplotlib/mpl-data/matplotlibrc

    # For details on customising see
    # https://matplotlib.org/tutorials/introductory/customizing.html

    # Set rcParams for LaTeX
    set_latex_fonts = {
        # Use LaTeX to write all text
        "text.usetex": True,
        "font.family": "serif",
        # Use xxpt font in plots, to match xxpt font in document
        "font.size": 12,
        "axes.labelsize": 12,
        # Make the legend/label fonts a little smaller
        "legend.fontsize": 12,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    }
    matplotlib.rcParams.update(set_latex_fonts)

    # Set rcParams for pgf backend.
    # For details see
    # https://matplotlib.org/3.1.1/tutorials/text/pgf.html
    matplotlib.rcParams.update({"pgf.texsystem": "xelatex"})
    matplotlib.rcParams.update({"pgf.rcfonts": False})

    set_preamble = {"pgf.preamble": r"\usepackage{amsmath} \usepackage{xfrac}"}
    matplotlib.rcParams.update(set_preamble)

    # set more rcParams
    matplotlib.rcParams.update({"patch.linewidth": 1})
    return


def set_plt_backend():
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


def remove_column_offset(dataframe, column_name):
    dataframe[column_name] = dataframe[column_name] - dataframe[column_name].iloc[0]

    return dataframe


def remove_row_offset(dataframe, column_name, threshold):
    threshold_begin = dataframe[dataframe[column_name] > threshold].index[0]

    dataframe = dataframe[threshold_begin:]

    return dataframe


def remove_fail_rows(dataframe, column_name, threshold):

    dataframe = dataframe[dataframe[column_name] > threshold]
    dataframe = dataframe[:-1]

    return dataframe


def remove_offsets(experiment):
    experiment.gauge_results = remove_row_offset(
        experiment.gauge_results, "reaction_force_in_kN", 0.015
    )

    experiment.gauge_results = remove_column_offset(
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


def style_poissons_ratio(width=None, height=None, x_lim=None, y_lim=0.5):

    if width and height:
        fig_1, axes_1 = create_styled_figure(width=width, height=height)
    else:
        fig_1, axes_1 = create_styled_figure()

    axes_1.set_xlabel(r"log. strain $\varepsilon$ [-]")
    axes_1.set_ylabel(r"poissons_ratio $\varepsilon_{xx}/\varepsilon_{yy}$ [-]")

    if x_lim:
        axes_1.set_xlim(0, x_lim)
    else:
        pass

    if y_lim:
        axes_1.set_ylim(0, y_lim)
    else:
        pass

    return fig_1, axes_1


def style_force_displ(width=None, height=None, x_lim=None, y_lim=None):

    if width and height:
        fig_1, axes_1 = create_styled_figure(width=width, height=height)
    else:
        fig_1, axes_1 = create_styled_figure()

    axes_1.set_xlabel(r"displacement $u$ [mm]")
    axes_1.set_ylabel(r"reaction force $F$ [kN]")

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
    plt_style()

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
        linewidth=2,
        zorder=10,
        color=current_color,
    )
    for i in range(len(xs)):
        if i == 0:
            axes.plot(
                xs[i],
                ys[i],
                linewidth=0.33,
                zorder=1,
                alpha=0.33,
                color=current_color,
                label=f"experiments {value}",
            )
        else:
            axes.plot(
                xs[i], ys[i], linewidth=0.5, zorder=1, alpha=0.33, color=current_color
            )

    return fig, axes
