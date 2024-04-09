# Install

*Content*
- [Install](#install)
  - [Requirements](#requirements)
  - [1. Install by pip](#1-install-by-pip)
    - [1.1 Install by conda and pip](#11-install-by-conda-and-pip)
    - [1.2. Install by pip](#12-install-by-pip)
  - [2. Get source code from github](#2-get-source-code-from-github)
    - [2.1. Install by conda and pip locally](#21-install-by-conda-and-pip-locally)
    - [2.2. Install by pip locally](#22-install-by-pip-locally)

## Requirements
- [Python](https://www.python.org/) >= 3.7
- PaCS-ToolKit currently supports 3 simulator
  - [Gromacs](https://www.gromacs.org/)
  - [Amber](https://ambermd.org/index.php)
  - [Namd](https://www.ks.uiuc.edu/Research/namd/)

## 1. Install by pip
### 1.1 Install by conda and pip
~~~shell
conda create -n pacsmd "python>=3.7" -y
conda activate pacsmd
~~~

- if using whole pacstk function
~~~shell
pip install "git+https://github.com/Kitaolab/PaCS-Toolkit.git#egg=pacs[all]"
pip install pyemma
~~~

- elif using "pacs mdrun" and analyzer == "mdtraj"
~~~shell
pip install "git+https://github.com/Kitaolab/PaCS-Toolkit.git#egg=pacs[mdtraj]"
~~~

- elif using "pacs mdrun" and analyzer == "gromacs"
~~~shell
pip install "git+https://github.com/Kitaolab/PaCS-Toolkit.git"
~~~

- elif performing MSM
~~~shell
pip install "git+https://github.com/Kitaolab/PaCS-Toolkit.git#egg=pacs[msm]"
pip install pyemma
~~~

### 1.2. Install by pip
- if using whole pacstk function
~~~shell
pip install "git+https://github.com/Kitaolab/PaCS-Toolkit.git#egg=pacs[all]"
~~~

- elif using "pacs mdrun" and analyzer == "mdtraj"
~~~shell
pip install "git+https://github.com/Kitaolab/PaCS-Toolkit.git#egg=pacs[mdtraj]"
~~~

- elif using "pacs mdrun" and analyzer == "gromacs"
~~~shell
pip install "git+https://github.com/Kitaolab/PaCS-Toolkit.git"
~~~

- elif performing MSM
~~~shell
pip install "git+https://github.com/Kitaolab/PaCS-Toolkit.git#egg=pacs[msm]"
pip install pyemma
~~~


## 2. Get source code from github
- git clone
~~~
git clone https://github.com/Kitaolab/PaCS-Toolkit.git
cd pacsmd
~~~

- get latest release
~~~
verion="x.x.x"
wget https://github.com/Kitaolab/PaCS-Toolkit/archive/refs/tags/${version}.tar.gz
tar -xvzf ${version}.tar.gz
cd pacsmd-${version}
~~~


### 2.1. Install by conda and pip locally
~~~shell
conda create -n pacsmd "python>=3.7" -y
conda activate pacsmd
~~~

- if using whole pacstk function
  -  pyemma does not recommend pip-install
~~~shell
pip install -e ".[all]"
conda install -c conda-forge pyemma
~~~

- elif using "pacs mdrun" and analyzer == "mdtraj"
~~~shell
pip install -e ".[mdtraj]"
~~~

- elif using "pacs mdrun" and analyzer == "gromacs"
~~~shell
pip install -e "."
~~~

- elif using "pacs mdrun" and analyzer == "cpptraj"
~~~shell
pip install -e "."
~~~

- elif performing MSM
  - pyemma does not recommend pip-install
~~~
pip install -e ".[msm]"
conda install -c conda-forge pyemma
~~~

### 2.2. Install by pip locally
- if using whole pacstk function
  - pyemma does not work, conda is recommend
~~~shell
pip install -e ".[all]"
pip install pyemma
~~~

- elif using "pacs mdrun" and analyzer == "mdtraj"
~~~shell
pip install -e ".[mdtraj]"
~~~

- elif using "pacs mdrun" and analyzer == "gromacs"
~~~shell
pip install -e "."
~~~

- elif using "pacs mdrun" and analyzer == "cpptraj"
~~~shell
pip install -e "."
~~~

- elif performing MSM
  - sometimes pyemma does not work, conda is recommend
~~~shell
pip install -e ".[msm]"
pip install pyemma
~~~
