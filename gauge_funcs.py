import numpy as np
import platform
import matplotlib
import matplotlib.pyplot as plt


def set_gui_backend():
    if platform.system() == "Darwin":
        matplotlib.use("macosx")
    elif platform.system() == "Linux":
        matplotlib.use("TkAgg")
    else:
        print(
            f"""
        {platform.system()} not supported (yet).
        Could you please add it in gauge_funcs.set_gui_backend()?
        """
        )
        exit()


class TensileDirection(object):
    def __init__(self, input_image):
        self.image = input_image
        self.direction = "x"

    def __gui__(self):
        def direction_selector(event):
            print(f"Key pressed {event.key}.")

            if event.key in ["left", "right"]:
                self.direction = "x"
                print("tensile direction set to `horizontal`")
                plt.close()

            if event.key in ["up", "down"]:
                self.direction = "y"
                print("tensile direction set to `vertical`")
                plt.close()

            if event.key in ["enter"]:
                print("default tensile direction `vertical` confirmed")
                plt.close()

        def print_instructions():
            print(
                """
                Enter tensile direction in image shown using arrow keys.
                Skip with enter to accept default direction: `horizontal`.
                """
            )

        # set_gui_backend()
        plt.style.use("classic")

        plt.ioff()
        fig_1 = plt.figure()
        plt.imshow(self.image, cmap="Greys_r")
        print_instructions()
        fig_1.canvas.mpl_connect("key_press_event", direction_selector)
        plt.show(block=True)


class RectangleCoordinates(object):
    def __init__(self, input_image):
        self.image = input_image
        self.coordinates = [0, 0, self.image.shape[1], self.image.shape[0]]

    def toggle_selector(event):
        print(f"Key pressed {event.key}.")

        if event.key in ["enter"]:
            plt.close()

    def __gui__(self):
        from matplotlib.widgets import RectangleSelector

        def line_select_callback(eclick, erelease):
            "eclick and erelease are the press and release events"
            x1, y1 = eclick.xdata, eclick.ydata
            x2, y2 = erelease.xdata, erelease.ydata

            x_min = min(x1, x2)
            x_max = max(x1, x2)
            y_min = min(y1, y2)
            y_max = max(y1, y2)

            self.coordinates = [x_min, y_min, x_max, y_max]

        def confirmation(event):
            if event.key in ["enter"]:
                plt.close()

        def print_instructions():
            print(
                """Use the whole image (default) or select rectangular part
                of image for mean strain calculation.
                Confirm with `enter`.
                """
            )

        # set_gui_backend()
        plt.style.use("classic")
        plt.ioff()
        fig_1 = plt.figure(figsize=(10, 8))

        plt.set_cmap("RdYlBu_r")
        current_cmap = matplotlib.cm.get_cmap()
        current_cmap.set_bad(color="grey")

        # fig_1.subplots_adjust(0.05, 0.05, 0.98, 0.98, 0.1)
        axes_1 = plt.subplot2grid((12, 4), (0, 0), rowspan=12, colspan=4)
        image_1 = axes_1.imshow(self.image, interpolation="none")

        fig_1.colorbar(
            image_1, ax=axes_1, fraction=0.046, pad=0.04, orientation="horizontal"
        )

        selector = RectangleSelector(
            axes_1,
            line_select_callback,
            drawtype="box",
            useblit=True,
            button=[1, 3],  # don't use middle button
            minspanx=5,
            minspany=5,
            spancoords="pixels",
            interactive=True,
        )

        _widgets = [selector]
        print_instructions()

        fig_1.canvas.mpl_connect("key_press_event", confirmation)

        plt.show(block=True)


def get_true_stress(
    force_in_N, true_strain_perpendicular, specimen_cross_section_in_mm2
):
    true_stress = force_in_N / (
        specimen_cross_section_in_mm2 * np.exp(2.0 * true_strain_perpendicular)
    )

    return true_stress


def get_true_strain(def_grad):
    """
    calculation of the elements of the true strain tensor
    E_0 = 1./2. * log(C)
    where C is the right Cauchy-Green tensor
    C = F^T * F
    """
    def_grad_dxdx = def_grad[:, :, :, 0]
    def_grad_dxdy = def_grad[:, :, :, 1]
    def_grad_dydx = def_grad[:, :, :, 2]
    def_grad_dydy = def_grad[:, :, :, 3]

    true_strain_xx = 1.0 / 2.0 * np.log(def_grad_dxdx ** 2 + def_grad_dydx ** 2)

    true_strain_yy = 1.0 / 2.0 * np.log(def_grad_dydy ** 2 + def_grad_dxdy ** 2)

    true_strain_xy = (
        1.0
        / 2.0
        * np.log(def_grad_dxdx * def_grad_dxdy + def_grad_dydy * def_grad_dydx)
    )

    (nbr_files, nbr_x, nbr_y, nbr_components_def_grad) = def_grad.shape
    true_strain = np.zeros((nbr_files, nbr_x, nbr_y, 3), dtype=np.float64)

    true_strain[:, :, :, 0] = true_strain_xx
    true_strain[:, :, :, 1] = true_strain_yy
    true_strain[:, :, :, 2] = true_strain_xy

    return true_strain
