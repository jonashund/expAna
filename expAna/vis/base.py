import expAna


def stress(experiment_list=None, keep_offset=True, set_failure=False, dic_system=None):
    expAna.vis.base_stress.main(
        experiment_list=experiment_list,
        keep_offset=keep_offset,
        set_failure=set_failure,
        dic_system=dic_system,
    )


def force(
    experiment_list=None, keep_offset=True, set_failure=False,
):
    expAna.vis.base_force.main(
        experiment_list=experiment_list,
        keep_offset=keep_offset,
        set_failure=set_failure,
    )
