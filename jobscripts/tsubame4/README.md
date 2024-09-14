# tsubame4
- [URL](https://www.t4.gsic.titech.ac.jp/)

| simulator | analyzer     | available |
| --------- | ------------ | --------- |
| gromacs   | gromacs      | o         |
| gromacs   | mdtraj       | o         |
| amber     | mdtraj       | o         |
| amber     | cpptraj      | o         |
| namd      | mdtraj       | o         |

- Note
  - Running gromacs over multiple node fails to run for some reason as of Sep. 2024.
  - So, we are sharing the script for the case `n_parallel=1`