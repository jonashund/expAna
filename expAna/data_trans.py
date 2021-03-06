import os
import math
import dill
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import istra2py

import expAna

from PIL import Image


class Project(object):
    def __init__(
        self,
        name,
        istra_acquisition_dir=None,
        export2tif_dir=None,
        dic_results_dir=None,
        expAna_data_dir=None,
        expAna_docu_dir=None,
        expAna_plots_dir=None,
    ):
        self.name = name
        self.experiments = {}
        self.export2tif_dir = export2tif_dir
        self.istra_acquisition_dir = istra_acquisition_dir
        self.dic_results_dir = dic_results_dir
        self.expAna_docu_dir = expAna_docu_dir
        self.expAna_data_dir = expAna_data_dir
        self.expAna_plots_dir = expAna_plots_dir

    def add_experiment(self, test):
        if isinstance(test, (Experiment)):
            self.experiments.update({test.name: test})
        else:
            raise TypeError("Test should be of type `Experiment`.")


class Experiment(object):
    def __init__(self, name):
        self.name = name

    def read_and_convert_istra_images(self, istra_acquisition_dir, export2tif_dir):

        image_reader = istra2py.Reader(
            path_dir_acquisition=os.path.join(istra_acquisition_dir, self.name),
            verbose=False,
        )

        image_reader.read()
        current_export_dir = os.path.join(export2tif_dir, self.name)
        os.makedirs(current_export_dir, exist_ok=True)

        self.image_count = len(image_reader.acquisition.images)
        # save force and displacement
        self.reaction_force = image_reader.acquisition.traverse_force
        self.traverse_displ = image_reader.acquisition.traverse_displ * 10.0

        # export images
        for img in range(self.image_count):
            filename = f"{self.name}_img_{img}.tif"
            current_image = Image.fromarray(image_reader.acquisition.images[img])

            current_image.save(os.path.join(current_export_dir, filename))

            if img == 0:
                self.ref_image = image_reader.acquisition.images[img]

    def read_istra_evaluation(self, istra_acquisition_dir, istra_evaluation_dir):

        image_reader = istra2py.Reader(
            path_dir_acquisition=os.path.join(istra_acquisition_dir, self.name),
            path_dir_evaluation=os.path.join(istra_evaluation_dir, self.name + "CORN1"),
            verbose=False,
        )

        image_reader.read(identify_images_evaluation=True)

        self.ref_image = image_reader.acquisition.images[0]

        self.image_count = np.shape(image_reader.evaluation.mask)[0]

        # save exported force and displacement
        self.reaction_force = image_reader.evaluation.traverse_force
        self.traverse_displ = image_reader.evaluation.traverse_displ * 10.0
        # save exported fields from evaluation
        self.coords = image_reader.evaluation.x
        self.pix_coords = image_reader.evaluation.pix_x
        self.def_grad = image_reader.evaluation.def_grad
        self.mask = image_reader.evaluation.mask

    def get_image(self, frame_no, istra_acquisition_dir):
        image_reader = istra2py.Reader(
            path_dir_acquisition=os.path.join(istra_acquisition_dir, self.name),
            verbose=False,
        )
        image_reader.read()

        return image_reader.acquisition.images[frame_no]

    def set_documentation_data(self, experiment_data):

        if experiment_data["dic"] == 1:
            experiment_data["dic"] = "yes"
        else:
            experiment_data["dic"] = "no"

        self.documentation_data = {}

        for feature in experiment_data.index:
            self.documentation_data.update({feature: experiment_data[feature]})

    def slenderise(self):
        keep = ["documentation_data", "name", "gauge_results"]

        discard = [x for x in vars(self).keys() if x not in keep]

        for attribute in discard:
            delattr(self, attribute)

    def plot_true_stress(
        self,
        out_dir=os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "expAna_plots"
        ),
        skip_tex=False,
    ):

        os.makedirs(out_dir, exist_ok=True)

        x_data = self.gauge_results["true_strain_image_x"]
        y_data = self.gauge_results["true_stress_in_MPa"]

        fig_1, axes_1 = expAna.plot.style_true_stress(
            x_lim=1.0, y_lim=1.1 * y_data.max(), skip_tex=skip_tex
        )

        axes_1.plot(
            x_data, y_data, label=f"{self.name}", linewidth=1.0, zorder=1,
        )
        fig_1.tight_layout()
        plt.savefig(os.path.join(out_dir, self.name + "_stress_strain.pdf",))
        fig_1.set_size_inches(12, 9)
        fig_1.suptitle(f"{self.name}", fontsize=12)
        fig_1.tight_layout()
        plt.savefig(os.path.join(out_dir, self.name + "_stress_strain.png",))

        plt.close()

    def plot_volume_strain(
        self,
        out_dir=os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "expAna_plots"
        ),
        skip_tex=False,
    ):

        os.makedirs(out_dir, exist_ok=True)

        x_data = self.gauge_results["true_strain_image_x"]
        y_data = self.gauge_results["volume_strain"]

        fig_1, axes_1 = expAna.plot.style_vol_strain(
            x_lim=1.0, y_lim=1.1 * y_data.max(), skip_tex=skip_tex
        )

        axes_1.plot(
            x_data, y_data, label=f"{self.name}", linewidth=1.0, zorder=1,
        )
        fig_1.tight_layout()
        plt.savefig(os.path.join(out_dir, self.name + "_vol_strain.pdf",))
        fig_1.set_size_inches(12, 9)
        fig_1.suptitle(f"{self.name}", fontsize=12)
        fig_1.tight_layout()
        plt.savefig(os.path.join(out_dir, self.name + "_vol_strain.png",))

        plt.close()

    def plot_force_displ(
        self,
        out_dir=os.path.join(
            os.path.abspath(os.path.dirname(__file__)), "..", "expAna_plots"
        ),
        skip_tex=False,
    ):

        os.makedirs(out_dir, exist_ok=True)

        x_data = self.data_instron["displacement_in_mm"]
        y_data = self.data_instron["force_in_kN"]

        fig_1, axes_1 = expAna.plot.style_force_displ(
            x_lim=math.ceil(x_data.max()), y_lim=1.1 * y_data.max(), skip_tex=skip_tex
        )
        fig_1.set_size_inches(5, 2.5)
        axes_1.plot(
            x_data, y_data, label=f"{self.name}", linewidth=1.0, zorder=1,
        )
        fig_1.tight_layout()
        plt.savefig(os.path.join(out_dir, self.name + "_force_displ.pdf",))
        fig_1.set_size_inches(12, 9)
        fig_1.suptitle(f"{self.name}", fontsize=12)
        fig_1.tight_layout()
        plt.savefig(os.path.join(out_dir, self.name + "_force_displ.png",))

        plt.close()


def export_one_curve_as_df(x_vals, y_vals, out_dir=".", out_filename="curve.pickle"):

    dataframe = pd.DataFrame(
        data=np.ma.concatenate(
            (x_vals.reshape(len(x_vals), 1), y_vals.reshape(len(y_vals), 1)), axis=1
        ),
        columns=["x_vals", "y_vals"],
    )

    with open(os.path.join(out_dir, out_filename), "wb",) as myfile:
        dill.dump(dataframe, myfile)


def import_one_curve_as_arrays(data_dir, filename):

    with open(os.path.join(data_dir, filename), "rb",) as myfile:
        dataframe = dill.load(myfile)

    return dataframe["x_vals"].to_numpy(), dataframe["y_vals"].to_numpy()


def export_analysis(analysis, out_dir=None, out_filename="analysis.pickle"):
    if out_dir is None:
        out_dir = os.path.join(os.getcwd(), "expAna_data")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, out_filename), "wb",) as myfile:
        dill.dump(analysis, myfile)


def import_analysis(data_dir, filename):
    with open(os.path.join(data_dir, filename), "rb",) as myfile:
        analysis = dill.load(myfile)

    return analysis
