# Analyzer

- In PaCS-MD, the analyzer is a component that evaluates the snapshot of each trajectory in each cycle and ranks them based on the evaluation type specified in the input file.
- Some of the top ranked frames become the initial structure of each replica in the next cycle.
- You can use the following evaluation functions by setting the `#analyzer` keyword in your input file. Depending on the phenomenon of interest, the appropriate `type` must be selected.
- If you do not find a `type` that meets your purpose, you can implement it yourself by setting `type` = [template](#template).
- The following are some commonly used evaluation types.

*Content*
- [Dissociation](#dissociation)
- [Association](#association)
- [Target](#target)
- [RMSD](#rmsd)
- [EdgeExpansion](#edgeexpansion)
- [A\_D](#a_d)
- [Template](#template)


## Dissociation
- Evaluate snapshots of each trajectory so that the centers of mass of the two selected groups are far apart.
- Usage Example
  - Ligand dissociating from a protein
  - Separate the distance between the two domains of a protein
- For more information, see [here](analyzer/dissociation.md).
- See [here](inputfile.md#dissociation) for an example input file.

<details><summary> Papers </summary>

```
[1] Protein-Ligand Dissociation Simulated by Parallel Cascade Selection Molecular Dynamics, https://doi.org/10.1021/acs.jctc.7b00504
[2] Dissociation Process of a MDM2/p53 Complex Investigated by Parallel Cascade Selection Molecular Dynamics and the Markov State Model, https://doi.org/10.1021/acs.jpcb.8b10309
[3] Binding free energy of protein/ligand complexes calculated using dissociation Parallel Cascade Selection Molecular Dynamics and Markov state model, https://doi.org/10.2142/biophysico.bppb-v18.037
[4] High pressure inhibits signaling protein binding to the flagellar motor and bacterial chemotaxis through enhanced hydration, https://doi.org/10.1038/s41598-020-59172-3
[5] Dissociation Pathways of the p53 DNA Binding Domain from DNA and Critical Roles of Key Residues Elucidated by dPaCS-MD/MSM, https://doi.org/10.1021/acs.jcim.1c01508
```

</details>


## Association
- Evaluate snapshots of each trajectory so that the centers of mass of the two selected groups are close together.
- Usage Example
  - Bringing a ligand closer to a protein
  - Bringing two domains of a protein closer together
- For more information, see [here](analyzer/association.md).
- See [here](inputfile.md#association) for an example input file.

<details><summary> Papers </summary>

</details>

## Target
- Evaluate snapshots of each trajectory so that the RMSD from the reference structure becomes smaller.
- Usage Example
  - Finding transitions between two known structures.
- Evaluate to follow the `reference` structure using RMSD.
- For more information, see [here](analyzer/target.md).
- See [here](inputfile.md#target) for an example input file.

<details><summary> Papers </summary>

~~~
[1] Parallel cascade selection molecular dynamics (PaCS-MD) to generate conformational transition pathway, https://doi.org/10.1063/1.4813023
~~~

</details>


## RMSD
- Evaluate snapshots of each trajectory so that the RMSD from the reference structure becomes larger.
- Usage Example
  - Sampling a wide range of structures
  - Sampling a wide range of ligand binding modes
- For more information, see [here](analyzer/rmsd.md).
- See [here](inputfile.md#rmsd) for an example input file.

<details><summary> Papers </summary>

~~~
[1] Inhibition of the hexamerization of SARS-CoV-2 endoribonuclease and modeling of RNA structures bound to the hexamer, https://doi.org/10.1038/s41598-022-07792-2
~~~

</details>

## EdgeExpansion
- Evaluate snapshots of each trajectory so that the frame forms the convex hull of the 4-dimentional principal component space(PCs).
- Usage Example
  - Sampling a wide range of phase space without knowing the reference structure
- For more information, see [here](analyzer/edgeexpansion.md).
- See [here](inputfile.md#edgeexpansion) for an example input file.
  
<details><summary> Papers </summary>

~~~
[1] Edge expansion parallel cascade selection molecular dynamics simulation for investigating large-amplitude collective motions of proteins, https://doi.org/10.1063/5.0004654
~~~

</details>


## A_D
- Evaluate snapshots of each trajectory so that the distance between the centers of mass of the two selected groups fluctuates significantly within a certain range.
- Usage Example
  - Observing large movements of proteins, such as opening and closing.
  - Observing the binding and unbinding of ligands.
- For more information, see [here](analyzer/a_d.md).
- See [here](inputfile.md#a_d) for an example input file.

<details><summary> Papers </summary>

~~~
[1] Kinetic Selection and Relaxation of the Intrinsically Disordered Region of a Protein upon Binding, https://doi.org/10.1021/acs.jctc.9b01203
~~~

</details>

## Template
- Evaluate snapshots of each trajectory using a user-defined evaluation function.
- Additional variables can be specified in `input.toml`
- Usage Example
  - If you want to use a different evaluation function than the ones provided.
- For more information, [click here](./analyzer/template.md)
