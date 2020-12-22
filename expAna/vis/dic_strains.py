import os
import dill
import numpy as np
import matplotlib.pyplot as plt
import scipy.spatial

import expAna


def main(
    experiment_name,
    strain_component,
    displacement,
    key_min=None,
    key_max=None,
    max_triang_len=10,
):
    work_dir = os.getcwd()
    expDoc_data_dir = os.path.join(work_dir, "data_expDoc", "python")
    istra_acquisition_dir = os.path.join(work_dir, "data_istra_acquisition")
    istra_evaluation_dir = os.path.join(work_dir, "data_istra_evaluation")
    vis_export_dir = os.path.join(work_dir, "visualisation")

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

    direction_selector = expAna.gui.TensileDirection(experiment.ref_image)
    direction_selector.__gui__()
    experiment.tensile_direction = direction_selector.direction

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

    # search frame number to given displacement
    frame_range = np.where(traverse_displ > displacement)[0]
    frame_no = frame_range[0]

    # strain in given direction for frame_no
    strain_to_plot = true_strain[frame_no, :, :, strain_component]

    # manipulate strain_to_plot: contour smoothing

    # coordinates of grid points [in px] for frame_no
    # coords_to_plot = experiment.coords[frame_no, ...]
    coords_to_plot = experiment.pix_coords[frame_no, ...]

    # get image to frame no
    image_to_plot = experiment.get_image(
        frame_no=frame_no, istra_acquisition_dir=istra_acquisition_dir
    )

    # plot using JB's Delauney triangulation (code courtesy of Julian Bauer)
    ###################################
    # Create flat data

    # Identify positions of DIC-grip-points where identification failed
    # i.e. where coordinates are near zero
    mask = np.linalg.norm(coords_to_plot, axis=-1) > 1e-12

    # Select data loosing grid
    x_coords_flat = coords_to_plot[mask, 0]
    y_coords_flat = coords_to_plot[mask, 1]
    strain_flat = strain_to_plot[mask]

    # cut image for overlay
    max_y = max(y_coords_flat)
    min_y = min(y_coords_flat)
    y_center = (max_y + min_y) / 2.0
    image_height = 1.25 * (max_y - min_y)
    if image_height > image_to_plot.shape[0]:
        image_height = image_to_plot.shape[0]
    else:
        pass

    image_width = image_height
    max_x = max(x_coords_flat)
    min_x = min(x_coords_flat)
    x_center = (max_x + min_x) / 2.0

    if max_x - min_x > image_width:
        image_width = 1.25 * (max_x - min_x)
    if image_width > image_to_plot.shape[1]:
        image_width = image_to_plot.shape[1]
    else:
        pass

    image_masked = image_to_plot[
        int(y_center - image_height / 2.0) : int(y_center + image_height / 2.0),
        int(x_center - image_width / 2.0) : int(x_center + image_width / 2.0),
    ]

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

    if not triangles_small.size == 0:
        plt.triplot(points[:, 0], points[:, 1], triangles_small)
        plt.plot(points[:, 0], points[:, 1], "o")

    if True:
        name = "01_tricontourf.png"
        figsize = (15, 15)
        fig_1, axes_1 = plt.subplots(1, 1, figsize=figsize)

        # ax.tricontourf(X=x_flat, Y=y_flat, triangles=triangles_small, Z=z_flat, N=10)
        strain_plot = axes_1.tricontourf(
            x_coords_flat,
            y_coords_flat,
            triangles_small,
            strain_flat,
            10,
            alpha=0.7,
            zorder=10,
        )
        image_plot = axes_1.imshow(image_masked, alpha=1, zorder=9, cmap="gray")
        # grid_plot = expAna.vis.plot.plot_points(ax=ax, x=x_coords_flat, y=y_coords_flat)

        # remove tick labels
        # add colorbar for strain_plot (vertical, on the right, optionally in range provided, legend title accoding to input)

        plt.savefig(os.path.join(vis_export_dir, name))
        plt.close("all")
