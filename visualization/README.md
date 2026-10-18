# Cryo-EM Data Visualization Tools

A collection of Python notebooks for visualizing and inspecting data from cryo-electron microscopy (cryo-EM) structural analysis.

This repository contains lightweight tools developed to support structural biology workflows, generate publication-ready plots, and make common visualization tasks easier to reproduce and adapt.

## Contents

### 1. `table1_chart.ipynb` - Structural Validation Metrics

A notebook for visualizing structural validation metrics using bar charts and color-coded quality thresholds.

**Features**
- Visualizes multiple metrics in a single figure.
- Uses configurable thresholds to distinguish quality ranges.
- Supports comparison of multiple structures.
- Exports plots in SVG format for further editing and use in scientific reports.

**Use case:** Comparing structural validation metrics and presenting the results in a clear, consistent format.

### 2. `FSC_plots.ipynb` - Fourier Shell Correlation (FSC) Plots

A notebook for plotting Fourier shell correlation (FSC) curves from data exported from CryoSPARC.

**Features**
- Visualizes FSC curves.
- Marks the FSC = 0.143 threshold.
- Illustrates the corresponding spatial resolution.
- Exports plots as PNG images.

**Use case:** Visual inspection and presentation of FSC curves during cryo-EM reconstruction analysis.

### 3. `genome_drawer.ipynb` - Draw genome map with highlighted genes and custom names

A notebook for plotting genome map of selected region and highlighting user-defined genes with custom labels and colors.

**Features**
- Utilizes [DnaFeaturesViewer](https://github.com/Edinburgh-Genome-Foundry/DnaFeaturesViewer) package.
- Supports the visualization of phage structural genes for structural biology research.
- Allows users to customize gene selection, labels, and plot appearance.
- Exports plots as SVG images.

## Requirements

The notebooks use Python and common scientific computing and plotting libraries.

Install Jupyter and the required packages in your Python environment. For example:

```bash
pip install jupyter numpy pandas matplotlib seaborn
```

Check the notebook imports and install any additional dependencies if needed.

## Getting Started

1. Clone or download this repository.
2. Install the required dependencies.
3. Open the desired notebook in Jupyter Notebook or JupyterLab.
4. Update the input data paths and analysis parameters.
5. Run the notebook cells in order.
6. Inspect and export the resulting figures.

## Input Data

The notebooks require input data in formats compatible with their respective workflows.

- **Structural validation notebook:** a table containing the metrics to visualize. See mock data for example.
- **FSC notebook:** a CSV file containing the spatial-frequency data and FSC values, with the column names expected by the notebook. CryoSPARC FSC export should be appropriate.

**Check the notebook code for the required column names, parameter definitions, and file paths before running the analysis.**

## Limitations

These notebooks are lightweight research tools rather than a fully packaged software library.

## Intended Audience

These tools may be useful for:
- Cryo-EM researchers and structural biologists.
- Students learning scientific Python and data visualization.
- Researchers who need to adapt plotting scripts to their own datasets.

Users are encouraged to adapt the notebooks to their workflows while documenting any changes to the analysis or visualization parameters.

## Citation and Acknowledgements

For the structural validation metrics, consult the relevant [MolProbity resources](http://molprobity.biochem.duke.edu/).

## License

A license has not yet been specified. Please check the repository's licensing terms before reusing or redistributing the code.