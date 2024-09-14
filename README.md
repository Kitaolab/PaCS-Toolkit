# PaCS-Toolkit

PaCS-Toolkit enables the execution of PaCS-MD (Parallel Cascade Selection Molecular Dynamic Simulation), a non-bias-enhanced sampling method, across various environments. Additionally, it offers tools for result analysis and visualization.
While PaCS-MD offers a wide range of applications with existing evaluation types, our toolkit also allows for the integration of additional types as needed.

We believe our package will benefit your research.

- [PaCS-Toolkit](#pacs-toolkit)
  - [Document](#document)
  - [Quick install](#quick-install)
  - [Example command](#example-command)
  - [Citation](#citation)
  - [LICENSE](#license)


## Document
- The documentation of PaCS-Toolkit is [here](https://kitaolab.github.io/PaCS-Toolkit/).

## Quick install

<details><summary> 1. Install by pip </summary>

~~~shell
# Install all feautres of PaCS-Toolkit
pip install "pacs[all] @ git+https://github.com/Kitaolab/PaCS-Toolkit.git"
~~~

see [document](https://kitaolab.github.io/PaCS-Toolkit/) for more information.

</details>


<details><summary> 2. Install by conda and pip </summary>

~~~shell
conda create -n pacs "python>=3.8" -y
conda activate pacs

# Install all features of PaCS-Toolkit
pip install "pacs[all] @ git+https://github.com/Kitaolab/PaCS-Toolkit.git"
~~~

see [document](https://kitaolab.github.io/PaCS-Toolkit/) for more information.

</details>


## Example command
```sh
pacs mdrun -t 1 -f input.toml
```
see help messages(`pacs --help`) and [document](https://kitaolab.github.io/PaCS-Toolkit/) for more information.

## Citation
- [1] PaCS-Toolkit: Ikizawa, S.*, Hori, T.*, Wijana, T.N.*, Kono, H., Bai, Z., Kimizono, T., Lu, W., Tran, D.P., & Kitao, A. PaCS-Toolkit: Optimized software utilities for parallel cascade selection molecular dynamics (PaCS-MD) simulations and subsequent analyses. *J. Phys. Chem. B.*, **128**, 15, 3631-3642 (2024). https://doi.org/10.1021/acs.jpcb.4c01271

- [2] Original PaCS-MD or targeted-PaCS-MD (t-PaCS-MD): Harada, R., & Kitao, A. Parallel cascade selection molecular dynamics (PaCS-MD) to generate conformational transition pathway. *J. Chem. Phys.* **139**, 035103 (2013). https://doi.org/10.1063/1.4813023

- [3] Dissociation PaCS-MD (dPaCS-MD): Tran, D. P., Takemura, K., Kuwata, K., & Kitao, A. Protein–Ligand Dissociation Simulated by Parallel Cascade Selection Molecular Dynamics. *J. Chem. Theory Comput*. **14**, 404–417 (2018). https://doi.org/10.1021/acs.jctc.7b00504

- [4] Dissociation PaCS-MD (dPaCS-MD): Tran, D. P., & Kitao, A. Dissociation Process of a MDM2/p53 Complex Investigated by Parallel Cascade Selection Molecular Dynamics and the Markov State Model. *J. Phys. Chem. B*, **123**, 11, 2469–2478 (2019). https://doi.org/10.1021/acs.jpcb.8b10309

- [5] Dissociation PaCS-MD (dPaCS-MD): Hata, H., Phuoc Tran, D., Marzouk Sobeh, M., & Kitao, A. Binding free energy of protein/ligand complexes calculated using dissociation Parallel Cascade Selection Molecular Dynamics and Markov state model. *Biophysics and Physicobiology*, **18**, 305–31 (2021). https://doi.org/10.2142/biophysico.bppb-v18.037

- [6] Application to protein domain motion: Inoue, Y., Ogawa, Y., Kinoshita, M., Terahara, N., Shimada, M., Kodera, N., Ando, T., Namba, K., Kitao, A., Imada, K., & Minamino, T. Structural Insights into the Substrate Specificity Switch Mechanism of the Type III Protein Export Apparatus. *Structure*, **27** , 965-976 (2019). https://doi.org/10.1016/j.str.2019.03.017

- [7] Association and dissociation PaCS-MD (a/dPaCS-MD): Tran, D. P., & Kitao, A. Kinetic Selection and Relaxation of the Intrinsically Disordered Region of a Protein upon Binding. *J. Chem. Theory Comput.*, **16**, 2835–2845 (2020). https://doi.org/10.1021/acs.jctc.9b01203

- [8] Edge expansion PaCS-MD (eePaCS-MD): Takaba, K., Tran, D. P., & Kitao, A. Edge expansion parallel cascade selection molecular dynamics simulation for investigating large-amplitude collective motions of proteins. *J. Chem. Phys.* **152**, 225101 (2020). https://doi.org/10.1063/5.0004654

- [9] Edge expansion PaCS-MD (eePaCS-MD): Takaba, K., Tran, D. P., & Kitao, A.  Erratum: "Edge expansion parallel cascade selection molecular dynamics simulation for investigating large-amplitude collective motions of proteins" [J. Chem. Phys. 152, 225101 (2020)]. *J. Chem. Phys.* **153**, 179902 (2020). https://doi.org/10.1063/5.0032465

- [10] rmsdPaCS-MD: Tran, D. P., Taira, Y., Ogawa, T., Misu, R., Miyazawa, Y., & Kitao, A. Inhibition of the hexamerization of SARS-CoV-2 endoribonuclease and modeling of RNA structures bound to the hexamer. *Sci Rep* **12**, 3860 (2022). https://doi.org/10.1038/s41598-022-07792-2


## LICENSE
- GPLv3
