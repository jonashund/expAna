import os
import dill
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import expAna

from natsort import natsorted

# from scipy.signal import savgol_filter


def force(
    compare,
    select=None,
    experiment_list=None,
    ignore_list=None,
    x_lim=4.0,
    displ_shift=None,
):
    work_dir = os.getcwd()
    instron_data_dir = os.path.join(work_dir, "data_instron")
    vis_export_dir = os.path.join(work_dir, "visualisation")

    os.makedirs(vis_export_dir, exist_ok=True)

    analysis = expAna.analysis.Analysis(type="force")
    analysis.setup(
        exp_data_dir=instron_data_dir,
        compare=compare,
        select=select,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
    )
    ####################################################################################
    # COMPUTE AVERAGE CURVES, ETC.
    ####################################################################################

    analysis.compute_data_force(displ_shift)

    expAna.data_trans.export_analysis(
        analysis,
        out_dir=vis_export_dir,
        out_filename=f"analysis_{analysis.export_prefix}.pickle",
    )

    ####################################################################################
    # PLOT
    ####################################################################################

    analysis.plot_data(vis_export_dir=vis_export_dir, x_lim=x_lim)


def vol_strain(
    compare, select=None, experiment_list=None, ignore_list=None, dic_system="istra",
):
    work_dir = os.getcwd()
    if dic_system == "istra":
        exp_data_dir = os.path.join(work_dir, "data_istra_evaluation")
        vis_export_dir = os.path.join(work_dir, "visualisation", "istra")
    elif dic_system == "muDIC":
        exp_data_dir = os.path.join(work_dir, "data_muDIC")
        vis_export_dir = os.path.join(work_dir, "visualisation", "muDIC")
    else:
        raise InputError(
            "-dic", f"`{dic_system}` is not a valid value for argument `dic_system`"
        )

    os.makedirs(vis_export_dir, exist_ok=True)

    analysis = expAna.analysis.Analysis(type="vol_strain")
    analysis.setup(
        exp_data_dir=exp_data_dir,
        compare=compare,
        select=select,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
    )

    ####################################################################################
    # COMPUTE AVERAGE CURVES, ETC.
    ####################################################################################

    analysis.compute_data_vol_strain()

    ####################################################################################
    # EXPORT ANALYSIS
    ####################################################################################

    expAna.data_trans.export_analysis(
        analysis,
        out_dir=vis_export_dir,
        out_filename=f"analysis_{analysis.export_prefix}.pickle",
    )

    ####################################################################################
    # PLOT
    ####################################################################################

    analysis.plot_data(vis_export_dir)


def stress(
    compare, select=None, experiment_list=None, ignore_list=None, dic_system="istra",
):
    work_dir = os.getcwd()
    if dic_system == "istra":
        exp_data_dir = os.path.join(work_dir, "data_istra_evaluation")
        vis_export_dir = os.path.join(work_dir, "visualisation", "istra")
    elif dic_system == "muDIC":
        exp_data_dir = os.path.join(work_dir, "data_muDIC")
        vis_export_dir = os.path.join(work_dir, "visualisation", "muDIC")
    else:
        raise InputError(
            "-dic", f"`{dic_system}` is not a valid value for argument `dic_system`"
        )

    os.makedirs(vis_export_dir, exist_ok=True)

    analysis = expAna.analysis.Analysis(type="stress")
    analysis.setup(
        exp_data_dir=exp_data_dir,
        compare=compare,
        select=select,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
    )
    ####################################################################################
    # COMPUTE AVERAGE CURVES, ETC.
    ####################################################################################

    analysis.compute_data_stress()

    ####################################################################################
    # EXPORT ANALYSIS
    ####################################################################################

    expAna.data_trans.export_analysis(
        analysis,
        out_dir=vis_export_dir,
        out_filename=f"analysis_{analysis.export_prefix}.pickle",
    )

    ####################################################################################
    # PLOT
    ####################################################################################

    analysis.plot_data(vis_export_dir)


