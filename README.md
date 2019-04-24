# PyVOL

PyVOL is a python library for identifying protein binding pockets, partitioning them into sub-pockets, and calculating their volumes. While PyVOL can be used to identify new binding pockets, there are many algorithms that have been optimized for that task. PyVOL is intended to be used to describe features of known binding pockets. PyVOL can be run as a PyMOL plugin, as an imported python library, or as a commandline program. Visualization of results is exclusively supported through PyMOL.

While the API is not guaranteed to be stable at this point, it is unlikely to change.

## Basic Installation

PyVOL minimally requires biopython, msms, numpy, pandas, scipy, scikit-learn, and trimesh in order to run. PyVOL is available for manual installation from github, through the schlessinger conda channel, or from PyPI.
```bash
conda install -c schlessinger bio-pyvol
or
pip install bio-pyvol
```
MSMS must be installed separately. The bioconda channel provides a version for Linux and OSX:
```bash
conda install -c bioconda msms

```
Otherwise MSMS must be installed manually by downloading it from [MGLTools](http://mgltools.scripps.edu/packages/MSMS/) and adding it to the path.

As mentioned before, visualization relies on PyMOL 2.0+. Once PyVOL is installed in the python environment used by PyMOL, the script can be installed by using the plugin manager to install the file "plugins/pyvol_plugin.py".

## Quick Start
From within PyMOL, the simplest binding pocket calculation is simply run with:
```bash
pocket protein_selection
```
The two parameters that most dramatically effect calculations are the maximum and minimum radii used to respectively define the exterior surface of the protein and the boundary of the binding pocket itself. In practice, the minimum radius does not need to be changed as its default (1.4) is broadly useful. The maximum radius does often need to be adjust to find a suitable value using the max_rad paramter:
```bash
pocket protein_selection min_rad=1.4 max_rad=3.4
```

## Basic Usage
### Pocket Specification
PyVOL by default recognizes the largest pocket and returns the volume and geometry for it. However, manual identification of the pocket of interest is generally preferable. This can be done through specification of a ligand, a residue, or a coordinate.

Default behavior:
```bash
pocket protein_selection mode=largest
```
Ligand specification:
```bash
pocket protein_selection mode=ligand ligand=ligand_selection
```
Residue specification:
```bash
pocket protein_selection mode=residue residue=A15
```
where the residue is written as <Chain><Residue number>. If there is only one chain in the selection, the chain ID can be excluded.

Coordinate specification:
```bash
pocket protein_selection mode=coordinate pocket_coordinate="5.0 10.0 15.0"
```
where the coordinate is provided as three floats separated by spaces and bounded by quotation marks.

Alternatively, PyVOL can return the surfaces and volumes for all pockets above a minimum volume that are identified. By default, this volume cutoff is set at 200 A^3.
```bash
pocket protein_selection mode=all minimum_volume=200

### Extra Ligand Options
When a ligand is provided, the atoms of the ligand can be used to identify both minimum and maximum extents of the calculated binding pocket. To include the volume of the ligand in the pocket volume (useful for when the ligand extends into bulk solvent), use the lig_incl_rad parameter:
```bash
pocket protein_selection ligand=ligand_selection lig_incl_rad=0.0
```
where the value of lig_incl_rad is added to the Van der Waals radii of each atom in the ligand selection when calculating the exterior surface of the protein.

The atoms of the ligand can also be used to define a maximum boundary to the calculated pocket by specifying the lig_excl_rad parameter:
```bash
pocket protein_selection ligand=ligand_selection lig_excl_rad=5.0
```
where the value of lig_excl_rad is added to the Van der Waals radii of each atom in the ligand selection when calculating the exterior surface of the protein.

### Sub-pocket Partitioning
Sub-partitioning is enabled by setting the subdivide paramter to True:
```bash
pocket protein_selection subdivide=True
```

Parameters controlling the number of sub-pockets identified generally perform well using defaults; however, they can be easily adjusted as needed. The two most important parameters are the minimum radius of the largest sphere in each sub-pocket (this excludes small sub-pockets) and the maximum number of clusters:
```bash
pocket protein_selection subdivide=True min_subpocket_rad=1.7 max_clusters=10
```
If the number of clusters must be reduced, sub-pockets are merged on the basis of connectivity between the defining sets of tangent spheres. Practically, sub-pockets with a greater surface area boundary are merged first.

### Display and Output Options
By default, PyVOL simply writes volumes to STDOUT and, when invoked through PyMOL, displays pocket boundaries as semi-translucent surfaces. This behavior can be extensively customized.

The output name for all computed PyMOL objects and the base filename for any output files can be specified usingo the name option:
```bash
pocket protein_selection name=favorite_protein_1
```

Calculated surfaces can be visualized in three different ways by setting the display_mode parameter. The following three commands set the output as a solid surface with transparency, a wireframe mesh, and a collection of spheres. Color is set with the color parameter and transparency (when applicable) with the alpha parameter:
```bash
pocket protein_selection display_mode=solid alpha=0.85 color=skyblue
pocket protein_selection display_mode=mesh color=red
pocket protein_selection display_mode=spheres color=firebrick
```
where alpha is [0, 1.0] and the color is any color defined within pymol. The presets should generally be sufficient, but custom colors can be chosen using the commands given on the PyMOL wiki.

PyVOL will write a report of volumes (csv format) as well as the geometry of each surface (csv and obj formats for tangent sphere and surface representations respectively) if provided with the output_dir option:
```bash
pocket protein_selection output_dir=foo/
```

