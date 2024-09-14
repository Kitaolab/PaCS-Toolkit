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
- [Python](https://www.python.org/) >= 3.7 (but python >= 3.8 is recommended because of deeptime)
- PaCS-ToolKit currently supports 3 simulator
  - [Gromacs](https://www.gromacs.org/) >= 2022.2 tested
  - [Amber](https://ambermd.org/index.php) >= 2023 tested
  - [Namd](https://www.ks.uiuc.edu/Research/namd/) >= 2021-02-20 tested

## 1. Install by pip
### 1.1 Install by conda and pip
~~~shell
conda create -n pacsmd "python>=3.8" -y
conda activate pacsmd
~~~

- if using whole pacstk function
~~~shell
pip install "pacs[all] @ git+https://github.com/Kitaolab/PaCS-Toolkit.git"
~~~

- elif using "pacs mdrun" and analyzer == "mdtraj"
~~~shell
pip install "pacs[mdtraj] @ git+https://github.com/Kitaolab/PaCS-Toolkit.git"
~~~

- elif using "pacs mdrun" and analyzer == "gromacs"
~~~shell
pip install "pacs @ git+https://github.com/Kitaolab/PaCS-Toolkit.git"
~~~

- elif performing MSM
  - python >= 3.8 is recommended because of deeptime
~~~shell
pip install "pacs[msm] @ git+https://github.com/Kitaolab/PaCS-Toolkit.git"
~~~

### 1.2. Install by pip
- if using whole pacstk function
~~~shell
pip install "pacs[all] @ git+https://github.com/Kitaolab/PaCS-Toolkit.git"
~~~

- elif using "pacs mdrun" and analyzer == "mdtraj"
~~~shell
pip install "pacs[mdtraj] @ git+https://github.com/Kitaolab/PaCS-Toolkit.git"
~~~

- elif using "pacs mdrun" and analyzer == "gromacs"
~~~shell
pip install "pacs @ git+https://github.com/Kitaolab/PaCS-Toolkit.git"
~~~

- elif performing MSM
  - python >= 3.8 is recommended because of deeptime
~~~shell
pip install "pacs[msm] @ git+https://github.com/Kitaolab/PaCS-Toolkit.git"
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
conda create -n pacsmd "python>=3.8" -y
conda activate pacsmd
~~~

- if using whole pacstk function
  - python >= 3.8 is recommended because of deeptime
~~~shell
pip install -e ".[all]"
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
~~~
pip install -e ".[msm]"
~~~

### 2.2. Install by pip locally
- if using whole pacstk function
  - python >= 3.8 is recommended because of deeptime
~~~shell
pip install -e ".[all]"
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
  - python >= 3.8 is recommended because of deeptime
~~~shell
pip install -e ".[msm]"
~~~
