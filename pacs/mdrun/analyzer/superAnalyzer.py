import dataclasses
import multiprocessing as mp
import re
import subprocess
from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import List

import numpy as np
from pacs.models.settings import MDsettings, Snapshot
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)
np.set_printoptions(suppress=True)


@dataclasses.dataclass
class SuperAnalyzer(metaclass=ABCMeta):
    CVs: List[float] = None

    @abstractmethod
    def calculate_cv(
        self, settings: MDsettings, cycle: int, replica: int, queue: mp.Queue
    ) -> List[float]:
        pass

    @abstractmethod
    def ranking(self, settings: MDsettings, CVs: List[Snapshot]) -> List[Snapshot]:
        pass

    @abstractmethod
    def is_threshold(self, settings: MDsettings, CVs: List[Snapshot] = None) -> bool:
        pass

    def pbc_by_gmx(self, settings: MDsettings, dir: str) -> str:
        """
        PBC treatment of {dir}/prd before CV calculation with gromacs.
        Returns the path of the trajectory that the analysis should use.

        pbc_level = 1 : no treatment, the raw trajectory is used
        pbc_level = 2 : -pbc mol                                   -> prd_image.xtc
        pbc_level = 3 : -center on centering_atom_for_PBC          -> tmp1.xtc
                        (atom number, or index group name of 1 atom)
                        -pbc atom                                  -> tmp2.xtc
                        -pbc mol                                   -> tmp3.xtc
        """
        prd = f"{dir}/prd{settings.trajectory_extension}"
        tpr = f"{dir}/prd.tpr"

        def trjconv(
            groups: str, src: str, out: str, option: str, log: str, ndx: str
        ) -> None:
            cmd = f"echo {groups} \
                    | {settings.cmd_gmx} trjconv \
                    -f {src} \
                    -s {tpr} \
                    -n {ndx} \
                    -o {out} \
                    {option} \
                    1> {dir}/{log} 2>&1"  # NOQA: E221
            res = subprocess.run(cmd, shell=True)
            if res.returncode != 0:
                LOGGER.error(f"error occurred at trjconv ({option})")
                LOGGER.error(f"see {dir}/{log}")
                exit(1)

        if settings.pbc_level == 1:
            return prd

        if settings.pbc_level == 2:
            out = f"{dir}/prd_image.xtc"
            trjconv("System", prd, out, "-pbc mol", "image.log", settings.index_file)
            return out

        # pbc_level == 3
        if isinstance(settings.centering_atom_for_PBC, int):
            # atom number: add a group that holds only this atom
            # to a copy of the index file
            ndx = f"{dir}/pbc_center.ndx"
            group = "PaCS_PBC_center"
            with open(settings.index_file, "r") as f_in, open(ndx, "w") as f_out:
                f_out.write(f_in.read().rstrip("\n") + "\n")
                f_out.write(f"[ {group} ]\n{settings.centering_atom_for_PBC}\n")
        else:
            # index group name (checked to contain exactly 1 atom in settings)
            ndx = settings.index_file
            group = settings.centering_atom_for_PBC

        tmp1, tmp2, tmp3 = (f"{dir}/tmp{i}.xtc" for i in (1, 2, 3))
        trjconv(f"{group} System", prd, tmp1, "-center", "pbc_center.log", ndx)
        trjconv("System", tmp1, tmp2, "-pbc atom", "pbc_atom.log", ndx)
        trjconv("System", tmp2, tmp3, "-pbc mol", "pbc_mol.log", ndx)
        subprocess.run(f"rm -f {tmp1} {tmp2}", shell=True)
        return tmp3

    def pbc_cmds_cpptraj(self, settings: MDsettings) -> List[str]:
        """
        cpptraj commands for PBC treatment before CV calculation.

        pbc_level = 1 : no treatment
        pbc_level = 2 : image
        pbc_level = 3 : center <centering_atom_for_PBC>, then image
        """
        if settings.pbc_level == 1:
            return []
        if settings.pbc_level == 2:
            return ["image"]
        return [f"center {settings.centering_mask_cpptraj()}", "image"]

    def pbc_by_mdtraj(self, settings: MDsettings, trj) -> None:
        """
        PBC treatment of an mdtraj trajectory in place before CV calculation.
        Same procedure as gromacs (see pacs.utils.pbc_mdtraj):

        pbc_level = 1 : no treatment
        pbc_level = 2 : make molecules whole, molecule COM in the box (-pbc mol)
        pbc_level = 3 : centering_atom_for_PBC -> box center (-center),
                        every atom in the box (-pbc atom), then -pbc mol
        Only molecules containing selection1/selection2 atoms are made whole.
        """
        from pacs.utils.pbc_mdtraj import treat_pbc

        if settings.pbc_level == 1:
            return
        if trj.unitcell_vectors is None:
            LOGGER.error(
                f"pbc_level = {settings.pbc_level} requires box information, "
                "but the trajectory has none. Use pbc_level = 1."
            )
            exit(1)

        center_atom = None
        if settings.pbc_level == 3:
            center_atom = settings.centering_atom_index_mdtraj(trj.topology)

        atom_indices = set()
        for sel in [settings.selection1, settings.selection2]:
            if sel is not None:
                atom_indices.update(trj.topology.select(sel).tolist())
        treat_pbc(
            trj,
            settings.pbc_level,
            center_atom=center_atom,
            atom_indices=atom_indices if atom_indices else None,
        )

    def remove_pbc_traj(self, settings: MDsettings, dir: str, traj: str) -> None:
        # never remove the raw trajectory (pbc_level = 1)
        if traj != f"{dir}/prd{settings.trajectory_extension}":
            subprocess.run(f"rm -f {traj}", shell=True)

    def write_cv_to_file(
        self, output_file: str, cv_arr: List[Snapshot], settings: MDsettings, cycle: int
    ) -> None:
        dir = settings.each_cycle(_cycle=cycle)
        with open(f"{dir}/summary/{output_file}", "w") as f:
            for snapshot in cv_arr:
                f.write(f"{snapshot}" + "\n")

    def analyze(self, settings: MDsettings, cycle: int) -> List[Snapshot]:
        dir = settings.each_cycle(_cycle=cycle)
        if Path(f"{dir}/summary/cv_ranked.log").exists():
            pattern1 = r"replica (\d+) frame (\d+) cv \[([-\d.\s]+)\]"
            pattern2 = r"replica (\d+) frame (\d+) cv ([-\d.]+)"
            results = []
            with open(f"{dir}/summary/cv_ranked.log", "r") as f:
                for line in f:
                    match1 = re.search(pattern1, line)
                    match2 = re.search(pattern2, line)
                    if match1:
                        replica = int(match1.group(1))
                        frame = int(match1.group(2))
                        cv_values = [float(x) for x in match1.group(3).split()]
                    elif match2:
                        replica = int(match2.group(1))
                        frame = int(match2.group(2))
                        cv_values = float(match2.group(3))
                    else:
                        LOGGER.error(
                            "pattern matching failed. please check the log file."
                        )
                        exit(1)

                    results.append(Snapshot(int(replica), int(frame), cv_values))
            LOGGER.info("analyzer was skipped")
            return results

        queue = mp.Queue(maxsize=0)
        # one slot per replica: cv_arr[replica - 1] holds that replica's CVs,
        # so the order does not depend on which process finishes first
        cv_arr = [None] * settings.n_replica
        n_loop = (settings.n_replica + settings.n_parallel - 1) // settings.n_parallel
        replicas = [x + 1 for x in range(settings.n_replica)]
        for i in range(n_loop):
            batch = replicas[i * settings.n_parallel : (i + 1) * settings.n_parallel]
            job_list = []
            for replica in batch:
                p = mp.Process(
                    target=self.calculate_cv, args=(settings, cycle, replica, queue)
                )
                job_list.append(p)
                p.start()

            for _ in range(len(job_list)):
                replica, ret = queue.get()
                cv_arr[replica - 1] = ret

            for proc in job_list:
                proc.join()

            for proc in job_list:
                if proc.exitcode != 0:
                    LOGGER.error("error occurred at child process")
                    exit(1)

            # Not necessary, but just in case.
            for proc in job_list:
                proc.close()

        # just in case
        queue.close()
        queue.join_thread()
        missing = [rep + 1 for rep, cv in enumerate(cv_arr) if cv is None]
        if missing:
            LOGGER.error(f"no CV was returned for replica(s) {missing}")
            exit(1)

        cv_arr = np.array(cv_arr)
        if len(cv_arr.shape) == 2:
            cv_arr = cv_arr.flatten()
        else:
            cv_arr = cv_arr.reshape(-1, cv_arr.shape[-1])
        n_frame = len(cv_arr) // settings.n_replica

        results: List[Snapshot] = []
        iter = 0
        for rep in range(1, settings.n_replica + 1):
            for frame in range(0, n_frame):
                snapshot = Snapshot(rep, frame, cv_arr[iter])
                iter += 1
                # Exclude the first frame of the trajectory file in gromacs
                # because it is the initial structure
                if settings.simulator == "gromacs" and frame == 0:
                    continue
                results.append(snapshot)

        self.write_cv_to_file("cv.log", results, settings, cycle)
        self.CVs = results[:: settings.skip_frame]
        self.CVs = self.ranking(settings, self.CVs)
        self.write_cv_to_file("cv_ranked.log", self.CVs, settings, cycle)
        LOGGER.info(f"The top ranking CV is {self.CVs[0]}")

        return self.CVs
