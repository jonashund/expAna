#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run tests:
    python -m pytest
"""

import os
import sys
import pytest
import pathlib
import runpy

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))),)
import expAna

##############################################


@pytest.fixture
def project():
    return expAna.data_trans.Project("test_core")


@pytest.fixture
def experiment():
    return expAna.data_trans.Experiment("test_core")


@pytest.fixture
def analysis():
    return expAna.analysis.Analysis("stress")


class Test_init:
    def test_init_project(self, project):
        assert hasattr(project, "add_experiment")

    def test_init_experiment(self, experiment):
        assert hasattr(experiment, "read_and_convert_istra_images",)

    def test_init_analysis(self, analysis):
        assert hasattr(analysis, "setup")


################################
# Scripts


@pytest.mark.parametrize(
    "script",
    sorted(
        pathlib.Path(os.path.dirname(__file__), "..", "scripts").resolve().glob("*.py")
    ),
)
def test_script_execution(script):
    print(script)
    runpy.run_path(script)
    assert True


if __name__ == "__main__":
    pass
