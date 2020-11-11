import expAna


def force(
    filter_key, filter_value=None, experiment_list=None, ignore_list=None,
):
    expAna.vis.analysis_force.main(
        filter_key, filter_value=None, experiment_list=None, ignore_list=None,
    )


def stress(
    filter_key, filter_value=None, experiment_list=None, ignore_list=None,
):
    expAna.vis.analysis_stress.main(
        filter_key, filter_value=None, experiment_list=None, ignore_list=None,
    )
