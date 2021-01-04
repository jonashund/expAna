import os
import dill
import numpy as np
import expAna

from natsort import natsorted


def force(
    compare,
    select=None,
    experiment_list=None,
    ignore_list=None,
    x_lim=4.0,
    displ_shift=None,
):
    expAna.vis.analysis_force.main(
        compare,
        select=select,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
        x_lim=x_lim,
        displ_shift=displ_shift,
    )


def vol_strain(
    compare,
    select=None,
    experiment_list=None,
    ignore_list=None,
    dic_system="istra",
):
    expAna.vis.analysis_vol_strain.main(
        compare,
        select=select,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
        dic_system=dic_system,
    )


def stress(
    compare,
    select=None,
    experiment_list=None,
    ignore_list=None,
    dic_system="istra",
):
    expAna.vis.analysis_stress.main(
        compare,
        select=select,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
        dic_system=dic_system,
    )


def poissons_ratio(
    compare,
    select=None,
    experiment_list=None,
    ignore_list=None,
    dic_system="istra",
):
    expAna.vis.analysis_poissons_ratio.main(
        compare,
        select=select,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
        dic_system=dic_system,
    )


class Analysis(object):
    def __init__(self, type):
        self.type = type

    def setup(
        self, exp_data_dir, compare, select=None, experiment_list=None, ignore_list=None
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
                        os.path.join(vis_export_dir, test_dir + "_expAna.pickle"),
                        "rb",
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

        self.export_material = export_material_dict[self.material]

        if select is None:
            self.export_prefix = (
                f"{self.export_material}_{self.type}_{self.compare_key}"
            )
        else:
            self.export_prefix = f"{self.export_material}_{self.type}_{self.select_key}_{self.select_value}_{self.compare_key}"

    def compute_data_force(self, displ_shift):
        for compare_value in self.compare_values:
            displacements = []
            forces = []
            # create list of arrays with x and y values
            for experiment_name in self.dict[compare_value]["experiment_list"]:
                if displ_shift is not None:
                    self.project.experiments[
                        experiment_name
                    ].data_instron = expAna.vis.plot.shift_columns(
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

            # TO DO:
            # for each experiment
            # get index of last positive value in "force_in_kN"
            # cut "displacement_in_mm" and "force_in_kN" at this index
            # WHY:
            # do not plot curves after specimen failure

            # interpolate every force displacement curve to an x-axis with equally spaced points
            # set spacing dependent on maximum x-value found in all x arrays

            max_x = max([max(displacements[i]) for i in range(len(displacements))])
            interval = max_x / 500
            mean_displ = np.arange(start=0.0, stop=max_x, step=interval)
            for i, strain in enumerate(displacements):
                displacements[i], forces[i] = expAna.calc.interpolate_curve(
                    strain, forces[i], interval
                )

            # compute the mean curve as long as at least three values are available
            mean_force, sem_force, force_indices = expAna.calc.get_mean_and_sem(forces)

            self.dict[compare_value]["mean_displ"] = mean_displ
            self.dict[compare_value]["mean_force"] = mean_force
            self.dict[compare_value]["sem_force"] = sem_force
            self.dict[compare_value]["force_indices"] = force_indices
            self.dict[compare_value]["displacements"] = displacements
            self.dict[compare_value]["forces"] = forces

            self.dict[compare_value].update(
                {"max_force": np.array(forces, dtype=object)[force_indices][-1].max()}
            )

    def compute_data_stress(
        self,
    ):
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
            mean_strain = np.arange(start=0.0, stop=max_x, step=interval)
            for i, strain in enumerate(true_strains):
                true_strains[i], true_stresses[i] = expAna.calc.interpolate_curve(
                    strain, true_stresses[i], interval
                )
            # compute the mean curve as long as at least three values are available
            mean_stress, sem_stress, stress_indices = expAna.calc.get_mean_and_sem(
                true_stresses
            )

            self.dict[compare_value]["mean_strain"] = mean_strain
            self.dict[compare_value]["mean_stress"] = mean_stress
            self.dict[compare_value]["sem_stress"] = sem_stress
            self.dict[compare_value]["stress_indices"] = stress_indices
            self.dict[compare_value]["strains"] = true_strains
            self.dict[compare_value]["stresses"] = true_stresses

            self.dict[compare_value].update(
                {
                    "max_stress": np.array(true_stresses, dtype=object)[stress_indices][
                        -1
                    ].max()
                }
            )

    def compute_data_vol_strain(
        self,
    ):
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
            mean_strain = np.arange(start=0.0, stop=max_x, step=interval)
            for i, strain in enumerate(true_strains):
                true_strains[i], vol_strains[i] = expAna.calc.interpolate_curve(
                    strain, vol_strains[i], interval
                )
            # compute the mean curve as long as at least three values are available
            (
                mean_vol_strain,
                sem_vol_strain,
                vol_strain_indices,
            ) = expAna.calc.get_mean_and_sem(vol_strains)

            self.dict[compare_value]["mean_strain"] = mean_strain
            self.dict[compare_value]["mean_vol_strain"] = mean_vol_strain
            self.dict[compare_value]["sem_vol_strain"] = sem_vol_strain
            self.dict[compare_value]["vol_strain_indices"] = vol_strain_indices
            self.dict[compare_value]["strains"] = true_strains
            self.dict[compare_value]["vol_strains"] = vol_strains

            self.dict[compare_value].update(
                {
                    "max_vol_strain": np.array(vol_strains, dtype=object)[
                        vol_strain_indices
                    ][-1].max()
                }
            )

    def compute_data_poissons_ratio(
        self,
    ):
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

            # interpolate every curve to an x-axis with equally spaced points
            # set spacing dependent on maximum x-value found in all x arrays

            max_x = max([max(true_strains[i]) for i in range(len(true_strains))])
            interval = max_x / 500
            mean_strain = np.arange(start=0.0, stop=max_x, step=interval)
            for i, strain in enumerate(true_strains):
                true_strains[i], poissons_ratios[i] = expAna.calc.interpolate_curve(
                    strain, poissons_ratios[i], interval
                )

            # compute the mean curve as long as at least three values are available
            (
                mean_poissons_ratio,
                sem_poissons_ratio,
                poissons_ratio_indices,
            ) = expAna.calc.get_mean_and_sem(poissons_ratios)

            self.dict[compare_value]["mean_strain"] = mean_strain
            self.dict[compare_value]["mean_poissons_ratio"] = mean_poissons_ratio
            self.dict[compare_value]["sem_poissons_ratio"] = sem_poissons_ratio
            self.dict[compare_value]["poissons_ratio_indices"] = poissons_ratio_indices
            self.dict[compare_value]["strains"] = true_strains
            self.dict[compare_value]["poissons_ratios"] = poissons_ratios
            self.dict[compare_value].update(
                {
                    "max_poissons_ratio": np.array(poissons_ratios, dtype=object)[
                        poissons_ratio_indices
                    ][-1].max()
                }
            )
