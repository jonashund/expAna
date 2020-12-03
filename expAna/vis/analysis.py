import expAna


def force(
    filter_key, filter_value=None, experiment_list=None, ignore_list=None, x_lim=None
):
    expAna.vis.analysis_force.main(
        filter_key,
        filter_value=filter_value,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
        x_lim=x_lim,
    )


def stress(
    filter_key,
    filter_value=None,
    experiment_list=None,
    ignore_list=None,
    dic_system="istra",
):
    expAna.vis.analysis_stress.main(
        filter_key,
        filter_value=filter_value,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
        dic_system=dic_system,
    )


def vol_strain(
    filter_key,
    filter_value=None,
    experiment_list=None,
    ignore_list=None,
    dic_system="istra",
):
    expAna.vis.analysis_vol_strain.main(
        filter_key,
        filter_value=filter_value,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
        dic_system=dic_system,
    )


def poissons_ratio(
    filter_key,
    filter_value=None,
    experiment_list=None,
    ignore_list=None,
    dic_system="istra",
):
    expAna.vis.analysis_poissons_ratio.main(
        filter_key,
        filter_value=filter_value,
        experiment_list=experiment_list,
        ignore_list=ignore_list,
        dic_system=dic_system,
    )
