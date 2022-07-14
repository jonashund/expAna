import os
import subprocess
import dill
import numpy as np
import pandas as pd

import expAna


def main(project_name, verbose=False):
    excel2tex_and_py(project_name)
    doc_plot(project_name)

    bash_commands = """
    for texfile in ../expAna_docu/latex/Test*.tex
      do 
        path_and_filename=`echo "$texfile" | cut -d'.' -f 1-3`
        filename=`echo "$path_and_filename" | rev | cut -d'/' -f 1 | rev`
        
        echo "processing $path_and_filename.tex"
        
        cp ${path_and_filename}.tex ./current_test.tex
        pdflatex test_report.tex;
        mv test_report.pdf ../expAna_docu/${filename}.pdf
        rm ./current_test.tex
      done

    for i in toc aux bbl blg dvi ps log
    do
      ls *.$i | xargs rm --
    done
    """
    if verbose:
        subprocess.call(bash_commands, shell=True)
    else:
        subprocess.check_output(bash_commands, shell=True)


def doc_plot(project_name):

    work_dir = os.getcwd()
    expDoc_dir_python = os.path.join(work_dir, "..", "expAna_docu", "python")
    os.makedirs(expDoc_dir_python, exist_ok=True)
    vis_export_dir = os.path.join(work_dir, "..", "expAna_plots")
    os.makedirs(vis_export_dir, exist_ok=True)
    project_dir = os.path.join(work_dir, "..", "data_instron")

    excel_project_work_dir = os.path.join(project_dir, project_name + ".xlsx")

    project_dataframe = excel_project_template_to_dataframe(
        filepath=excel_project_work_dir
    )

    project_data = {}

    project_data.update(
        {
            "wave_matrix_project_name": project_name,
            "work_dir_to_data": project_dir,
            "project_dataframe": project_dataframe,
        }
    )

    for experiment_name in project_data["project_dataframe"].columns:
        try:
            try:
                with open(
                    os.path.join(expDoc_dir_python, experiment_name + "_docu.pickle",),
                    "rb",
                ) as myfile:
                    experiment = dill.load(myfile)
            except:
                experiment = expAna.data_trans.Experiment(experiment_name)

            experiment.data_instron = instron_to_dataframe(
                filepath=os.path.join(
                    project_dir, experiment_name, experiment_name + ".Stop.csv",
                )
            )

            experiment.data_instron = expAna.plot.remove_row_offset(
                experiment.data_instron, "force_in_kN", 0.0
            )

            experiment.data_instron = expAna.plot.remove_column_offset(
                experiment.data_instron, "displacement_in_mm"
            )

            experiment.plot_force_displ(out_dir=vis_export_dir)

            with open(
                os.path.join(expDoc_dir_python, experiment.name + "_docu.pickle"), "wb",
            ) as myfile:
                dill.dump(experiment, myfile)

        except:
            print(f"No {experiment_name} found in {project_name} project.")