def poissons_ratio(
    compare, select=None, experiment_list=None, ignore_list=None, dic_system="istra",
):
    work_dir = os.getcwd()
    if dic_system == "istra":
        exp_data_dir = os.path.join(work_dir, "data_istra_evaluation")
        vis_export_dir = os.path.join(work_dir, "visualisation", "istra")
    elif dic_system == "muDIC":
        exp_data_dir = os.path.join(work_dir, "data_muDIC")
        vis_export_dir = os.path.join(work_dir, "visualisation", "muDIC")
    else:
        raise InputError(
            "-dic", f"`{dic_system}` is not a valid value for argument `dic_system`"
        )

    os.makedirs(vis_export_dir, exist_ok=True)

    analysis = expAna.analysis.Analysis(type="poissons_ratio")
    analysis.setup(
        exp_data_dir=exp_data_dir,
        compare=compare,
        select=select,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
    )
    ####################################################################################
    # COMPUTE AVERAGE CURVES, ETC.
    ####################################################################################

    analysis.compute_data_poissons_ratio()

    ####################################################################################
    # EXPORT ANALYSIS
    ####################################################################################

    expAna.data_trans.export_analysis(
        analysis,
        out_dir=vis_export_dir,
        out_filename=f"analysis_{analysis.export_prefix}.pickle",
    )

    ####################################################################################
    # PLOT
    ####################################################################################

    analysis.plot_data(vis_export_dir=vis_export_dir)

    ####################################################################################


