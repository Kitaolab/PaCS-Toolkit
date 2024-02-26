import dataclasses
import subprocess
from typing import List

from pacs.mdrun.exporter.superExporter import SuperExporter
from pacs.models.settings import MDsettings, Snapshot
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


@dataclasses.dataclass
class eAmber(SuperExporter):
    def export_each(
        self,
        settings: MDsettings,
        cycle: int,
        replica_rank: int,
        results: List[Snapshot],
    ) -> None:
        if settings.analyzer == "mdtraj":
            self.export_by_mdtraj(settings, cycle, replica_rank, results)
        elif settings.analyzer == "cpptraj":
            self.export_by_cpptraj(settings, cycle, replica_rank, results)
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

    def export_by_cpptraj(
        self,
        settings: MDsettings,
        cycle: int,
        replica_rank: int,
        results: List[Snapshot],
    ) -> None:
        extension = settings.trajectory_extension
        from_dir = settings.each_replica(
            _cycle=cycle, _replica=results[replica_rank].replica
        )
        # cpptraj frame starts from 1
        selected_frame = results[replica_rank].frame + 1
        out_dir = settings.each_replica(_cycle=cycle + 1, _replica=replica_rank + 1)
        if settings.centering:
            cmd_cpptraj = [
                f"parm {settings.topology}",
                f"trajin {from_dir}/prd{extension}",
                f"center {settings.centering_selection}",
                "image",
                f"trajout {out_dir}/input{settings.structure_extension} \
                        onlyframes {selected_frame}",
                "run",
                "clear all",
                "quit",
            ]
        else:
            cmd_cpptraj = [
                f"parm {settings.topology}",
                f"trajin {from_dir}/prd{extension}",
                f"trajout {out_dir}/input{settings.structure_extension} \
                        onlyframes {selected_frame}",
                "run",
                "clear all",
                "quit",
            ]
        with open(f"{out_dir}/export.cpptraj", "w") as f:
            f.write("\n".join(cmd_cpptraj))
        res_cpptraj = subprocess.run(
            f"cpptraj -i {out_dir}/export.cpptraj \
                    1> {out_dir}/export.log 2>&1 --log {out_dir}/export.log",
            shell=True,
        )  # NOQA: E221
        if res_cpptraj.returncode != 0:
            LOGGER.error("error occurred at cpptraj command")
            LOGGER.error(f"see {out_dir}/cpptraj.log for details")
            exit(1)
