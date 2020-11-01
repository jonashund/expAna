import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt


def excel_project_template_to_dataframe(filepath):
    dataframe = pd.read_excel(filepath, sheet_name="python", index_col=0)

    dataframe = dataframe[dataframe.columns[dataframe.columns.str.contains("Test")]]

    dataframe = dataframe.replace(np.nan, "", regex=True)

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


def remove_column_offset(dataframe, column_name):
    dataframe[column_name] = dataframe[column_name] - dataframe[column_name].iloc[0]

    return dataframe


def remove_row_offset(dataframe, column_name, threshold):
    threshold_begin = dataframe[dataframe[column_name] > threshold].index[0]

    dataframe = dataframe[threshold_begin:]

    return dataframe


def remove_fail_rows(dataframe, column_name, threshold):

    dataframe = dataframe[dataframe[column_name] > threshold]
    dataframe = dataframe[:-1]

    return dataframe


def plot_style():
    """
        Set custom style parameters for plots.
    """

    matplotlib.use("pgf")  # use the pgf backend

    # Include user defined 'phd.mplstyle' located in
    # print(matplotlib.get_configdir())
    #   * MacBook Air: ./Users/jonas/.matplolib/stylelib
    #   * ifmpc84: /home/jonas/.config/matplotlib/stylelib
    # The style file can also be located in any directory.
    # For invoking it the path has to be specified then.
    # For details see
    # https://matplotlib.org/tutorials/introductory/customizing.html
    plt.style.use("phd")

    # Overwrite default settings in rcParams if necessary.
    # For matplotlibrc.template file see
    # <python_installation_dir>/site-packages/matplotlib/mpl-data/matplotlibrc

    # For details on customising see
    # https://matplotlib.org/tutorials/introductory/customizing.html

    # Set rcParams for LaTeX
    set_latex_fonts = {
        # Use LaTeX to write all text
        "text.usetex": True,
        "font.family": "serif",
        # Use xxpt font in plots, to match xxpt font in document
        "font.size": 12,
        "axes.labelsize": 12,
        # Make the legend/label fonts a little smaller
        "legend.fontsize": 12,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
    }
    matplotlib.rcParams.update(set_latex_fonts)

    # Set rcParams for pgf backend.
    # For details see
    # https://matplotlib.org/3.1.1/tutorials/text/pgf.html
    matplotlib.rcParams.update({"pgf.texsystem": "xelatex"})
    matplotlib.rcParams.update({"pgf.rcfonts": False})

    set_preamble = {"pgf.preamble": r"\usepackage{amsmath} \usepackage{xfrac}"}
    matplotlib.rcParams.update(set_preamble)

    # set more rcParams
    matplotlib.rcParams.update({"patch.linewidth": 1})
    return
