import platform
import copy
import numpy as np
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
        Could you please add it in gui_funcs.set_gui_backend()?
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
        fig_1.suptitle(
            """
            Enter tensile direction in image shown using arrow keys.
            Skip with enter to accept default direction: `horizontal`.
            """
        )
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
        current_cmap = copy.copy(matplotlib.cm.get_cmap("RdYlBu_r"))
        current_cmap.set_bad(color="grey")

        # fig_1.subplots_adjust(0.05, 0.05, 0.98, 0.98, 0.1)
        axes_1 = plt.subplot2grid((12, 4), (0, 0), rowspan=12, colspan=4)
        image_1 = axes_1.imshow(self.image, interpolation="none")

        axes_1.set_title(
            """Use the whole image (default) or select rectangular part
                        of image for mean strain calculation.
                                Confirm with `enter`.
            """
        )

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


class FailureLocator(object):
    def __gui__(self, experiment):
        def line_picker(line, mouseevent):
            """
            find the points within a certain distance from the mouseclick in
            data coords and attach some extra attributes, pickx and picky
            which are the data points that were picked
            """
            if mouseevent.xdata is None:
                return False, dict()
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            maxd = 0.05
            d = np.sqrt(
                (xdata - mouseevent.xdata) ** 2.0 + (ydata - mouseevent.ydata) ** 2.0
            )

            ind = np.nonzero(np.less_equal(d, maxd))
            if len(ind):
                pickx = np.take(xdata, ind)
                picky = np.take(ydata, ind)
                props = dict(ind=ind, pickx=pickx, picky=picky)
                return True, props
            else:
                return False, dict()

        def onpick2(event):
            print("selected [[strain(s)]][[stress(es)]]:", event.pickx, event.picky)
            experiment.fail_strain = event.pickx
            experiment.fail_stress = event.picky

        def confirmation(event):
            if event.key in ["enter"]:
                fail_idx = experiment.gauge_results[
                    experiment.gauge_results["true_strain_image_x"]
                    == experiment.fail_strain[0][0]
                ].index[0]

                experiment.gauge_results = experiment.gauge_results[:fail_idx]
                plt.close()

        import matplotlib.ticker as mtick
        import sys

        # doc funcs are located in instron2doc directory
        sys.path.append("../instron2doc/")

        import doc_funcs

        experiment.gauge_results = doc_funcs.remove_fail_rows(
            experiment.gauge_results, "reaction_force_in_kN", 0.0
        )

        fig_1, axes_1 = plt.subplots(figsize=[12, 8])
        # axes styling
        axes_1.xaxis.set_minor_locator(mtick.AutoMinorLocator(2))
        # axes_1.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        axes_1.yaxis.set_minor_locator(mtick.AutoMinorLocator(2))
        axes_1.grid(color="#929591", linewidth=0.33, zorder=0)

        axes_1.set_xlim(0, 1.1 * experiment.gauge_results["true_strain_image_x"].max())
        axes_1.set_ylim(0, 1.1 * experiment.gauge_results["true_stress_in_MPa"].max())

        axes_1.set_xlabel(r"log. strain $\varepsilon$ [-]")
        axes_1.set_ylabel(r"true stress $\sigma$ [MPa]")
        axes_1.set_title(
            """
            Pick point of material failure (left mouse button).
            Confirm with `enter`.
            """
        )

        lineplot = axes_1.plot(
            experiment.gauge_results["true_strain_image_x"],
            experiment.gauge_results["true_stress_in_MPa"],
            label=f"{experiment.name}",
            linewidth=1.5,
            picker=line_picker,
        )
        fig_1.tight_layout()
        fig_1.canvas.mpl_connect("pick_event", onpick2)
        fig_1.canvas.mpl_connect("key_press_event", confirmation)

        plt.show()
