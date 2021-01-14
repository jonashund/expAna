import copy
import numpy as np
import matplotlib
import matplotlib.ticker as mtick
import matplotlib.pyplot as plt
import expAna


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
    def __init__(self, input_image_x_strain, input_image_y_strain):
        self.image_x = input_image_x_strain
        self.image_y = input_image_y_strain
        self.coordinates = [0, 0, self.image_x.shape[1], self.image_x.shape[0]]

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
                """
                Use the whole image (default) or select rectangular part
                of image for mean strain calculation.
                Confirm with `enter`.
                """
            )

        # set_gui_backend()
        plt.style.use("classic")
        plt.ioff()
        fig_1 = plt.figure(figsize=(12, 10))

        custom_cmap = copy.copy(matplotlib.cm.get_cmap("RdYlBu_r"))
        custom_cmap.set_bad(color="grey")

        axes_1 = plt.subplot2grid((2, 1), (0, 0))
        axes_2 = plt.subplot2grid((2, 1), (1, 0))
        image_x = axes_1.imshow(self.image_x, interpolation="none", cmap=custom_cmap)
        image_y = axes_2.imshow(self.image_y, interpolation="none", cmap=custom_cmap)

        axes_1.set_title(
            """Select rectangular part of visualised axial strain data for mean strain calculation.
                Confirm with `enter`.
            """
        )

        cbar_x = fig_1.colorbar(image_x, ax=axes_1)
        cbar_x.set_label("log. axial strain")
        cbar_y = fig_1.colorbar(image_y, ax=axes_2)
        cbar_y.set_label("log. transverse strain")

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


class FailureLocatorStress(object):
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
                if experiment.fail_strain.size > 0:
                    fail_idx = experiment.gauge_results[
                        experiment.gauge_results["true_strain_image_x"]
                        == experiment.fail_strain[0][0]
                    ].index[0]

                    experiment.gauge_results = experiment.gauge_results[:fail_idx]
                else:
                    print(
                        """
                    No valid point selected. Assuming no failure of specimen.
                    """
                    )
                plt.close()

        experiment.gauge_results = expAna.plot.remove_fail_rows(
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


class FailureLocatorForce(object):
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
            print("selected [[displacement(s)]][[force(s)]]:", event.pickx, event.picky)

            experiment.fail_displ = event.pickx
            experiment.fail_force = event.picky

        def confirmation(event):
            if event.key in ["enter"]:
                if experiment.fail_displ.size > 0:
                    fail_idx = experiment.data_instron[
                        experiment.data_instron["displacement_in_mm"]
                        == experiment.fail_displ[0][0]
                    ].index[0]

                    print(experiment.fail_displ)
                    print(experiment.fail_displ[0])
                    print(experiment.fail_displ[0][0])

                    experiment.data_instron = experiment.data_instron[:fail_idx]
                else:
                    print(
                        """
                    No valid point selected. Assuming no failure of specimen.
                    """
                    )
                plt.close()

        fig_1, axes_1 = plt.subplots(figsize=[12, 8])
        # axes styling
        axes_1.xaxis.set_minor_locator(mtick.AutoMinorLocator(2))
        # axes_1.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
        axes_1.yaxis.set_minor_locator(mtick.AutoMinorLocator(2))
        axes_1.grid(color="#929591", linewidth=0.33, zorder=0)

        axes_1.set_xlim(0, 1.1 * experiment.data_instron["displacement_in_mm"].max())
        axes_1.set_ylim(-0.1, 1.1 * experiment.data_instron["force_in_kN"].max())

        axes_1.set_xlabel(r"displacement $u$ [mm]")
        axes_1.set_ylabel(r"reaction force $F$ [kN]")
        axes_1.set_title(
            """
            Pick point of material failure (left mouse button).
            Confirm with `enter`.
            """
        )

        lineplot = axes_1.plot(
            experiment.data_instron["displacement_in_mm"],
            experiment.data_instron["force_in_kN"],
            label=f"{experiment.name}",
            linewidth=1.5,
            picker=line_picker,
        )
        fig_1.tight_layout()
        fig_1.canvas.mpl_connect("pick_event", onpick2)
        fig_1.canvas.mpl_connect("key_press_event", confirmation)

        plt.show()
