import os
import dill
import platform
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import scipy.spatial
import expAna


def plt_style():
    """
    Set custom style parameters for plots.
    """

    matplotlib.use("pgf")  # use the pgf backend

    # Include user defined 'phd.mplstyle' located in
    # print(matplotlib.get_configdir())
    #   * MacBook Air: ./Users/jonas/.matplotlib/stylelib
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
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
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


def shift_columns(dataframe, column_name, shift):
    dataframe[column_name] = dataframe[column_name] - shift

    return dataframe


def remove_row_offset(dataframe, column_name, threshold):
    threshold_begin = dataframe[dataframe[column_name] > threshold].index[0]

    dataframe = dataframe[threshold_begin:]

    return dataframe


def remove_fail_rows(dataframe, column_name, threshold):

    dataframe = dataframe[dataframe[column_name] > threshold]
    dataframe = dataframe[:-1]

    return dataframe


def remove_offsets(experiment, row_threshold=None):
    if row_threshold == None:
        row_threshold = 0.015
    experiment.gauge_results = remove_row_offset(
        experiment.gauge_results, "reaction_force_in_kN", row_threshold
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


def create_styled_figure(width=5, height=3.75):
    plt_style()

    fig, axes = plt.subplots(figsize=[width, height])
    axes.xaxis.set_minor_locator(mtick.AutoMinorLocator(2))
    # axes.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    axes.yaxis.set_minor_locator(mtick.AutoMinorLocator(2))
    axes.grid(color="lightgrey", linewidth=0.33, linestyle="-")

    axes.tick_params(direction="out", pad=5)
    axes.tick_params(bottom=True, left=True, top=False, right=False)

    return fig, axes


def add_curves_same_value(fig, axes, x_mean, y_mean, xs=[], ys=[], value=None):

    current_color = next(axes._get_lines.prop_cycler)["color"]
    axes.plot(
        x_mean,
        y_mean,
        label=f"{value} (mean)",
        linewidth=2,
        zorder=10,
        color=current_color,
    )
    for i in range(len(xs)):
        if i == 0:
            axes.plot(
                xs[i],
                ys[i],
                linewidth=0.75,
                linestyle="--",
                dashes=(7, 7),
                zorder=1,
                color=current_color,
                label=f"{value} (raw data)",
                # alpha=0.33,
            )
        else:
            axes.plot(
                xs[i],
                ys[i],
                linewidth=0.75,
                linestyle="--",
                dashes=(7, 7),
                zorder=1,
                color=current_color,
                # alpha=0.33,
            )

    return fig, axes


def add_mean_and_sem(fig, axes, x_mean, y_mean, y_error, value=None):

    current_color = next(axes._get_lines.prop_cycler)["color"]
    axes.plot(
        x_mean,
        y_mean,
        label=f"{value} (mean)",
        linewidth=2,
        zorder=10,
        color=current_color,
    )
    axes.fill_between(
        x_mean, y_mean - y_error, y_mean + y_error, alpha=0.2, facecolor=current_color
    )

    return fig, axes


def plot_points(ax, x, y):
    # x and y can be of vector or matrix shape
    ax.plot(x, y, "ko ", markersize=0.4)


def dic_strains(
    experiment_name,
    displacement,
    strain_component,
    tensile_direction="x",
    image_height=None,
    image_width=None,
    rotate=None,
    key=True,
    key_min=None,
    key_max=None,
    key_extend=None,
    max_triang_len=10,
    out_format="pdf",
    dots_pi=400,
):
    work_dir = os.getcwd()
    vis_export_dir = os.path.join(work_dir, "visualisation")

    if out_format == "eps" or out_format == "pdf":
        set_latex_fonts = {
            # Use LaTeX to write all text
            "text.usetex": True,
            "font.family": "serif",
            # Use xxpt font in plots, to match xxpt font in document
            "font.size": 12,
            "axes.labelsize": 12,
            # Make the legend/label fonts a little smaller
            "legend.fontsize": 12,
            "xtick.labelsize": 12,
            "ytick.labelsize": 12,
        }
        matplotlib.rcParams.update(set_latex_fonts)
    elif out_format == "pgf":
        expAna.plot.plt_style()
    else:
        pass

    figsize = (4, 4)
    fig_1, axes_1 = plt.subplots(1, 1, figsize=figsize)

    name = (
        f"{experiment_name}_dic_strain_{strain_component}_displ_{displacement:.1f}_mm"
    )

    displacement_val = expAna.plot.create_dic_vis(
        fig=fig_1,
        axes=axes_1,
        experiment_name=experiment_name,
        displacement=displacement,
        strain_component=strain_component,
        tensile_direction=tensile_direction,
        image_height=image_height,
        image_width=image_width,
        rotate=rotate,
        key=key,
        key_min=key_min,
        key_max=key_max,
        key_extend=key_extend,
        max_triang_len=max_triang_len,
    )

    axes_1.text(
        0.05,
        0.95,
        r"$u = $ " + f"{displacement_val:.1f}" + r"~mm",
        verticalalignment="top",
        horizontalalignment="left",
        transform=fig_1.transFigure,
        color="black",
        fontsize=12,
        zorder=12,
    )

    if rotate == 90:
        csys_params = {
            "xy_0": (0.04, 0.2),
            "xy_1": (0.19, 0.045),
        }
    else:
        csys_params = {
            "xy_0": (0.2, 0.05),
            "xy_1": (0.05, 0.2),
        }

    axes_1.annotate(
        "",
        xy=csys_params["xy_0"],
        xycoords="figure fraction",
        xytext=csys_params["xy_1"],
        arrowprops=dict(
            arrowstyle="<|-|>",
            color="black",
            shrinkA=5,
            shrinkB=5,
            patchA=None,
            patchB=None,
            connectionstyle="angle,angleA=-90,angleB=180,rad=0",
        ),
        color="black",
        fontsize=12,
        zorder=12,
    )

    axes_1.text(
        0.21,
        0.09,
        r"$x$",
        verticalalignment="center",
        horizontalalignment="left",
        transform=fig_1.transFigure,
        color="black",
        fontsize=12,
        zorder=12,
    )
    axes_1.text(
        0.09,
        0.21,
        r"$y$",
        verticalalignment="bottom",
        horizontalalignment="center",
        transform=fig_1.transFigure,
        color="black",
        fontsize=12,
        zorder=12,
    )

    fig_1.tight_layout()
    if out_format == "pdf":
        plt.savefig(
            os.path.join(vis_export_dir, name + ".pdf"),
            format="pdf",
            bbox_inches="tight",
            pad_inches=0,
            dpi=dots_pi,
        )
    elif out_format == "eps":
        plt.savefig(
            os.path.join(vis_export_dir, name + ".eps"),
            format="eps",
            bbox_inches="tight",
            pad_inches=0,
            dpi=dots_pi,
        )
    elif out_format == "pgf":
        plt.savefig(
            os.path.join(vis_export_dir, name + ".pgf"),
        )
    else:
        plt.show()

    plt.close("all")


def hex_to_rgb(value):
    """
    Converts hex to rgb colours
    value: string of 6 characters representing a hex colour.
    Returns: list length 3 of RGB values"""
    value = value.strip("#")  # removes hash symbol if present
    lv = len(value)
    return tuple(int(value[i : i + lv // 3], 16) for i in range(0, lv, lv // 3))


def rgb_to_dec(value):
    """
    Converts rgb to decimal colours (i.e. divides each value by 256)
    value: list (length 3) of RGB values
    Returns: list (length 3) of decimal values"""
    return [v / 256 for v in value]


def get_continuous_cmap(hex_list, float_list=None):
    """creates and returns a color map that can be used in heat map figures.
    If float_list is not provided, colour map graduates linearly between each color in hex_list.
    If float_list is provided, each color in hex_list is mapped to the respective location in float_list.

    Parameters
    ----------
    hex_list: list of hex code strings
    float_list: list of floats between 0 and 1, same length as hex_list. Must start with 0 and end with 1.

    Returns
    ----------
    colour map"""
    rgb_list = [rgb_to_dec(hex_to_rgb(i)) for i in hex_list]
    if float_list:
        pass
    else:
        float_list = list(np.linspace(0, 1, len(rgb_list)))

    cdict = dict()
    for num, col in enumerate(["red", "green", "blue"]):
        col_list = [
            [float_list[i], rgb_list[i][num], rgb_list[i][num]]
            for i in range(len(float_list))
        ]
        cdict[col] = col_list
    cmp = matplotlib.colors.LinearSegmentedColormap("my_cmp", segmentdata=cdict, N=256)
    return cmp


def create_dic_vis(
    fig,
    axes,
    experiment_name,
    displacement,
    strain_component,
    tensile_direction="x",
    image_height=None,
    image_width=None,
    rotate=None,
    key=True,
    key_min=None,
    key_max=None,
    key_extend=None,
    max_triang_len=10,
    raster=True,
    cmap=None,
):
    work_dir = os.getcwd()
    expDoc_data_dir = os.path.join(work_dir, "data_expDoc", "python")
    istra_acquisition_dir = os.path.join(work_dir, "data_istra_acquisition")
    istra_evaluation_dir = os.path.join(work_dir, "data_istra_evaluation")

    try:
        with open(
            os.path.join(expDoc_data_dir, experiment_name + "_expDoc.pickle"),
            "rb",
        ) as myfile:
            experiment = dill.load(myfile)
    except:
        print(
            f"""
        Warning:
        No documentation data found for {experiment_name}!
        Document your experiments properly using the expDoc package before analysis.
        """
        )
        assert False

    experiment.read_istra_evaluation(istra_acquisition_dir, istra_evaluation_dir)

    if tensile_direction is None:
        direction_selector = expAna.gui.TensileDirection(experiment.ref_image)
        direction_selector.__gui__()
        experiment.tensile_direction = direction_selector.direction
    else:
        experiment.tensile_direction = tensile_direction

    if experiment.tensile_direction == "x":
        x_idx = 0
        y_idx = 1
    else:
        x_idx = 1
        y_idx = 0

    # get strains from evaluation
    # pixel gradients are treated as elements of the deformation gradient
    # true_strain[nbr_frames, x_pxl_pos, y_pxl_pos, component]
    # component:{0:"xx", 1:"yy",2:"xy"}
    true_strain = expAna.gauge.get_true_strain(experiment.def_grad)
    true_strain[:, :, :, :][experiment.mask[:, :, :, 0] == 0] = np.nan

    (nbr_frames, nbr_x_pxls, nbr_y_pxls, nbr_def_grad_comps) = experiment.def_grad.shape
    true_strain_sorted = np.zeros(
        (nbr_frames, nbr_x_pxls, nbr_y_pxls, 3), dtype=np.float64
    )
    true_strain_sorted[:, :, :, 0] = true_strain[:, :, :, x_idx]
    true_strain_sorted[:, :, :, 1] = true_strain[:, :, :, y_idx]
    true_strain_sorted[:, :, :, 2] = true_strain[:, :, :, 2]

    true_strain = true_strain_sorted
    traverse_displ = experiment.traverse_displ
    # remove offset in traverse_displ
    traverse_displ = experiment.traverse_displ - experiment.traverse_displ[0]

    # search frame numbers for given displacement
    # frame_range = np.where(traverse_displ > displacement)[0]
    # frame_no = frame_range[0]

    displacement_val, frame_no = expAna.calc.find_nearest(traverse_displ, displacement)
    displacement_val = displacement_val[0]

    print(
        f"Nearest displacement value to given displacement {displacement} is {displacement_val}. Difference: {abs(displacement_val-displacement)}"
    )

    if strain_component == "x":
        strain_idx = 0
    if strain_component == "y":
        strain_idx = 1
    if strain_component == "xy":
        strain_idx = 2

    # strain in given direction for frame_no
    strain_to_plot = true_strain[frame_no, :, :, strain_idx]

    # coordinates of grid points [in px] for frame_no
    # coords_to_plot = experiment.coords[frame_no, ...]
    coords_to_plot = experiment.pix_coords[frame_no, ...]

    # get image to frame no
    image_to_plot = experiment.get_image(
        frame_no=frame_no, istra_acquisition_dir=istra_acquisition_dir
    )

    # rotate image and data
    if rotate is None:
        pass
    elif rotate == 90:
        image_to_plot = np.rot90(m=image_to_plot, k=-1)
        strain_to_plot = np.rot90(m=strain_to_plot)
        coords_to_plot_2 = np.rot90(m=coords_to_plot, k=1, axes=(0, 1))
        coords_to_plot = np.empty_like(coords_to_plot_2)
        coords_to_plot[:, :, 0] = coords_to_plot_2[:, :, 1]
        coords_to_plot[:, :, 1] = coords_to_plot_2[:, :, 0]
    else:
        print(
            "Only rotate=90 supported. Expand this package to support other rotations? :-)"
        )

    # plot using JB's Delauney triangulation (code courtesy of Julian Bauer)
    ###################################
    # Create flat data

    # Identify positions of DIC-grid-points where identification failed
    # i.e. where coordinates are near zero
    mask = np.linalg.norm(coords_to_plot, axis=-1) > 1e-12

    if rotate == 90:
        coords_to_plot[:, :, 0] = (
            np.full(coords_to_plot[:, :, 0].shape, image_to_plot.shape[1])
            - coords_to_plot[:, :, 0]
        )

    # Select data loosing grid
    x_coords_flat = coords_to_plot[mask, 0]
    y_coords_flat = coords_to_plot[mask, 1]
    strain_flat = strain_to_plot[mask]

    # cut image for overlay
    max_y = max(y_coords_flat)
    min_y = min(y_coords_flat)
    y_center = (max_y + min_y) / 2.0

    if image_height == None:
        image_height = 1.25 * (max_y - min_y)
    else:
        image_height = image_height
        y_center = image_to_plot.shape[0] / 2.0

    if (
        image_height > image_to_plot.shape[0]
        or y_center + image_height / 2.0 > image_to_plot.shape[0]
        or y_center - image_height / 2.0 < 0.0
    ):
        image_height = image_to_plot.shape[0]
        y_center = image_to_plot.shape[0] / 2.0
    else:
        pass

    if image_width == None:
        image_width = image_height
    else:
        image_width = image_width
        x_center = image_to_plot.shape[1] / 2.0

    max_x = max(x_coords_flat)
    min_x = min(x_coords_flat)
    x_center = (max_x + min_x) / 2.0

    if max_x - min_x > image_width:
        image_width = 1.25 * (max_x - min_x)
    else:
        pass

    if (
        image_width > image_to_plot.shape[1]
        or x_center + image_width / 2.0 > image_to_plot.shape[1]
        or x_center - image_width / 2.0 < 0.0
    ):
        image_width = image_to_plot.shape[1]
        x_center = image_to_plot.shape[1] / 2.0
    else:
        pass

    image_masked = image_to_plot[
        int(y_center - image_height / 2.0) : int(y_center + image_height / 2.0),
        int(x_center - image_width / 2.0) : int(x_center + image_width / 2.0),
    ]

    # sometimes manually determining the image_width and image_height is necessary
    # print(image_to_plot.shape)
    # print("x_center", x_center)
    # print("image_width", image_width)
    # print("y_center", y_center)
    # print("image_height", image_width)
    # print(image_masked.shape)

    # coordinate transformation for other values
    x_coords_flat = x_coords_flat - int(x_center - image_width / 2.0)
    y_coords_flat = y_coords_flat - int(y_center - image_height / 2.0)

    points = np.concatenate((x_coords_flat[:, None], y_coords_flat[:, None]), axis=1)

    delauney_triangulation = scipy.spatial.Delaunay(points)

    # a 2-simplex is a triangle
    triangles = delauney_triangulation.simplices

    max_length = max_triang_len  # Todo: get this parameter algorithmically e.g. take mean of 100 random triangle edges
    pairs_points_in_triangle = [[0, 1], [1, 2], [2, 0]]

    mask_smaller = np.ones(len(triangles), dtype=np.bool)
    for i, simplex in enumerate(triangles):
        for pair in pairs_points_in_triangle:
            diff = points[simplex[pair[0]]] - points[simplex[pair[1]]]
            if np.linalg.norm(diff) > max_length:
                mask_smaller[i] = False

    triangles_small = triangles[mask_smaller]

    # Do not plot to reduce filesize!
    # if not triangles_small.size == 0:
    #     plt.triplot(points[:, 0], points[:, 1], triangles_small)
    #     plt.plot(points[:, 0], points[:, 1], "o")

    # determine levels for contourplot
    min_strain = min(strain_flat)
    max_strain = max(strain_flat)
    # from given min/max values
    if key_min is not None and key_max is None:
        levels = np.linspace(key_min, max_strain, 1000)
        extend = "min"
    elif key_min is None and key_max is not None:
        levels = np.linspace(min_strain, key_max, 1000)
        extend = "max"
    elif key_min is not None and key_max is not None:
        levels = np.linspace(key_min, key_max, 1000)
        extend = "both"
    else:
        # from minimum and maximum strain values
        levels = np.linspace(min_strain, max_strain, 1000)
        extend = "neither"

    if key_extend is not None:
        extend = key_extend

    if cmap is not None:
        cmap = cmap
    else:
        cmap = "jet"

    strain_plot = axes.tricontourf(
        x_coords_flat,
        y_coords_flat,
        triangles_small,
        strain_flat,
        levels,
        zorder=-1,
        cmap=cmap,
        extend=extend,
    )
    for c in strain_plot.collections:
        c.set_edgecolor("face")

    # raster output to reduce filesize
    if raster is True:
        axes.set_rasterization_zorder(0)
    else:
        pass

    if key is True:
        # add colorbar for strain_plot (vertical, on the right, optionally in range provided, legend title accoding to input)
        clrbar = fig.colorbar(
            strain_plot,
            orientation="vertical",
            ax=axes,
            # fraction=0.05,
            # pad=0.05,
            shrink=0.8,
            format="%0.2f",
        )
        # set legend title
        if strain_component == "x":
            lgnd_title = r"$\varepsilon_{xx}$ [~-~]"
        elif strain_component == "y":
            lgnd_title = r"$\varepsilon_{yy}$ [~-~]"
        elif strain_component == "xy":
            lgnd_title = r"$\varepsilon_{xy}$ [~-~]"
        else:
            lgnd_title = ""

        # clrbar.ax.set_title(lgnd_title)
        clrbar.ax.set_ylabel(lgnd_title, labelpad=10)
    else:
        pass

    image_plot = axes.imshow(image_masked, alpha=1, zorder=-2, cmap="gray")
    # grid_plot = expAna.plot.plot_points(ax=ax, x=x_coords_flat, y=y_coords_flat)

    # remove tick labels
    axes.tick_params(
        axis="x",  # changes apply to the x-axis
        which="both",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,
    )

    axes.tick_params(
        axis="y",
        which="both",
        left=False,
        right=False,
        labelleft=False,
    )

    return displacement_val
