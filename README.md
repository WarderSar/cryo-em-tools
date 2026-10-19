# Cryo-EM Tools

A collection of Python scripts and Jupyter notebooks for cryo-electron microscopy (cryo-EM) data analysis, structural validation, and scientific visualization.

This repository contains lightweight research tools developed to simplify common data visualization tasks and support structural biology workflows. It is intended both as a personal portfolio of scientific programming and as a resource for students and researchers working with cryo-EM data.

**Disclaimer:** These scripts are provided for research and educational purposes. Users are responsible for validating the scientific assumptions, parameters, and interpretation of their results.

## Repository Contents

### Visualization

The `visualization/` directory contains Jupyter notebooks for plotting and inspecting cryo-EM analysis results.

| Notebook | Description |
|---|---|
| `table1_chart.ipynb` | Visualizes structural validation metrics using bar charts and configurable quality thresholds. |
| `FSC_plots.ipynb` | Plots Fourier shell correlation (FSC) curves and visualizes the FSC = 0.143 threshold for resolution assessment. |
| `genome_drawer.ipynb` | Plots genome map of selected region and highlighting user-defined genes with custom labels and colors. |

### Cryo-EM Processing

The `cryoem_processing/` directory contains useful Jupyter notebooks and Python3 scripts to speed routine tasks while quering CryoSPARC.

| Notebook | Description |
|---|---|
| `sets_crop_merger.py` | A lightweight calculator for merging two datasets during Extract from Micrographs step. It simply outputs two `Extraction box size` and one `Fourier-crop to box size (pix)`. It posts list of the results in the terminal. So you can choose appropriate values. It is also available in `cstools_set.py`. |
| `cstools_set.py` | A module of useful functions based on (cryosparc-tools)[https://tools.cryosparc.com/]. Requires cryosparc-tools python package. functions can be combined in flexible pipelines to achieve various reconstruction goals.|

Additional scripts and notebooks will be added as the repository develops.