import os
import dill
import expAna

from natsort import natsorted


def force(compare, select=None, experiment_list=None, ignore_list=None, x_lim=None):
    expAna.vis.analysis_force.main(
        compare,
        select=select,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
        x_lim=x_lim,
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
            assert False, "Experiment list is empty for filter_key specified."

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
        self.compare_values = compare_values