class Analysis(object):
    def __init__(self, type):
        self.type = type

    def setup(
        self,
        exp_data_dir,
        compare,
        select=None,
        experiment_list=None,
        ignore_list=None,
    ):
        if experiment_list is None:
            experiment_list = list()
            print(
                f"No experiments passed. Will search for folders named `Test*` in {exp_data_dir}."
            )
            for path, directories, files in os.walk(exp_data_dir):
                for test_dir in directories:
                    if str(test_dir[:5] == "Test"):
                        experiment_list.append(test_dir)
        else:
            pass

        if ignore_list is not None:
            for experiment in ignore_list:
                experiment_list.remove(experiment)

        experiment_list = natsorted(experiment_list)

        analysis_dict = {}

        if select is not None:
            self.select_key = select[0]
            select_value = select[1]
            if type(select_value) is not str:
                select_value = str(select_value)
            self.select_value = select_value.replace(" ", "_")
            analysis_project = expAna.data_trans.Project(
                name=f"analysis_select_{self.select_key}_is_{self.select_value}_compare_{compare}"
            )
        else:
            analysis_project = expAna.data_trans.Project(
                name=f"analysis_compare_{compare}"
            )

        # load the experiments
        for test_dir in experiment_list:
            if self.type == "force":
                work_dir = os.getcwd()
                expDoc_data_dir = os.path.join(work_dir, "data_expDoc", "python")
                vis_export_dir = os.path.join(work_dir, "visualisation")
                try:
                    with open(
                        os.path.join(expDoc_data_dir, test_dir + "_expDoc.pickle"),
                        "rb",
                    ) as myfile:
                        experiment = dill.load(myfile)
                except:
                    assert False, f"""
                Warning:
                No documentation data found for {test_dir}!
                Document your experiments properly using expDoc before using expAna.
                """
                # search for expAna data
                try:
                    with open(
                        os.path.join(vis_export_dir, test_dir + "_expAna.pickle"), "rb",
                    ) as myfile:
                        experiment = dill.load(myfile)
                except:
                    pass

            else:
                with open(
                    os.path.join(exp_data_dir, test_dir, test_dir + "_expAna.pickle"),
                    "rb",
                ) as myfile:
                    experiment = dill.load(myfile)

            if select is not None:
                if str(experiment.documentation_data[select[0]]) == str(select[1]):
                    analysis_project.add_experiment(experiment)
                else:
                    pass
            else:
                analysis_project.add_experiment(experiment)

        if not bool(analysis_project.experiments.items()):
            assert False, "Experiment list is empty for options specified."

        # compile list of different values for compare key
        compare_values = []
        for experiment_name, experiment_data in analysis_project.experiments.items():
            compare_values.append(experiment_data.documentation_data[compare])
            # remove experiments with no value for given key
        compare_values = list(filter(None, compare_values))
        for compare_value in set(compare_values):
            value_count = compare_values.count(compare_value)
            if value_count < 3:
                for i in range(value_count):
                    compare_values.remove(compare_value)
            else:
                pass
        # remove duplicates from list
        compare_values = set(compare_values)

        compare_values = natsorted(compare_values)

        for compare_value in compare_values:
            analysis_dict[compare_value] = {}
            analysis_dict[compare_value]["experiment_list"] = []
            for (
                experiment_name,
                experiment_data,
            ) in analysis_project.experiments.items():
                if experiment_data.documentation_data[compare] == compare_value:
                    analysis_dict[compare_value]["experiment_list"].append(
                        experiment_name
                    )

        self.project = analysis_project
        self.dict = analysis_dict
        self.specimen_type = self.project.experiments[
            list(self.project.experiments.keys())[0]
        ].documentation_data["specimen_type"]
        self.compare_key = compare
        self.compare_values = compare_values

        ################################################################################
        # PREPARE FOR EXPORT
        ################################################################################
        # some string replacement for underscores in filenames
        self.title_key = self.compare_key.replace("_", " ")
        self.material = self.project.experiments[
            list(self.project.experiments.keys())[0]
        ].documentation_data["material"]

        export_material_dict = {
            "Bayblend T45": "pcAbs_4555",
            "Bayblend T65": "pcAbs_6040",
            "Bayblend T85": "pcAbs_7030",
        }
        export_specimen_type_dict = {1: "uniax_tension", 2: "sent"}

        if self.material in list(export_material_dict.keys()):
            self.export_material = export_material_dict[self.material]
        else:
            self.export_material = self.material.replace("_", " ")

        if self.specimen_type in list(export_specimen_type_dict.keys()):
            self.export_specimen_type = export_specimen_type_dict[self.specimen_type]
        else:
            self.export_specimen_type = str(self.specimen_type).replace("_", " ")

        if select is None:
            self.export_prefix = f"{self.export_material}_{self.export_specimen_type}_{self.type}_{self.compare_key}"
        else:
            self.export_prefix = f"{self.export_material}_{self.export_specimen_type}_{self.type}_{self.select_key}_{self.select_value}_{self.compare_key}"

    def compute_data_force(self, displ_shift):
        for compare_value in self.compare_values:
            displacements = []
            forces = []
            # create list of arrays with x and y values
            for experiment_name in self.dict[compare_value]["experiment_list"]:
                if displ_shift is not None:
                    self.project.experiments[
                        experiment_name
                    ].data_instron = expAna.plot.shift_columns(
                        self.project.experiments[experiment_name].data_instron,
                        "displacement_in_mm",
                        displ_shift,
                    )
                else:
                    pass
                displacements.append(
                    self.project.experiments[experiment_name]
                    .data_instron["displacement_in_mm"]
                    .to_numpy()
                )
                forces.append(
                    self.project.experiments[experiment_name]
                    .data_instron["force_in_kN"]
                    .to_numpy()
                )

                if self.specimen_type == 1:
                    for i, force in enumerate(forces):
                        idx_fail = np.argwhere(force > 0.1).max()
                        forces[i] = forces[i][: idx_fail + 2]
                        forces[i][-2:] = 0.0
                        displacements[i] = displacements[i][: idx_fail + 2]
                        displacements[i][-2] = displacements[i][-2] + 1e-3
                        displacements[i][-1] = displacements[i][-1] + 2e-3
                else:
                    for i, force in enumerate(forces):
                        idx_fail = np.argwhere(force > 0.07).max()
                        forces[i] = forces[i][: idx_fail + 2]
                        forces[i][-1] = 0.0
                        displacements[i] = displacements[i][: idx_fail + 2]

            # interpolate every force displacement curve to an x-axis with equally spaced points
            # set spacing dependent on maximum x-value found in all x arrays

            max_x = max([max(displacements[i]) for i in range(len(displacements))])
            interval = max_x / 10000
            # interval = max_x / 500
            x_mean = np.arange(start=0.0, stop=max_x, step=interval)
            for i, strain in enumerate(displacements):
                displacements[i], forces[i] = expAna.calc.interpolate_curve(
                    strain, forces[i], interval
                )

            # compute the mean curve as long as at least three values are available
            y_mean, y_sem, y_indices = expAna.calc.get_mean_and_sem(forces)

            x_mean = x_mean[: len(y_mean)]

            self.dict[compare_value]["x_mean"] = x_mean
            self.dict[compare_value]["y_mean"] = y_mean
            self.dict[compare_value]["y_sem"] = y_sem
            self.dict[compare_value]["y_indices"] = y_indices
            self.dict[compare_value]["xs"] = displacements
            self.dict[compare_value]["ys"] = forces

            self.dict[compare_value].update(
                {"y_max": np.array(forces, dtype=object)[y_indices][-1].max()}
            )

    def compute_data_stress(self,):
        for compare_value in self.compare_values:
            true_strains = []
            true_stresses = []
            # create list of arrays with x and y values
            for experiment_name in self.dict[compare_value]["experiment_list"]:
                true_strains.append(
                    self.project.experiments[experiment_name]
                    .gauge_results["true_strain_image_x"]
                    .to_numpy()
                )
                true_stresses.append(
                    self.project.experiments[experiment_name]
                    .gauge_results["true_stress_in_MPa"]
                    .to_numpy()
                )

            # interpolate every stress strain curve to an x-axis with equally spaced points
            # set spacing dependent on maximum x-value found in all x arrays

            max_x = max([max(true_strains[i]) for i in range(len(true_strains))])
            interval = max_x / 500
            x_mean = np.arange(start=0.0, stop=max_x, step=interval)
            for i, strain in enumerate(true_strains):
                true_strains[i], true_stresses[i] = expAna.calc.interpolate_curve(
                    strain, true_stresses[i], interval
                )
            # compute the mean curve as long as at least three values are available
            y_mean, y_sem, y_indices = expAna.calc.get_mean_and_sem(true_stresses)

            x_mean = x_mean[: len(y_mean)]

            self.dict[compare_value]["x_mean"] = x_mean
            self.dict[compare_value]["y_mean"] = y_mean
            self.dict[compare_value]["y_sem"] = y_sem
            self.dict[compare_value]["y_indices"] = y_indices
            self.dict[compare_value]["xs"] = true_strains
            self.dict[compare_value]["ys"] = true_stresses

            self.dict[compare_value].update(
                {"y_max": np.array(true_stresses, dtype=object)[y_indices][-1].max()}
            )

    def compute_data_vol_strain(self,):
        for compare_value in self.compare_values:
            true_strains = []
            vol_strains = []
            # create list of arrays with x and y values
            for experiment_name in self.dict[compare_value]["experiment_list"]:
                true_strains.append(
                    self.project.experiments[experiment_name]
                    .gauge_results["true_strain_image_x"]
                    .to_numpy()
                )
                vol_strains.append(
                    self.project.experiments[experiment_name]
                    .gauge_results["volume_strain"]
                    .to_numpy()
                )

            # interpolate every curve to an x-axis with equally spaced points
            # set spacing dependent on maximum x-value found in all x arrays

            max_x = max([max(true_strains[i]) for i in range(len(true_strains))])
            interval = max_x / 500
            x_mean = np.arange(start=0.0, stop=max_x, step=interval)
            for i, strain in enumerate(true_strains):
                true_strains[i], vol_strains[i] = expAna.calc.interpolate_curve(
                    strain, vol_strains[i], interval
                )
            # compute the mean curve as long as at least three values are available
            (y_mean, y_sem, y_indices,) = expAna.calc.get_mean_and_sem(vol_strains)

            x_mean = x_mean[: len(y_mean)]

            self.dict[compare_value]["x_mean"] = x_mean
            self.dict[compare_value]["y_mean"] = y_mean
            self.dict[compare_value]["y_sem"] = y_sem
            self.dict[compare_value]["y_indices"] = y_indices
            self.dict[compare_value]["xs"] = true_strains
            self.dict[compare_value]["ys"] = vol_strains

            self.dict[compare_value].update(
                {"y_max": np.array(vol_strains, dtype=object)[y_indices][-1].max()}
            )

    def compute_data_poissons_ratio(self,):
        for compare_value in self.compare_values:
            true_strains = []
            poissons_ratios = []
            # create list of arrays with x and y values
            for experiment_name in self.dict[compare_value]["experiment_list"]:
                true_strains.append(
                    self.project.experiments[experiment_name]
                    .gauge_results["true_strain_image_x"]
                    .to_numpy()
                )
                poissons_ratios.append(
                    self.project.experiments[experiment_name]
                    .gauge_results["poissons_ratio"]
                    .to_numpy()
                )
                # poissons_ratios.append(
                #     savgol_filter(
                #         self.project.experiments[experiment_name]
                #         .gauge_results["poissons_ratio"]
                #         .to_numpy(),
                #         51,
                #         3,
                #     )
                # )

            # interpolate every curve to an x-axis with equally spaced points
            # set spacing dependent on maximum x-value found in all x arrays

            max_x = max([max(true_strains[i]) for i in range(len(true_strains))])
            interval = max_x / 500
            x_mean = np.arange(start=0.0, stop=max_x, step=interval)
            for i, strain in enumerate(true_strains):
                true_strains[i], poissons_ratios[i] = expAna.calc.interpolate_curve(
                    strain, poissons_ratios[i], interval
                )

            # compute the mean curve as long as at least three values are available
            (y_mean, y_sem, y_indices,) = expAna.calc.get_mean_and_sem(poissons_ratios)

            x_mean = x_mean[: len(y_mean)]

            self.dict[compare_value]["x_mean"] = x_mean
            self.dict[compare_value]["y_mean"] = y_mean
            self.dict[compare_value]["y_sem"] = y_sem
            self.dict[compare_value]["y_indices"] = y_indices
            self.dict[compare_value]["xs"] = true_strains
            self.dict[compare_value]["ys"] = poissons_ratios
            self.dict[compare_value].update(
                {"y_max": np.array(poissons_ratios, dtype=object)[y_indices][-1].max()}
            )

    def plot_data(self, vis_export_dir, x_lim=None, export_curves=False):
        fig_props = self.get_type_props()

        if self.type == "force":
            x_lim = x_lim
        else:
            x_lim = fig_props["x_lim"]

        # plot individual curves and averaged curves in one plot for each value
        for compare_value in self.compare_values:
            # remove spaces in string before export
            if type(compare_value) == str:
                export_value = compare_value.replace(" ", "_")
            else:
                export_value = str(compare_value)

            if export_curves:
                expAna.data_trans.export_one_curve_as_df(
                    x_vals=self.dict[compare_value]["x_mean"],
                    y_vals=self.dict[compare_value]["y_mean"],
                    out_dir=vis_export_dir,
                    out_filename=f"curve_avg_{self.export_prefix}_{export_value}.pickle",
                )
            else:
                pass

            if self.type == "poissons_ratio":
                y_lim = 0.5
            else:
                y_lim = 1.5 * self.dict[compare_value]["y_max"]

            fig_1, axes_1 = fig_props["fig_style"](
                x_lim=x_lim, y_lim=y_lim, width=6, height=4,
            )

            expAna.plot.add_curves_same_value(
                fig=fig_1,
                axes=axes_1,
                x_mean=self.dict[compare_value]["x_mean"],
                y_mean=self.dict[compare_value]["y_mean"],
                xs=np.array(self.dict[compare_value]["xs"], dtype=object)[
                    self.dict[compare_value]["y_indices"]
                ],
                ys=np.array(self.dict[compare_value]["ys"], dtype=object)[
                    self.dict[compare_value]["y_indices"]
                ],
                value=compare_value,
            )

            axes_1.legend(loc="upper left")

            fig_1.tight_layout()
            plt.savefig(
                os.path.join(
                    vis_export_dir, f"{self.export_prefix}_{export_value}.pdf",
                ),
                dpi=600,
            )
            plt.savefig(
                os.path.join(
                    vis_export_dir, f"{self.export_prefix}_{export_value}.png",
                ),
                dpi=600,
            )
            plt.close()

        ############################################################################
        # plot mean and CI curves in one plot for each "compare_value"
        for compare_value in self.compare_values:
            # remove spaces in string before export
            if type(compare_value) == str:
                export_value = compare_value.replace(" ", "_")
            else:
                export_value = str(compare_value)

            if export_curves:
                expAna.data_trans.export_one_curve_as_df(
                    x_vals=self.dict[compare_value]["x_mean"],
                    y_vals=self.dict[compare_value]["y_sem"],
                    out_dir=vis_export_dir,
                    out_filename=f"curve_sem_{self.export_prefix}_{export_value}.pickle",
                )
            else:
                pass

            if self.type == "poissons_ratio":
                y_lim = 10.0
            else:
                y_lim = 1.5 * self.dict[compare_value]["y_max"]

            fig_2, axes_2 = fig_props["fig_style"](
                x_lim=x_lim, y_lim=y_lim, width=6, height=4,
            )

            expAna.plot.add_mean_and_sem(
                fig=fig_2,
                axes=axes_2,
                x_mean=self.dict[compare_value]["x_mean"],
                y_mean=self.dict[compare_value]["y_mean"],
                y_error=1.96 * self.dict[compare_value]["y_sem"],
                value=compare_value,
            )

            axes_2.legend(loc="upper left")

            fig_2.tight_layout()
            plt.savefig(
                os.path.join(
                    vis_export_dir,
                    f"{self.export_prefix}_{export_value}_with_error.pdf",
                ),
                dpi=600,
            )
            plt.savefig(
                os.path.join(
                    vis_export_dir,
                    f"{self.export_prefix}_{export_value}_with_error.png",
                ),
                dpi=600,
            )

            plt.close()

        ################################################################################
        # comparison plot with mean and individual curves

        # get maximum y value for upper y-axis limit
        if self.type == "poissons_ratio":
            y_max = 0.5 / 1.5
        else:
            y_max = max(
                self.dict[compare_value]["y_max"]
                for compare_value in self.compare_values
            )
        fig_3, axes_3 = fig_props["fig_style"](
            x_lim=x_lim, y_lim=1.5 * y_max, width=6, height=4,
        )

        for compare_value in self.compare_values:
            expAna.plot.add_curves_same_value(
                fig=fig_3,
                axes=axes_3,
                x_mean=self.dict[compare_value]["x_mean"],
                y_mean=self.dict[compare_value]["y_mean"],
                xs=np.array(self.dict[compare_value]["xs"], dtype=object)[
                    self.dict[compare_value]["y_indices"]
                ],
                ys=np.array(self.dict[compare_value]["ys"], dtype=object)[
                    self.dict[compare_value]["y_indices"]
                ],
                value=compare_value,
            )

        axes_3.legend(loc="upper left")

        fig_3.tight_layout()
        plt.savefig(
            os.path.join(vis_export_dir, f"{self.export_prefix}_comparison.pdf"),
            dpi=600,
        )
        plt.savefig(
            os.path.join(vis_export_dir, f"{self.export_prefix}_comparison.png",),
            dpi=600,
        )
        plt.close()

        ################################################################################
        # comparison plot with mean and std curve

        fig_4, axes_4 = fig_props["fig_style"](
            x_lim=x_lim, y_lim=1.5 * y_max, width=6, height=4,
        )

        for compare_value in self.compare_values:
            expAna.plot.add_mean_and_sem(
                fig=fig_4,
                axes=axes_4,
                x_mean=self.dict[compare_value]["x_mean"],
                y_mean=self.dict[compare_value]["y_mean"],
                y_error=1.96 * self.dict[compare_value]["y_sem"],
                value=compare_value,
            )

        axes_4.legend(loc="upper left")

        fig_4.tight_layout()
        plt.savefig(
            os.path.join(
                vis_export_dir, f"{self.export_prefix}_comparison_with_error.pdf",
            ),
            dpi=600,
        )
        plt.savefig(
            os.path.join(
                vis_export_dir, f"{self.export_prefix}_comparison_with_error.png",
            ),
            dpi=600,
        )
        plt.close()

    def get_type_props(self,):
        type_props = {
            "force": {"fig_style": expAna.plot.style_force_displ},
            "stress": {
                "x_lim": 1.0,
                "y_lim": 100,
                "fig_style": expAna.plot.style_true_stress,
            },
            "vol_strain": {"x_lim": 1.0, "fig_style": expAna.plot.style_vol_strain,},
            "poissons_ratio": {
                "x_lim": 1.0,
                "fig_style": expAna.plot.style_poissons_ratio,
            },
        }
        return type_props[self.type]

    def get_max_mean(self, compare_value=None, x_min=None, x_max=None):
        """
        Method to get the max value of the mean curve, the index of the max value, and the sem at the max value
        The method takes three optional arguments:
            compare_value (default=None)    one of analysis.compare_values
                                            if None all compare_values are considered
            x_min (default=None)            lower bound of the considered interval
            x_max (default=None)            upper bound of the considered interval
        """

        df_columns = [f"{self.compare_key}", "x_max", "y_max", "y_sem", "idx"]
        out_data = []
        if compare_value is None:
            compare_values = self.compare_values
        else:
            compare_values = compare_value

        for compare_value in compare_values:
            mean_x_max, mean_y_max, idx_max = expAna.calc.curve_max(
                x=self.dict[compare_value]["x_mean"],
                y=self.dict[compare_value]["y_mean"],
                x_min=x_min,
                x_max=x_max,
            )
            out_data.append(
                [
                    compare_value,
                    mean_x_max,
                    mean_y_max,
                    self.dict[compare_value]["y_sem"][idx_max],
                    idx_max,
                ]
            )

        out_df = pd.DataFrame(out_data, columns=df_columns)
        return out_df

    def get_min_mean(self, compare_value=None, x_min=None, x_max=None):
        """
        Method to get the max value of the mean curve, the index of the max value, and the sem at the max value
        The method takes three optional arguments:
            compare_value (default=None)    one of analysis.compare_values
                                            if None all compare_values are considered
            x_min (default=None)            lower bound of the considered interval
            x_max (default=None)            upper bound of the considered interval
        """

        df_columns = [f"{self.compare_key}", "x_max", "y_max", "y_sem", "idx"]
        out_data = []
        if compare_value is None:
            compare_values = self.compare_values
        else:
            compare_values = compare_value

        for compare_value in compare_values:
            mean_x_min, mean_y_min, idx_min = expAna.calc.curve_min(
                x=self.dict[compare_value]["x_mean"],
                y=self.dict[compare_value]["y_mean"],
                x_min=x_min,
                x_max=x_max,
            )
            out_data.append(
                [
                    compare_value,
                    mean_x_min,
                    mean_y_min,
                    self.dict[compare_value]["y_sem"][idx_min],
                    idx_min,
                ]
            )

        out_df = pd.DataFrame(out_data, columns=df_columns)
        return out_df
