import dataclasses
import subprocess
from pathlib import Path
from typing import Dict, List

import numpy as np
from pacs.mdrun.exporter.superExporter import SuperExporter
from pacs.models.settings import MDsettings, Snapshot
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


@dataclasses.dataclass
class eGromacs(SuperExporter):
    def export(self, settings: MDsettings, cycle: int) -> None:
        if cycle == 0:
            self.frame_to_time(settings)
        super().export(settings, cycle)

    def export_each(
        self,
        settings: MDsettings,
        cycle: int,
        replica_rank: int,
        results: List[Snapshot],
    ) -> None:
        if settings.analyzer == "mdtraj":
            self.export_by_mdtraj(settings, cycle, replica_rank, results)
        elif settings.analyzer == "gromacs":
            self.export_by_gmx(settings, cycle, replica_rank, results)
        else:
            raise NotImplementedError

    def export_by_mdtraj(
        self,
        settings: MDsettings,
        cycle: int,
        replica_rank: int,
        results: List[Snapshot],
    ) -> None:
        import mdtraj as md

        extension = settings.trajectory_extension
        from_dir = settings.each_replica(
            _cycle=cycle, _replica=results[replica_rank].replica
        )
        selected_frame = md.load_frame(
            f"{from_dir}/prd{extension}",
            index=results[replica_rank].frame,
            top=settings.top_mdtraj,
        )

        out_dir = settings.each_replica(_cycle=cycle + 1, _replica=replica_rank + 1)
        if settings.centering:
            atom_indices = selected_frame.topology.select(settings.centering_selection)
            anchors = [
                set(
                    [
                        selected_frame.topology.atom(atom_indices[i])
                        for i in range(len(atom_indices))
                    ]
                )
            ]
            selected_frame.image_molecules(anchor_molecules=anchors, inplace=True)
        selected_frame.save(f"{out_dir}/input{settings.structure_extension}")

    def export_by_gmx(
        self,
        settings: MDsettings,
        cycle: int,
        replica_rank: int,
        _results: List[Snapshot],
    ) -> None:
        f2t_dict = self.load_frame_to_time(settings)

        results = []
        dir = settings.each_cycle(_cycle=cycle)
        with open(f"{dir}/summary/cv_ranked.log", "r") as f:
            for line in f:
                _, replica, _, frame, _, _cv = line.split()
                results.append(Snapshot(int(replica), int(frame), _cv))

        for i in range(len(results)):
            results[i].frame = f2t_dict[results[i].frame]

        if settings.n_replica > len(results):
            LOGGER.error(
                f"The total number of frames now is {len(results)}. "
                f"This is less than the number of replicas {settings.n_replica}"
            )
            exit(1)

        extension = settings.trajectory_extension
        from_dir = settings.each_replica(
            _cycle=cycle, _replica=results[replica_rank].replica
        )
        out_dir = settings.each_replica(_cycle=cycle + 1, _replica=replica_rank + 1)

        # treatment for centering option
        if settings.centering is True:
            centering_option = "-center"
            args_to_trjconv = f"{settings.centering_selection} System"
        else:
            centering_option = ""
            args_to_trjconv = "System"

        # treatment for nojump option
        if settings.nojump is True:
            pbc_option = "-pbc nojump"
        else:
            pbc_option = "-pbc whole"

        # First convert trj with -pbc option, and then extract with -b, -e options
        # If we do the both at the same time, the -pbc nojump does not work properly
        # Output the prd_image_prev_cycle to the next cycle to avoid overwrapping.
        cmd_trjconv = f"echo {args_to_trjconv} \
                | {settings.cmd_gmx} trjconv \
                -f {from_dir}/prd{extension} \
                -o {out_dir}/prd_image_prev_cycle{extension} \
                -s {from_dir}/prd.tpr \
                -n {settings.index_file} \
                {pbc_option} \
                {centering_option} \
                1> {from_dir}/trjconv.log 2>&1"  # NOQA: E221

        res_trjconv = subprocess.run(cmd_trjconv, shell=True)

        if res_trjconv.returncode != 0:
            LOGGER.error("error occurred at trjconv command")
            LOGGER.error(f"see {from_dir}/trjconv.log")
            exit(1)

        cmd_extract = f"echo System \
                | {settings.cmd_gmx} trjconv \
                -f {out_dir}/prd_image_prev_cycle{extension} \
                -o {out_dir}/input{settings.structure_extension} \
                -s {from_dir}/prd.tpr \
                -b {results[replica_rank].frame} \
                -e {results[replica_rank].frame} \
                -novel \
                1> {from_dir}/extract.log 2>&1"  # NOQA: E221

        res_extract = subprocess.run(cmd_extract, shell=True)

        if res_extract.returncode != 0:
            LOGGER.error("error occurred at extract command")
            LOGGER.error(f"see {from_dir}/extract.log")
            exit(1)

        # remove the intermediate trajectory
        res_rm = subprocess.run(
            f"rm {out_dir}/prd_image_prev_cycle{extension}", shell=True
        )
        if res_rm.returncode != 0:
            LOGGER.error("error occurred at rm command")
            exit(1)

    def frame_to_time(self, settings: MDsettings) -> None:
        # Output correspondence between frame and time to file
        dir_0_1 = settings.each_replica(_cycle=0, _replica=1)
        if Path(f"{dir_0_1}/frame_time.tsv").exists():
            return
        cmd_pseudo_rms = f"echo 0 0 \
                    | {settings.cmd_gmx} rms \
                    -f {dir_0_1}/prd{settings.trajectory_extension} \
                    -s {dir_0_1}/prd.gro \
                    -o {dir_0_1}/pseudo_rms.xvg \
                    -nomw \
                    -xvg none 1> {dir_0_1}/pseudo_rms.log 2>&1"  # NOQA: E221
        res_pseudo_rms = subprocess.run(cmd_pseudo_rms, shell=True)
        if res_pseudo_rms.returncode != 0:
            LOGGER.error("error occurred at pseudo rms command")
            LOGGER.error(f"see {dir_0_1}/pseudo_rms.log")
            exit(1)
        time_data = np.genfromtxt(f"{dir_0_1}/pseudo_rms.xvg", usecols=0)
        frame_data = np.arange(len(time_data))
        frame_time_data = np.array([frame_data, time_data]).reshape(2, -1).T
        np.savetxt(
            f"{dir_0_1}/frame_time.tsv",
            frame_time_data,
            fmt=("%d", "%.3f"),
            header="frame time(ps)",
            delimiter="\t",
        )

    def load_frame_to_time(self, settings: MDsettings) -> Dict[int, float]:
        # Read correspondence between frame and time from file
        dir_0_1 = settings.each_replica(_cycle=0, _replica=1)
        frame_time_array = np.loadtxt(
            f"{dir_0_1}/frame_time.tsv", delimiter="\t", skiprows=1
        )
        frame_time_dict: Dict[int, float] = {}
        for frame, time in frame_time_array:
            frame_time_dict[int(frame)] = time
        return frame_time_dict
