# expAna

Experiment documentation and analysis tool:

-   Scripted generation of test reports from experiments conducted at the KIT Institute of Mechanics (IFM) laboratory using the _Instron 1342_ testing machine with _Instron WaveMatrix_ software (Version 1.5.302.0).

-   Processing of raw DIC images or evaluation of data from Istra4D (Version 4.3.0.1) to analyse experimental results. Uses DIC results from [µDIC](https://github.com/PolymerGuy/muDIC) or Istra4D to compute and visualise stress-strain, volume strain, force-displacement, transversal strain responses.

Analysis and visualisation of the experimental results in [this PhD thesis](https://publikationen.bibliothek.kit.edu/1000141093/148698121) are based on `expAna`.

## Getting started

### Requirements

-   Mandatory:
    -   Python (Version 3.x, installation e.g. via [Conda](https://docs.conda.io/en/latest/)) or [pyenv](https://github.com/pyenv/pyenv)
        -   creating and subsequently setting/activating an environment is recommended
-   Optional (for full functionality):
    -   capability to run bash (`.sh`) scripts
    -   LaTeX 2e

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

### Create a Python environment and activate it
```shell
conda create -n expAna python=3.9 ipython scipy numpy pandas flake8 black
conda activate expAna
```

Alternatively create an environment using the `environment.yml` in the expAna repository after cloning:

```shell
conda env create -f environment.yml
conda activate expAna
```

   
### Clone the repositories and install the packages

Clone from [github](https://github.com/) into a local repository, activate the newly created conda environment, and install in the following order from within the corresponding directories:

1.  [`istra2py`](https://github.com/jonashund/istra2py)

```shell
    git clone git@github.com:jonashund/istra2py.git
    cd ./istra2py
    pip install -e .
    cd ..
```
2.  [`muDIC`](https://github.com/PolymerGuy/muDIC)

```shell
    git clone git@github.com:PolymerGuy/muDIC.git
    cd ./muDIC
    pip install -r requirements.txt
    cd ..
```

3.  [`expAna`](https://github.com/jonashund/expAna):

```shell
    git clone git@github.com:jonashund/expAna.git
    cd ./expAna
    pip install -e .
```

## Run the tests

```shell
python -m pytest
```

## Example data and scripts
Example data and scripts can be found in the [expAna_demo][expAna_demo] repository.

## Documentation
See also the [expAna_demo][expAna_demo] repository and see the included demonstration scripts.

### Folder structure

-   `project_directory`
    -   `data_instron` _instron project directory_
        -   `Test1`
        -   `Test2`
        -   `project_documentation_spreadsheet.xlsx`
    -   `data_istra_acquisition` _Istra4D acquisition directories_
        -   `Test1`
        -   `Test2`
    -   `data_istra_evaluation` _Istra4D evaluation directories_
        -   `Test1CORN1`
        -   `Test2CORN1`
    -   `data_export2tif` _created by expAna.acquis2tif_
        -   `Test1`
        -   `Test2`
    -   `data_muDIC` _created by dic\_with\_muDIC_
        -   `Test1`
        -   `Test2`
    -   `expAna_docu` _created by expAna.docu_
    -   `expAna_plots` _created by expAna.docu_
        -   `istra` _created by expAna.review.stress()_
        -   `muDIC` _created by expAna.review.stress(dic\_system="muDIC")_
_

### Data acquisition and experiment documentation
-   Document experiments in a spreadsheet using the `documentation_template.xlsx` located in `expAna/docu_templates`

-   Record an image series with the [_LIMESS Q-400_](https://git.scc.kit.edu/ifm/labor/pruefmaschinen/-/tree/master/DIC_Limess) system
    -   Name the recorded files in accordance with the _Instron WaveMatrix_ software
-   Optional: evaluate the acquisition using _Istra4D_

### Data import

-   Copy the filled `project_name.xlsx` spreadsheet into `project_directory/data_instron` 
-   Move all the `TestX` folders into `project_directory/data_instron`
    -   Make sure that every `TestX` folder contains a `TestX.Stop.csv` file. If only a `TestX.steps.tracking.csv` exists, rename this file as `TestX.Stop.csv`
-   Copy the `tex` folder from `expAna/docu_templates` into the `project_directory`
-   From the laboratory laptop running _Istra4D_, transfer the respective data into the `project_directory/data_istra_acquisition` and `project_directory/data_istra_evaluation` folders

### Create documentation reports and join data

-   Open a terminal in the `project_directory/tex` folder
-   Activate the environment with `expAna` installed in it
```shell
conda activate expAna
ipython
```

-   In the `ipython` terminal, run:
```python
import expAna
expAna.docu.main(<project_name>)
```

#### Result:

-   For every experiment, the data from the `project_name.xlsx` spreadsheet has been joined with the Instron data and exported to a `TestX_docu.pickle` file in `project_directory/expAna_docu/python` 
-   For every experiment, the force-dsplacement curve has been exported to the `project_directory/expAna_plots` folder  
-   For every experiment, from each `TestX.tex` in the `project_directory/expAna_docu/latex` directory, a `Test.pdf` test report has been created in `project_directory/expAna_docu`

### Obtaining true stress and volume strain response

-   Open a terminal in the `project_directory`:
```shell
conda activate expAna
ipython
```

-   In the `ipython` terminal: `import expAna`

    #### Option 1: Use evaluated data from _Istra4D_
-   `expAna.eval2stress.main()`
-   Experiments can be selected via `experiment_list=["TestN","TestM","TestX"]`, optionally excluded using `ignore_list=["TestY", "TestZ"]`, or filtered using a criterion based on a key value pair passed on as a list via `select=[<key>, <value>]`
    -    The key value pair provided must be part of the `documentation_data` dictionary that is created for every experiment by running `expAna.docu.main()`
    -   This dictionary is an attribute of every instance of the `Experiment` class and contains all the information for each experiment that is provided through  from the `project_name.xlsx` spreadsheet

    #### Option 2: Use `muDIC` on _Istra4D_ acquisition data
-   Read `*hdf5` files from image acquisition and export the contained images: `expAna.acquis2tif.main()`
-   Perform digital image correlation with `muDIC`: `expAna.dic_with_muDIC.main()`
-   Compute the true stress strain behaviour from the DIC results: `expAna.muDIC2stress.main()`
-   `experiment_list`, `ignore_list`, and `select` are all optional arguments of the `acquis2tif.main()`, `dic_with_muDIC.main()`, and `muDIC2stress.main()` functions

### Quick visualisation and review of the results

-   Plot true stress _vs._ log. strain: `expAna.review.stress()` or `expAna.review.stress(dic_system="muDIC")` (in case of usage with muDIC)
-   Plot reaction force _vs._ machine displacement curves: `expAna.review.force()`  or `expAna.review.force(dic_system="muDIC")` (in case of usage with muDIC)
-   Pass argument `set_failure=True` to remove corrupted parts of the stress strain curves via a GUI
-   Selected experiments to be considered can be specified via `experiment_list=["TestN","TestM","TestX"]` or through a selection criterion based on a `documentation_data` dictionary key value pair passed on as a list via `select=[<key>, <value>]`

### DIC visualisation

-   From each experiment with _Istra4D_ evaluation files available, plots of the DIC strain field overlaid on the raw images can be produced with the function  `expAna.plot.dic_strains(experiment_name="TestX", displacement=1,strain_component="x")`
-   Mandatory parameters:
    -   `experiment_name` (string): name of the folder with results omitting "CORN1" at its end
    -   `displacement` (float): traverse displacement where the results should be visualised in mm
    -   `strain_component` (string): possible values are "x", "y" an "xy" describing the strain relative to the tensile direction (given in image coordinate system) such that "x" means the tensile direction
-   Optional parameters:
    -   `tensile_direction` (string): "x" or "y"; tensile direction in terms of image coordinate system (x: horizontal, y: vertical); if not specified GUI to enter direction via arrow key opens
    -   'key' (bool): `True`(default) or `False`; colorbar or no colorbar right to plot of image
    -   'key_min' (float): minimum value for colorbar, default: `None`
    -   'key_max' (float): maximum value for colorbar, default: `None`
    -   `key_extend` (string): "min", "max", "both", "neither", default: `None`
    -   `max_triang_len` (integer): threshold of triangle length to be included in plot of Delaunay triangulation, default: 10
    -   `out_format` (string): "pdf" (default), "eps" or "pgf"

    #### Troubleshooting:
    
    -   `key = False` option only works when at least one previous command with `key = True` was executed
    -   in the case of "holes" in the deformation field overlay plot, increase the `max_triang_len` parameter

    #### Examples:
    
    -   **example # 0:** `expAna.plot.dic_strains(experiment_name="Test3", strain_component="x", tensile_direction="x", displacement=2.2, max_triang_len=25, key_min=0, key_max=0.5, key_extend="neither")`
    -   **example # 1:** `expAna.plot.dic_strains(experiment_name="Test3", strain_component="x", tensile_direction="x", displacement=1.5, no_key=True)`

### Results analysis
Analysis objects of the results are based on the `*.pickle` files located in the `expAna_data` directory. Analysis objects can also be exported so that they can be stored independently of the results.
**Remark**: Two examples are provided as part of the [expAna_demo] repository.

-   Create an analysis object of type `"stress"`, `"vol_strain"`, `"force"`, or `"poissons_ratio"`: `expAna.analysis.Analysis(type)`
-   Experiments may be selected using a `<key>`,`<value>` pair passed on as a list via `select=[<key>, <value> ]`
-   A non-optional input parameter for every analysis is `compare=<key>` where another `<key>` from the `documentation_data` dictionary must be passed on that is then used to compare the selected experiments
-   **Remark**: by default at least three experiments matching each criterion are required by the script to compute an average

    #### Examples:

    -   **Example # 0:** calculate and visualise the mean behaviour for every `<value>` found for the provided `<key>` and also visualise the mean curves in a comparison plot: `expAna.analysis.stress(compare="<key")` or `expAna.analysis.force(compare="<key")`
    -   **Example # 1:** compare the experiments of the project regarding the different values for the key "specimen_orientation": `expAna.analysis.stress(compare="specimen_orientation")`
    -   **Example # 2:** select all experiments that were carried out at a "crosshead_speed" of 0.1 and compare them regarding "specimen_orientation": `expAna.analysis.stress(select=["crosshead_speed", "0.1"],compare="specimen_orientation")`

-   Compute the data based on the analysis type, for `"stress"` use: `<analysis_object>.compute_data_stress()`
-   Visualise the results: `<analysis_object>.plot_data()`
-   Export the results:
```python
expAna.data_trans.export_analysis(
    <analysis_object>, out_filename=f"analysis_{<analysis_object>.export_prefix}.pickle",
)
```

* * * 
[expAna_demo]: https://github.com/jonashund/expAna_demo
