import expAna


def stress(
    select=None,
    experiment_list=None,
    ignore_list=None,
    keep_offset=True,
    set_failure=False,
    dic_system="istra",
):
    expAna.vis.base_stress.main(
        select=select,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
        keep_offset=keep_offset,
        set_failure=set_failure,
        dic_system=dic_system,
    )


def force(
    select=None,
    experiment_list=None,
    displ_shift=None,
    set_failure=False,
):
    expAna.vis.base_force.main(
        select=select,
        experiment_list=experiment_list,
        displ_shift=displ_shift,
        set_failure=set_failure,
    )
