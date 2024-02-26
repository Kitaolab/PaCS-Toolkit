"""
reference
"""

import subprocess
from typing import List

import numpy as np
from pacs.mdrun.analyzer.superAnalyzer import SuperAnalyzer
from pacs.models.settings import MDsettings, Snapshot
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


class A_D(SuperAnalyzer):
    def __init__(self):
        self.direction = "maximize"
        self.bound_cnt = 0

    def calculate_cv(
        self, settings: MDsettings, cycle: int, replica: int, send_rev
    ) -> List[float]:
        if settings.analyzer == "mdtraj":
            ret = self.cal_by_mdtraj(settings, cycle, replica)
        elif settings.analyzer == "gromacs":
            ret = self.cal_by_gmx(settings, cycle, replica)
        elif settings.analyzer == "cpptraj":
            ret = self.cal_by_cpptraj(settings, cycle, replica)
        else:
            raise NotImplementedError
        send_rev.send(ret)
        return ret

    def ranking(self, settings: MDsettings, CVs: List[Snapshot]) -> List[Snapshot]:
        if self.direction == "maximize":
            sorted_cv = sorted(CVs, key=lambda x: x.cv, reverse=True)
            # If the distance exceeds the d-threshold (if they are far apart),
            # change the sort direction so that it becomes smaller.
            if sorted_cv[0].cv > float(settings.d_threshold):
                LOGGER.info("cv reached d-threshold, REVERSING the sort direction")
                self.direction = "minimize"
                sorted_cv = sorted(CVs, key=lambda x: x.cv, reverse=False)
        else:
            sorted_cv = sorted(CVs, key=lambda x: x.cv, reverse=False)
            # If the closest frame is taken from within the first t_sel frame,
            if sorted_cv[0].frame < float(settings.frame_sel):
                self.bound_cnt += 1
                if self.bound_cnt >= float(settings.bound_threshold):
                    LOGGER.info("bound threshold reached, REVERSING the sort direction")
                    self.direction = "maximize"
                    sorted_cv = sorted(CVs, key=lambda x: x.cv, reverse=True)
                    self.bound_cnt = 0
        return sorted_cv

    def is_threshold(self, settings: MDsettings, CVs: List[Snapshot] = None) -> bool:
        return False

    def cal_by_mdtraj(
        self, settings: MDsettings, cycle: int, replica: int
    ) -> List[float]:
        import mdtraj as md

        dir = settings.each_replica(_cycle=cycle, _replica=replica)
        trj = md.load(
            f"{dir}/prd{settings.trajectory_extension}",
            top=settings.top_mdtraj,
        )

        com1 = md.compute_center_of_mass(
            trj.atom_slice(trj.topology.select(settings.selection1))
        )
        com2 = md.compute_center_of_mass(
            trj.atom_slice(trj.topology.select(settings.selection2))
        )
        dist = np.array([np.linalg.norm(com1[i] - com2[i]) for i in range(len(com1))])
        return dist

    def cal_by_gmx(self, settings: MDsettings, cycle: int, replica: int) -> List[float]:
        extension = settings.trajectory_extension
        grp1 = settings.selection1
        grp2 = settings.selection2

        dir = settings.each_replica(_cycle=cycle, _replica=replica)

        cmd_image = f"echo 'System' \
                | {settings.cmd_gmx} trjconv \
                -f {dir}/prd{extension} \
                -s {dir}/prd.tpr \
                -o {dir}/prd_image{extension} \
                -pbc mol \
                -ur compact \
                1> {dir}/center.log 2>&1"  # NOQA: E221
        res_image = subprocess.run(cmd_image, shell=True)
        if res_image.returncode != 0:
            LOGGER.error("error occured at image command")
            LOGGER.error(f"see {dir}/center.log")
            exit(1)

        cmd_dist = f"{settings.cmd_gmx} distance \
                -f {dir}/prd_image{extension} \
                -s {dir}/prd.tpr \
                -n {settings.index_file} \
                -oxyz {dir}/interCOM_xyz.xvg \
                -xvg none \
                -select 'com of group {grp1} plus com of group {grp2}' \
                1> {dir}/distance.log 2>&1"  # NOQA: E221
        res_dist = subprocess.run(cmd_dist, shell=True)
        if res_dist.returncode != 0:
            LOGGER.error("error occurred at distance command")
            LOGGER.error(f"see {dir}/distance.log")
            exit(1)

        cmd_rmfile = f"rm {dir}/prd_image{extension}"
        subprocess.run(cmd_rmfile, shell=True)

        xyz_rep = np.loadtxt(f"{dir}/interCOM_xyz.xvg")
        dist = np.linalg.norm(xyz_rep[:, [1, 2, 3]], axis=1)
        return dist

    def cal_by_cpptraj(
        self, settings: MDsettings, cycle: int, replica: int
    ) -> List[float]:
        dir = settings.each_replica(_cycle=cycle, _replica=replica)

        # Construct the cpptraj command
        cmd_cpptraj = [
            f"parm {settings.topology}",
            f"trajin {dir}/prd{settings.trajectory_extension}",
            f"center {settings.centering_selection}",
            "image",
            f"distance {settings.selection1} {settings.selection2} out {dir}/interCOM.xvg",
            "run",
            "quit",
        ]
        with open(f"{dir}/calCV.cpptraj", "w") as f:
            f.write("\n".join(cmd_cpptraj))

        res_cpptraj = subprocess.run(
            f"cpptraj -i {dir}/calCV.cpptraj 1> {dir}/distance.log \
                    2>&1 --log {dir}/distance.log",
            shell=True,
        )

        if res_cpptraj.returncode != 0:
            LOGGER.error("error occurred at cpptraj command")
            LOGGER.error(f"see {dir}/distance.log for details")
            exit(1)

        rmsd = np.loadtxt(f"{dir}/interCOM.xvg")[:, 1]
        return rmsd
