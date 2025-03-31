# distance_deeptime.ipynb
You can use the distance notebook (`distance.ipynb`) to calculate standard binding free energies $\Delta G^o$ and rate constants $k_{off}, k_{on}$ by constructing Markov State Model (MSM).
After performing a/dissociation `pacs mdrun` and generating features with `pacs genfeature comdist` or `pacs genfeature comvec`, please refer to this notebook.

The distance notebook requires some important parameters.
Please make sure to set appropriate parameters as needed.

## Inputs
You need to prepare features for MSM extracted from MD trajectories before you run this notebook.

This notebook is intended for use after dissociation- or association- PaCS-MD, but you can also use it with  MD trajectories generated from normal MD simulations.

The features for MSM used in this distance notebook should follow the specified format and be kept in the same directory.
You can manually prepare these feature data as follows with your own script.

- Inter-COM distance (comdist)
  - directory: anywhere (you can specify)
  - filename: `t{trial:03}*.npy`
  - shape: (frames,)
- Inter-COM vector (comvec)
  - directory: anywhere (you can specify)
  - filename: `*.npy`
  - shape: (frames, 3)

## Analytical procedure
In this notebook, we use two types of Markov State Models (MSMs):

- **1D-MSM**
  - **Basis**: Center-of-mass distance (1D feature) between two molecules (typically a protein and a small molecule).
  - **Method**: Applied on a trial-by-trial basis using [maximum likelihood MSM](https://deeptime-ml.github.io/latest/api/generated/deeptime.markov.msm.MaximumLikelihoodMSM.html).
  - **Error Estimation**: Error ranges are calculated as statistical measures derived from the values obtained from each trial's MSM.

- **3D-MSM**
  - **Basis**: Center-of-mass vector (3D feature) between the molecules.
  - **Method**: Applied simultaneously across all trials using a [Bayesian MSM](https://deeptime-ml.github.io/latest/api/generated/deeptime.markov.msm.BayesianMSM.html#deeptime.markov.msm.BayesianMSM).
  - **Error Estimation**: Error ranges are derived from Bayesian sampling.

- **Rationale**:
  - The 1D approach is well-suited for distinguishing the direction of dissociation.
  - The 3D approach allows us to differentiate dissociation in multiple directions.

- Contents
  - Plot feature
  - 1D: Clustering
  - 1D: Plot Histogram of $d$
  - 1D: Plot Inertias
  - 1D: Build MSM
  - 1D: Plot ITS using distance
  - 1D: FEL along inter-COM distance $d$
  - 1D: Binding Free Energy
  - 3D: Clustering
  - 3D: Plot Histogram of $d$
  - 3D: Plot Inertias
  - 3D: Build MSM
  - 3D: Plot ITS using distance
  - 3D: FEL along $d$
  - 3D: Binding Free Energy
  - 3D: $k_{on}, k_{off}$
  - 3D: FEL on the 2D plane


## Parameters
Below is the list of parameters that need to be specified by the user.
Sample parameters can be found in a cell inside `distance_deeptime.ipynb`.


- `n_trial_for_calc`: List[int], required
  - list of indices of trials
- `trial_root_directory`: str, required
  - directory path containing trial directories
- `feature_1d_directory`: str, required
  - directory path containing comdist (created by `pacs gengeature comdist`)
- `feature_3d_directory`: str, required
  - directory path containing comvec (created by `pacs gengeature comvec`)
- `output_directory`: str, required
  - output directory path created by this notebook
- `show_picture`: bool, required
  - whether to show pictures in this notebook, select from [True, False]
- `T`: float, required
  - [K], temperature in your system
- `dt`: int, required
  - [ps], time interval of saved trajectory in PaCS-MD
- `n_clusters_for_try_1d`: List[int > 10], required
  - n_clusters list for plotting ITS
- `lags_for_try_1d`: List[int], required
  - lag time [steps] list for plotting ITS (1 step = 1 interval in the trajectory)
- `n_clusters_for_try_3d`: List[int > 10], required
  - n_clusters list for plotting ITS
- `lags_for_try_3d`: List[int], required
  - lag time [steps] list for plotting ITS (1 step = 1 interval in the trajectory)
- `cutoff`: float, required
  - [nm], cutoff for inter-COM distance to decide whether the replica is used for MSM to avoid artifacts caused by sparse sampling in regions with large $d$
  - If you prefer not to set the cutoff, you can set a very large number(e.g, 1000), which effectively means no cutoff. Avoid setting it to zero or None to prevent potential errors.
- `nbins`: int, required
  - the number of bins when plotting. 
- `cmap`: ListedColormap, required
  - color map for plotting FEL of each trial
- `do_volume_correction`: bool, required
  - whether to perform volume correction, select from [True, False]
- `num_of_ligands`: intm required
  - the number of ligands in the system.
- `box_size`: float, required
  - [nm^3], box size for volume ligand concentration used for koff calculation

In addition to these initial parameters, the notebook contains a cell for defining the threshold values for the bound and unbound states (denoted by $d$). This cell (below) is intended to determine the thresholds based on the energy landscape along $d$ and is located after the section titled **"1D: FEL along inte-COM distance $d$"**. If you already know these values from preliminary calculations, you can specify them at the beginning before executing the notebook.

```python
# this cell is placed after 1D: FEL along inte-COM distance $d$
# Default values are invalid to prevent mistakes. Please modify them to fit your system.

# definition for bound-state
lower_bound = 0 # 0 is recommended
upper_bound = 5

# definition for unbound-state
lower_unbound = 4
upper_unbound = params.cutoff # params.cutoff is recommended
```


## Outputs
The notebook outputs are saved in the directory specified by `output_directory`. More specifically, the data are organized into subdirectories based on their types: `logs/`, `images/`, `result_csvs/`, `cluster_objs/`, `MSM_objs/` and `Count_objs/`. The contents of data and their corresponding filenames stored in each directory are as follows:

- `logs/`
  - **Description**
    - The log files are saved here.
  - **Files**
    - log file generated by this notebook or equivalent script
    - (same as the output in the terminal)
      - `distance_deeptime.log`

- `images/`
  - **Description**
    - The image files are saved here.
  - **Files**
    - plot showing selection feature over cycles
      - `cycle_feature.png`
    - convergence of clustering
      - 1D
        - `clustering_converge_1d_trial{trial:03}_n_clusters{n_clusters}_cut{cutoff}.png`
      - 3D
        - `clustering_converge_3d_n_clusters{n_clusters}_cut{cutoff}.png`
    - histogram of $d$
      - 1D
        - `hist_1d_trial{trial:03}_n_clusters{n_clusters}_cut{cutoff}.png`
      - 3D
        - `hist_3d_n_clusters{n_clusters}_cut{cutoff}.png`
    - inertia along n_cluster
      - 1D
        - `inertia_1d_trial{trial:03}_cut{cutoff}.png`
      - 3D
        - `inertia_3d_cut{cutoff}.png`
    - implied timescales (ITS)
      - 1D
        - `its_1d_trial{trial:03}_n_clusters{n_clusters}_cut{cutoff}.png`
      - 3D
        - `its_3d_n_clusters{n_clusters}_cut{cutoff}.png`
    - fel along inter-COM distance $d$
      - 1D
        - `fel_1d_trial{trial:03}_n_clusters{n_clusters}_lag{lag}_cut{cutoff}.png`
      - 3D
        - `fel_3d_n_clusters{n_clusters}_lag{lag}_cut{cutoff}.png`
    - fel on 2D
      - `fel_2d_n_clusters{n_clusters}_lag{lag}_dim={first_coord}-{second_coord}_cut{params.cutoff}.png`


- `result_csvs/`
  - **Description**
    - The important results of analysis are stored as csv files here.
    - You can load and analyze with pandas, polars, R or excel.
  - **Files**
    - MSM stationary destribution data
      - 1D
        - `1d_trial{trial:03}_n_clusters{n_clusters}_lag{lag}_cut{cutoff}.csv`
          - shape: (n_clusters, 2)
          - column 1: $d$ [nm] of each cluster center
          - column 2: stationary destribution of the corresponding cluster
      - 3D
        - `3d_n_clusters{n_clusters}_lag{lag}_cut{cutoff}.csv`
          - shape: (n_clusters, 3+n_samples)
          - column 1: $d_x$ [nm] of each cluster center
          - column 2: $d_y$ [nm] of each cluster center
          - column 3: $d_z$ [nm] of each cluster center
          - column 4 to end: stationary destribution of the corresponding cluster in i-th sample
    - standard binding free energy data
      - 1D
        - `1d_binding_energy_summary.csv`
          - column 1: trial
          - column 2: n_clusters
          - column 3: lag [steps]
          - column 4: lower bound of the bound state [nm]
          - column 5: upper bound of the bound state [nm]
          - column 6: lower bound of the unbound state [nm]
          - column 7: upper bound of the unbound state [nm]
          - column 8: $\Delta G_{PMF}$ [kcal/mol]
          - column 9: volume correction term [kcal/mol]
          - Note: column 8 plus column 9 yield $\Delta G^o$
      - 3D
        - `3d_binding_energy_summary.csv`
          - column 1: n_clusters
          - column 2: lag [steps]
          - column 3: lower bound of the bound state [nm]
          - column 4: upper bound of the bound state [nm]
          - column 5: lower bound of the unbound state [nm]
          - column 6: upper bound of the unbound state [nm]
          - column 7: $\Delta G_{PMF}$ [kcal/mol]
          - column 8: volume correction term [kcal/mol]
          - Note: column 7 plus column 8 yield $\Delta G^o$
    - volume correction data
      - 1D
        - `1d_VC.csv`
          - column 1: trial
          - column 2: lower bound of the unbound state [nm]
          - column 3: upper bound of the unbound state [nm]
          - column 4: convex volume of the unbound state [$\AA^3$]
          - column 5: volume correction [kcal/mol]
      - 3D
        - `3d_VC.csv`
          - column 1: lower bound of the unbound state [nm]
          - column 2: upper bound of the unbound state [nm]
          - column 3: convex volume of the unbound state [$\AA^3$]
          - column 4: volume correction [kcal/mol]
    - rate constant data
      - 3D
        - `3d_rate_constant_summary.csv`
          - column 1: n_clusters
          - column 2: lag [steps]
          - column 3: lower bound of the bound state [nm]
          - column 4: upper bound of the bound state [nm]
          - column 5: lower bound of the unbound state [nm]
          - column 6: upper bound of the unbound state [nm]
          - column 7: mean of $k_{off}$ [s^-1]
          - column 8: standard error of $k_{off}$ [s^-1]
          - column 9: mean of $k_{on}$ [M^-1 s^-1]
          - column 10: standard error of $k_{on}$ [M^-1 s^-1]

- `cluster_objs/`
  - **Description**
    - The objects related to clustering are saved here.
    - The saved object is a python dictionary object.
      - key: lag time [steps]
      - value: [deeptime.clustering.KMeansModel](https://deeptime-ml.github.io/latest/api/generated/deeptime.clustering.KMeansModel.html#deeptime.clustering.KMeansModel)
    - You can load with python's `pickle` module.
  - **Files**
    - python dictionary of clustering result objects
      - 1D
        - `1d_trial{trial:03}_n_clusters{n_clusters}_cut{cutoff}.pkl`
      - 3D
        - `3d_n_clusters{n_clusters}_cut{cutoff}.pkl`

- `MSM_objs/`
  - **Description**
    - Objects related to MSM are saved here.
    - The saved object is a python dictionary object.
      - key: lag time [steps]
      - value: [deeptime.markov.msm.MarkovStateModelCollection](https://deeptime-ml.github.io/latest/api/generated/deeptime.markov.msm.MarkovStateModelCollection.html#deeptime.markov.msm.MarkovStateModelCollection)
    - You can load with python's `pickle` module.
  - **Files**
    - python dictionary of msm result objects
      - 1D
        - `1d_trial{trial:03}_n_clusters{n_clusters}_cut{cutoff}.pkl`
      - 3D
        - `3d_n_clusters{n_clusters}_cut{cutoff}.pkl`

- `Count_objs/`
  - **Description**
    - Objects related to transition counting are saved here.
    - The saved object is a python dictionary object.
      - key: lag time [steps]
      - value: [deeptime.markov.TransitionCountModel](https://deeptime-ml.github.io/latest/api/generated/deeptime.markov.TransitionCountModel.html#deeptime.markov.TransitionCountModel)
    - You can load with python's `pickle` module.
  - **Files**
    - 1D
      - `1d_trial{trial:03}_n_clusters{n_clusters}_cut{cutoff}.pkl`
    - 3D
      - `3d_n_clusters{n_clusters}_cut{cutoff}.pkl`

## Tips
The most time-consuming part is clustering and MSM building part.

We recommend you to run the script in .py for those parts in background, and run the other parts in .ipynb.


- **Example Procedure:**
  1. Fill in the parameters in the notebook.
  2. Run `jupyter nbconvert distance_deeptime.ipynb --to script` to convert the notebook into a Python script.
  3. Copy the resulting `distance_notebook.py` and create separate scripts for 1D-MSM and 3D-MSM that include only the clustering and MSM building parts.
  4. Run these scripts in parallel on different clusters.
  5. Return to the notebook to plot the free energy landscape, and calculate the binding free energy, rate constants, etc.