# PaCS-ToolKit

PaCS-ToolKit enables the execution of PaCS-MD (Parallel Cascade Selection Molecular Dynamic Simulation), a non-bias-enhanced sampling method, across various environments. Additionally, it offers tools for result analysis and visualization.
While PaCS-MD offers a wide range of applications with existing evaluation types, our toolkit also allows for the integration of additional types as needed.

We believe our package will benefit your research.

- [PaCS-ToolKit](#pacs-toolkit)
  - [Document](#document)
  - [Quick install](#quick-install)
  - [Citation](#citation)
  - [LICENSE](#license)


## Document
- The documentation of PaCS-ToolKit is [here](https://kitaolab.github.io/PaCS-Toolkit/).

## Quick install

<details><summary> 1. Install by pip </summary>

~~~shell
# Install all feautres of PaCS-ToolKit
pip install "git+https://github.com/Kitaolab/PaCS-Toolkit.git#[all]"
~~~

see [document](https://kitaolab.github.io/PaCS-Toolkit/) for more information.

</details>


<details><summary> 2. Install by conda and pip </summary>

~~~shell
conda create -n pacs "python>=3.7" -y
conda activate pacs

# Install all features of PaCS-ToolKit
pip install "git+https://github.com/Kitaolab/PaCS-Toolkit.git#[all]"
~~~

see [document](https://kitaolab.github.io/PaCS-Toolkit/) for more information.

</details>


## Citation
pleae cite the paper, which is under cosideration. This information will be updated upon publication.

~~~markdown
- PaCS-Toolkit
The paper is under consideration. The information will be updated upon publication.
[1] Ikizawa, S, Hori, T., Wijana, T.N., Kono, H., Bai, Z., Kimizono, T., Lu, W., Tran, D.P., & Kitao, A. PaCS-Toolkit: Optimized software utilities for parallel cascade selection molecular dynamics (PaCS-MD) simulations and subsequent analyses. Submitted.

- Original PaCS-MD or targeted-PaCS-MD (t-PaCS-MD)
[2] Harada, R., & Kitao, A. Parallel cascade selection molecular dynamics (PaCS-MD) to generate conformational transition pathway. J. Chem. Phys. 139, 035103 (2013). https://doi.org/10.1063/1.4813023

- Dissociation PaCS-MD (dPaCS-MD)
[3] Tran, D. P., Takemura, K., Kuwata, K., & Kitao, A. Protein–Ligand Dissociation Simulated by Parallel Cascade Selection Molecular Dynamics. J. Chem. Theory Comput. 14, 404–417 (2018). https://doi.org/10.1021/acs.jctc.7b00504
[4] Tran, D. P., & Kitao, A. Dissociation Process of a MDM2/p53 Complex Investigated by Parallel Cascade Selection Molecular Dynamics and the Markov State Model. J. Phys. Chem. B , 123, 11, 2469–2478 (2019). https://doi.org/10.1021/acs.jpcb.8b10309
[5] Hata, H., Phuoc Tran, D., Marzouk Sobeh, M., & Kitao, A. Binding free energy of protein/ligand complexes calculated using dissociation Parallel Cascade Selection Molecular Dynamics and Markov state model. Biophysics and Physicobiology, 18, 305–31 (2021). https://doi.org/10.2142/biophysico.bppb-v18.037

- Application to protein domain motion
[6] Inoue, Y., Ogawa, Y., Kinoshita, M., Terahara, N., Shimada, M., Kodera, N., Ando, T., Namba, K., Kitao, A., Imada, K., & Minamino, T. Structural Insights into the Substrate Specificity Switch Mechanism of the Type III Protein Export Apparatus. Structure, 27 , 965-976 (2019). https://doi.org/10.1016/j.str.2019.03.017

- Association and dissociation PaCS-MD (a/dPaCS-MD)
[7] Tran, D. P., & Kitao, A. Kinetic Selection and Relaxation of the Intrinsically Disordered Region of a Protein upon Binding. J. Chem. Theory Comput. 16, 2835–2845 (2020). https://doi.org/10.1021/acs.jctc.9b01203

- Edge expansion PaCS-MD (eePaCS-MD)
[8] Takaba, K., Tran, D. P., & Kitao, A. Edge expansion parallel cascade selection molecular dynamics simulation for investigating large-amplitude collective motions of proteins. J. Chem. Phys. 152, 225101 (2020). https://doi.org/10.1063/5.0004654
[9] Takaba, K., Tran, D. P., & Kitao, A.  Erratum: "Edge expansion parallel cascade selection molecular dynamics simulation for investigating large-amplitude collective motions of proteins" [J. Chem. Phys. 152, 225101 (2020)]. . J. Chem. Phys. 153, 179902 (2020). https://doi.org/10.1063/5.0032465

- rmsdPaCS-MD
[10] Tran, D. P., Taira, Y., Ogawa, T., Misu, R., Miyazawa, Y., & Kitao, A. Inhibition of the hexamerization of SARS-CoV-2 endoribonuclease and modeling of RNA structures bound to the hexamer. Sci Rep 12, 3860 (2022). https://doi.org/10.1038/s41598-022-07792-2
~~~


## LICENSE
- GPLv3
