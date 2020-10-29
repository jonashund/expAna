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

    plt.style.use("seaborn")


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

        set_gui_backend()

        plt.ioff()
        fig_1 = plt.figure()
        plt.imshow(self.image)
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

        set_gui_backend()

        plt.ioff()
        fig_1 = plt.figure()

        fig_1.subplots_adjust(0.05, 0.05, 0.98, 0.98, 0.1)
        overview = plt.subplot2grid((12, 4), (0, 0), rowspan=12, colspan=4)
        overview.imshow(self.image)

        selector = RectangleSelector(
            overview,
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
    force_in_N, log_strain_perpendicular, specimen_cross_section_in_mm2
):
    true_stress = force_in_N / (
        specimen_cross_section_in_mm2 * np.exp(2.0 * log_strain_perpendicular)
    )

    return true_stress