def excel2tex_and_py(project_name):
    work_dir = os.getcwd()

    expDoc_dir_python = os.path.join(work_dir, "..", "expAna_docu", "python")
    os.makedirs(expDoc_dir_python, exist_ok=True)
    expDoc_dir_tex = os.path.join(work_dir, "..", "expAna_docu", "latex")
    os.makedirs(expDoc_dir_tex, exist_ok=True)
    project_dir = os.path.join(work_dir, "..", "data_instron")

    excel_project_filepath = os.path.join(project_dir, project_name + ".xlsx")

    project_data = excel_project_template_to_dataframe(filepath=excel_project_filepath)

    for experiment_name in project_data.columns:
        try:
            with open(
                os.path.join(expDoc_dir_python, experiment_name + "_docu.pickle"), "rb",
            ) as myfile:
                experiment = dill.load(myfile)
        except:
            experiment = expAna.data_trans.Experiment(experiment_name)

        experiment.set_documentation_data(project_data[experiment_name])
        current_report_work_dir = os.path.join(expDoc_dir_tex, experiment_name + ".tex")

        with open(current_report_work_dir, "w") as outputFile:
            outputFile.write(
                """
                    %-----------------------------USER INPUT---------------------------
                    % PROJECT PROPERTIES
                    \\def\\waveMatrixProject{{{0}}}
                    \\def\\tester{{{1}}}
                    %
                    % TEST SETUP
                    \\def\\testNumber{{{2}}}
                    \\def\\testTime{{{3}}}
                    \\def\\testDate{{{4}}}
                    \\def\\dic{{{5}}}
                    \\def\\crossheadSpeed{{{6}}} % [mm/s]
                    \\def\\waveMatrixMethod{{{7}}}
                    \\def\\clampingLength{{{8}}} % [mm]
                    \\def\\clampingTorque{{{9}}} % [Nm]
                    \\def\\testingMachine{{{10}}}
                    \\def\\loadCell{{{20}}} % serial no.
                    %
                    % SPECIMEN PROPERTIES
                    \\def\\specimenType{{{11}}} % 1: simple tension, 2: SENT
                    \\def\\material{{{12}}}
                    \\def\\specimenThickness{{{13}}} % [mm]
                    \\def\\specimenLength{{{14}}} % [mm]
                    \\def\\specimenWidth{{{15}}} % [mm]
                    \\def\\specimenOrientation{{{16}}}
                    \\def\\specimenPosition{{{17}}}
                    % in case of SENT specimen
                    \\def\\notchRadius{{{18}}} % [mm]
                    \\def\\notchDepth{{{19}}} % [mm]
                    % additional useful information
                    \\def\\testName{{{21}}}
                    \\def\\remark{{{22}}}
                    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
                """.format(
                    r"\_".join(project_name.split(r"_")),
                    experiment.documentation_data["tester"],
                    experiment.documentation_data["test_number"],
                    experiment.documentation_data["test_time"].strftime("%H:%M"),
                    experiment.documentation_data["test_date"].strftime("%d.%m.%Y"),
                    experiment.documentation_data["dic"],
                    experiment.documentation_data["crosshead_speed"],
                    r"\_".join(
                        experiment.documentation_data["testing_method"].split(r"_")
                    ),
                    experiment.documentation_data["clamping_length"],
                    experiment.documentation_data["clamping_torque"],
                    experiment.documentation_data["testing_machine"],
                    experiment.documentation_data["specimen_type"],
                    experiment.documentation_data["material"],
                    experiment.documentation_data["specimen_thickness"],
                    experiment.documentation_data["specimen_length"],
                    experiment.documentation_data["specimen_width"],
                    experiment.documentation_data["specimen_orientation"],
                    experiment.documentation_data["specimen_position"],
                    experiment.documentation_data["notch_radius"],
                    experiment.documentation_data["notch_depth"],
                    experiment.documentation_data["load_cell"],
                    experiment.name,
                    experiment.documentation_data["remark"],
                )
            )

        # export experiment data to file
        with open(
            os.path.join(expDoc_dir_python, experiment.name + "_docu.pickle",), "wb",
        ) as myfile:
            dill.dump(experiment, myfile)


def excel_project_template_to_dataframe(filepath):
    dataframe = pd.read_excel(filepath, sheet_name="user_input", index_col=1)

    dataframe = dataframe[dataframe.columns[dataframe.columns.str.contains("Test")]]

    try:
        dataframe = dataframe.drop("NaN")
    except:
        pass

    dataframe = dataframe.replace(np.nan, "", regex=True)

    dataframe = dataframe.loc[dataframe.index.dropna()]

    return dataframe


def instron_to_dataframe(filepath):
    dataframe = pd.read_csv(
        filepath,
        delimiter=";",
        decimal=",",
        usecols=[
            "Position des Aktuators(8800MK9168:Position) (mm)",
            "Last(8800MK9168:Kraft) (kN)",
        ],
    )
    dataframe = dataframe.rename(
        columns={
            "Position des Aktuators(8800MK9168:Position) (mm)": "displacement_in_mm",
            "Last(8800MK9168:Kraft) (kN)": "force_in_kN",
        }
    )

    return dataframe

