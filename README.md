# expAna

Experiment documentation and analysis tool:

-   Scripted generation of test reports from experiments conducted at the KIT Institute of Mechanics (IFM) laboratory using the _Instron 1342_ testing machine with _Instron WaveMatrix_ software (Version 1.5.302.0).

-   Processing of raw DIC images or evaluation of data from Istra4D (Version 4.3.0.1) to analyse experimental results. Uses DIC results from [µDIC](https://github.com/PolymerGuy/muDIC) or Istra4D to compute and visualise stress-strain, volume strain, force-displacement, transversal strain responses.

## Requirements

-   create a copy on a computer that runs bash (`.sh`) scripts as well as

    -   LaTeX 2e
    -   Python (Version 3.x, installation e.g. via [Conda](https://docs.conda.io/en/latest/)) or [pyenv](https://github.com/pyenv/pyenv)
        -   creating and subsequently setting/activating an environment is recommended

    #### **TLDR**: [Managing environments with Conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)

    -   create an environment based on version X.X of Python and packages 1 and 2:\
          `conda create --name <my_env_name> python=X.X package1 package2`
    -   **remark:** specifying the Python version and packages is optional\
          `conda create --name <my_env_name>`
    -   activate environment:\
          `conda activate <my_env_name>`
    -   deactivate environment:\
          `conda deactivate`
    -   remove an environment:\
          `conda remove --name <my_env_name> --all`

## Installation

### Create the environment

**1. manually using conda (on any OS running conda):**

-   create environment:
    `conda create --name <my_env_name> python=3.7 scipy=1.2.1 numpy ipython`

**1. using conda and environment.yml (tested on CentOS):**

-   execute in directory with `environmental.yml` (after cloning [`expDoc`](https://github.com/jonashund/expDoc) or [`expAna`](https://github.com/jonashund/expAna) )\
    `conda env create -f environmental.yml`

**1. using pyenv virtualenv (on macOS):**

-   install `pyenv virtualenv` via homebrew
-   install `miniconda-latest`:\
    `pyenv install miniconda-latest`
-   create a new virtualenv based on `miniconda-latest`:\
    `pyenv virtualenv miniconda-latest <my_env_name>`
-   in a directory (with one of the packages below) set the local environment:\
    `pyenv local <my_env_name>`
-   downgrade to Python v3.7 in the environment:\
    `conda install python=3.7`
-   install scipy v1.2.1 (requirement of muDIC_ifm):\
    `conda install scipy=1.2.1`
-   install ipython:\
    `conda install ipython`
-   install packages listed below, the local environment has to be set in each directory unless it's made the global environment (temporarily)

**1. manually using conda and pip (tested on CentOS):** 

-   based on current Python version with ipython and numpy:\
    `conda create --name <my_env_name> ipython numpy`
-   activate created environment:\
    `conda activate <my_env_name>`

### Cloning the repositories and installing

Clone from [github](https://github.com/) into a local repository and install in the following order from within the corresponding repository:

1.  [`istra2py`](https://github.com/jonashund/istra2py)
    -   `git clone git@git.scc.kit.edu:ifm/labor/istra2py.git`
    -   `cd ./istra2py`
    -   `pip install -e .`
2.  [`muDIC`](https://github.com/jonashund/muDIC)
    -   `git clone git@github.com:PolymerGuy/muDIC.git`
    -   `cd ./muDIC`
    -   `pip install -r requirements.txt`
3.  [`expAna`](https://github.com/jonashund/expAna):
    -   `git clone git@github.com:jonashund/expAna.git`
    -   `cd ./expAna`
    -   `pip install -e .`

## Usage

### Folder structure:

-   `project_directory`
    -   `data_instron` _instron project directory_
        -   `Test1`
        -   `Test2`
    -   `data_istra_acquisition` _Istra4D acquisition directories_
        -   `Test1`
        -   `Test2`
    -   `data_istra_evaluation` _Istra4D evaluation directories_
        -   `Test1CORN1`
        -   `Test2CORN1`
    -   `data_export2tif` _created by expAna.acquis2tif_
        -   `Test1`
        -   `Test2`
    -   `data_muDIC` _created by dic_with_muDIC_
        -   `Test1`
        -   `Test2`
    -   `expAna_docu` _created by expAna.docu_
    -   `expAna_plots` _created by expAna.docu_
        -   `istra` _created by expAna.review.stress()_
        -   `muDIC` _created by expAna.review.stress(dic_system="muDIC")
_

### Data acquisition and experiment documentation
-   document your experiments in a spreadsheet using the template in `./docu_templates`

-   record experiments with the [_LIMESS Q-400_](https://git.scc.kit.edu/ifm/labor/pruefmaschinen/-/tree/master/DIC_Limess) system
    -   name the recorded files similarly as the _Instron WaveMatrix_ software
-   optional: evaluate the acquisitions 

### Data import

-   move the `project_name.xlsx` spreadsheet into `data_instron` 
-   move all the `TestX` folders into `data`
    -   make sure that every `TestX` folder contains a `TestX.Stop.csv` file
        -   if only a `TestX.steps.tracking.csv` file has been created, rename file as `TestX.Stop.csv`
-   copy the `tex` folder from `./docu_templates` into the project folder
-   from the laboratory laptop running _Istra4D_ transfer the respective data into the `data_istra_acquisition` and `data_istra_evaluation` directories

### Create documentation reports and join data

-   open a termminal in the `./tex` folder
-   activate an environment with `expAna` installed in it
-   execute:
    -   `import expAna`
    -   `expAna.docu.main(<project_name>)`

#### Result:

-   for every experiment, the data from the Excel spreadsheet has been joined with the Instron data and exported to a `TestX_docu.pickle` file in `./expAna_docu/python` 
-   for every experiment, the force-dsplacement curve has been exported to the `expAna_plots` directory  
-   for every experiment, from each `TestX.tex` in the `./expAna_docu/latex` directory a `Test.pdf` test report has been created in `./data_docu`

### Obtaining true stress strain curves

-   in the `project_directory` open a terminal
-   run (preferably) `ipython` or `python`
-   `import expAna`
-   for every function called below look into the code or call as script to gain insight into optional arguments
    #### Option 1: Use evaluated data from _Istra4D_
-   `expAna.eval2stress.main()`
-   experiments can be selected via `experiment_list=["TestN","TestM","TestX"]`, optionally excluded using `ignore_list=["TestY", "TestZ"]`, or filtered using a criterion based on a key value pair passed on as a list via `select=[<key>, <value>]`
    -    the key value pair provided must be part of the `documentation_data` dictionary that is created for every experiment by running `expDoc` and subsequently used by `expAna`
    -   this dictionary is an attribute of every instance of the `Experiment` class and contains all the information for each experiment that is provided through the project's _Excel_ spreadsheet

    #### Option 2: Use `muDIC` on _Istra4D_ acquisition data
-   read an convert images: `expAna.acquis2tif.main()`
-   digital image correlation with `muDIC`: `expAna.dic_with_muDIC.main()`
-   true stress strain behaviour from DIC results: `expAna.muDIC2stress.main()`
-   `experiment_list`, `ignore_list`, and `select` are all optional arguments of the `acquis2tif.main()`, `dic_with_muDIC.main()`, and `muDIC2stress.main()` functions

### Quick visualisation

-   plot stress strain curves: `expAna.review.stress()` or `expAna.review.stress(dic_system="muDIC")` (in case of usage with muDIC)
-   plot force displacement curves: `expAna.review.force()`  or `expAna.review.force(dic_system="muDIC")` (in case of usage with muDIC)
-   pass argument `set_failure=True` to remove corrupted parts of the stress strain curves via a GUI
-   experiments to consider can be selected via `experiment_list=["TestN","TestM","TestX"]` or through a selection criterion based on a `documentation_data` dictionary key value pair passed on as a list via `select=[<key>, <value>]`

### DIC visualisation

-   from experiments with _Istra4D_ evaluation files available, plots with DIC strain field can be produced with the function   

  `expAna.plot.dic_strains(experiment_name="TestX", displacement=1,strain_component="x")`
-   mandatory parameters:
    -   `experiment_name` (string): name of the folder with results omitting "CORN1" at its end
    -   `displacement` (float): traverse displacement where the results should be visualised in mm
    -   `strain_component` (string): possible values are "x", "y" an "xy" describing the strain relative to the tensile direction (given in image coordinate system) such that "x" means in tensile direction
- optional parameters:
    -   `tensile_direction` (string): "x" or "y"; tensile direction in terms of image coordinate system (x: horizontal, y: vertical); if not specified GUI to enter direction via arrow key opens
    -   'key' (bool): `True`(default) or `False`; colorbar or no colorbar right to plot of image
    -   'key_min' (float): minimum value for colorbar, default: `None`
    -   'key_max' (float): maximum value for colorbar, default: `None`
    -   `key_extend` (string): "min", "max", "both", "neither", default: `None`
    -   `max_triang_len` (integer): threshold of triangle length to be included in plot of Delaunay triangulation, default: 10
    -   `out_format` (string): "pdf" (default), "eps" or "pgf"

    #### Examples:
    
    -   **example # 0:** `expAna.plot.dic_strains(experiment_name="Test3", strain_component="x", tensile_direction="x", displacement=2.2, max_triang_len=25, key_min=0, key_max=0.5, key_extend="neither")`
    -   **example # 1:** `expAna.plot.dic_strains(experiment_name="Test3", strain_component="x", tensile_direction="x", displacement=1.5, no_key=True)`

    #### Issues:
    
    -   `key = False` option only works when at least one previous command with `key = True` was executed
 
    #### Troubleshooting:

    -   in the case of "holes" in the deformation field overlay plot, increase the `max_triang_len` parameter

### Results analysis

-   experiments may be selected using a `<key>`,`<value>` pair passed on as a list via `select=[<key>, <value> ]`
-   a non-optional input parameter for every analysis is `compare=<key>` where another `<key>` from the `documentation_data` dictionary must be passed on that is then used to compare the selected experiments
-   **remark**: by default at least three experiments matching each criterion are required by the script to compute an average

    #### Examples:

    -   **example # 0:** calculate and visualise the mean behaviour for every `<value>` found for the provided `<key>` and also visualise the mean curves in a comparison plot: `expAna.analysis.stress(compare="<key")` or `expAna.analysis.force(compare="<key")`
    -   **example # 1:** compare the experiments of the project regarding the different values for the key "specimen_orientation": `expAna.analysis.stress(compare="specimen_orientation")`
    -   **example # 2:** select all experiments that were carried out at a "crosshead_speed" of 0.1 and compare them regarding "specimen_orientation": `expAna.analysis.stress(select=["crosshead_speed", "0.1"],compare="specimen_orientation")`
