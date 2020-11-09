# expAna

Evaluate DIC images or evaluation data exported from Istra4D.  
True stress strain curves can be extracted from raw image material or evaluations    
present as Istra4D hdf5 files.

## install
- `cd path/to/local/git_repositories`
- `git clone git@git.scc.kit.edu:ifm/labor/exputil/mudic_ifm.git`
- `cd path/to/mudic_ifm`
- `pip install -e .`
- Goal:
- `git clone git@git.scc.kit.edu:ifm/labor/exputil/expAna.git`
- `cd path/to/expAna`
- `pip install -e .`
- `git clone git@git.scc.kit.edu:ifm/labor/exputil/expDoc.git`
- `cd path/to/expDoc`
- `pip install -e .`

## minimal how to:
### folder structure:
- `project_directory`
  - `data_instron` *instron project directory*
     - `Test1`
     - `Test2`
  - `data_istra_acquisition` *Istra4D acquisition directories*
     - `Test1`
     - `Test2`
  - `data_istra_evaluation` *Istra4D evaluation directories*
     - `Test1CORN1`
     - `Test2CORN1`
  - `data_export2tif` *generated by acquis2tif*
     - `Test1`
     - `Test2`
  - `data_muDIC` *generated by dic_with_muDIC*
     - `Test1`
     - `Test2`
  - `istra2true_stress`

### usage


## TO DO:
- Istra4D version?

### Eco mode - saving space
- only export the gauge results, strip fields from experiment object before export 

### Plot util
- analysis_util
- put argparser into utils
