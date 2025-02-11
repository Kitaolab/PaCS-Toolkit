"""
reference
Inhibition of the hexamerization of SARS-CoV-2 endoribonuclease and modeling of RNA structures bound to the hexamer # NOQA: B950
https://doi.org/10.1038/s41598-022-07792-2
"""


import subprocess
import multiprocessing as mp
from typing import List

import numpy as np
from pacs.mdrun.analyzer.superAnalyzer import SuperAnalyzer
from pacs.models.settings import MDsettings, Snapshot
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


class RMSD(SuperAnalyzer):
    def calculate_cv(
        self, settings: MDsettings, cycle: int, replica: int, queue: mp.Queue
    ) -> List[float]:
        if settings.analyzer == "mdtraj":
            ret = self.cal_by_mdtraj(settings, cycle, replica)
        elif settings.analyzer == "gromacs":
            ret = self.cal_by_gmx(settings, cycle, replica)
        elif settings.analyzer == "cpptraj":
            ret = self.cal_by_cpptraj(settings, cycle, replica)
        else:
            raise NotImplementedError
        queue.put(ret)
        return ret

    def ranking(self, settings: MDsettings, CVs: List[Snapshot]) -> List[Snapshot]:
        sorted_cv = sorted(CVs, key=lambda x: x.cv, reverse=True)
        return sorted_cv

    def is_threshold(self, settings: MDsettings, CVs: List[Snapshot] = None) -> bool:
        if CVs is None:
            CVs = self.CVs
        return CVs[0].cv > settings.threshold

    def cal_by_mdtraj(self, settings: MDsettings, cycle: int, replica: int) -> None:
        import mdtraj as md

        ref = md.load(settings.reference)
        dir = settings.each_replica(_cycle=cycle, _replica=replica)
        trj = md.load(
            f"{dir}/prd{settings.trajectory_extension}",
            top=settings.top_mdtraj,
        )
        trj.superpose(
            ref,
            0,
            atom_indices=trj.top.select(settings.selection1),
            ref_atom_indices=ref.top.select(settings.selection3),
        )
        # md.rmsd performs superposition automatically, so we don't use that typeality here
        rmsd = np.sqrt(
            3
            * np.mean(
                np.square(
                    trj.xyz[:, trj.top.select(settings.selection2)]
                    - ref.xyz[:, ref.top.select(settings.selection4)]
                ),
                axis=(1, 2),
            )
        )
        return rmsd

    def cal_by_gmx(self, settings: MDsettings, cycle: int, replica: int) -> None:
        extension = settings.trajectory_extension
        selection1 = settings.selection1
        selection2 = settings.selection2
        ndx = settings.index_file
        ref = settings.reference
        dir = settings.each_replica(_cycle=cycle, _replica=replica)

        # nojump treatment
        if settings.nojump is True:
            pbc_option = "-pbc nojump"
        else:
            pbc_option = "-pbc mol -ur compact"

        cmd_image = f"echo 'System' \
                | {settings.cmd_gmx} trjconv \
                -f {dir}/prd{extension} \
                -s {dir}/prd.tpr \
                -o {dir}/prd_image{extension} \
                {pbc_option} \
                1> {dir}/image.log 2>&1"  # NOQA: E221

        res_image = subprocess.run(cmd_image, shell=True)
        if res_image.returncode != 0:
            LOGGER.error("error occured at image command")
            LOGGER.error(f"see {dir}/image.log")
            exit(1)

        cmd_rms = f"echo {selection1} {selection2} \
                | {settings.cmd_gmx} rms \
                -f {dir}/prd_image{extension} \
                -s {ref} \
                -o {dir}/rms.xvg \
                -n {ndx} \
                -pbc no \
                -nomw \
                -xvg none 1> {dir}/rms.log 2>&1"  # NOQA: E221
        res_rms = subprocess.run(cmd_rms, shell=True)
        if res_rms.returncode != 0:
            LOGGER.error("error occured at rms command")
            LOGGER.error(f"see {dir}/rms.log")
            exit(1)

        cmd_rmfile = f"rm {dir}/prd_image{extension}"
        subprocess.run(cmd_rmfile, shell=True)

        rmsd_rep = np.loadtxt(f"{dir}/rms.xvg")[:, 1]
        return rmsd_rep
        # output of rms command will be tsv-like format

    def cal_by_cpptraj(
        self, settings: MDsettings, cycle: int, replica: int
    ) -> List[float]:
        dir = settings.each_replica(_cycle=cycle, _replica=replica)

        cmd_cpptraj = [
            f"parm {settings.topology}",
            f"trajin {dir}/prd{settings.trajectory_extension}",
            f"center {settings.centering_selection}",
            "image",
            f"reference {settings.reference} [refstr]",
            f"rms fit ref [refstr] {settings.selection1}",
            f"rms cal ref [refstr] {settings.selection2} nofit out {dir}/rms.xvg",
            "run",
            "quit",
        ]
        """
        cmd_cpptraj = [
            f"parm {settings.topology}",
            f"trajin {dir}/prd{settings.trajectory_extension}",
            # f"center {settings.centering_selection}",
            f"image",
            f"reference {settings.reference} [refstr]",
            f"rms fitting {settings.selection1} {settings.selection3} mass ref [refstr]",
            f"rms rmsd {settings.selection2} {settings.selection4} \
                    mass nofit out {dir}/rms.xvg",
            "run",
            "quit"
        ]
        """
        with open(f"{dir}/calCV.cpptraj", "w") as f:
            f.write("\n".join(cmd_cpptraj))

        res_cpptraj = subprocess.run(
            f"cpptraj -i {dir}/calCV.cpptraj 1> {dir}/rms.log 2>&1 --log {dir}/rms.log",
            shell=True,
        )

        if res_cpptraj.returncode != 0:
            LOGGER.error("error occurred at cpptraj command")
            LOGGER.error(f"see {dir}/rms.log for details")
            exit(1)

        rmsd = np.loadtxt(f"{dir}/rms.xvg")[:, 1]
        return rmsd
