import dataclasses
from typing import List

from pacs.mdrun.exporter.superExporter import SuperExporter
from pacs.models.settings import MDsettings, Snapshot
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


@dataclasses.dataclass
class eNamd(SuperExporter):
    def export_each(
        self,
        settings: MDsettings,
        cycle: int,
        replica_rank: int,
        results: List[Snapshot],
    ) -> None:
        if settings.analyzer == "mdtraj":
            self.export_by_mdtraj(settings, cycle, replica_rank, results)
        else:
            raise NotImplementedError

    def export_by_mdtraj(
        self, settings: int, cycle: int, replica_rank: int, results: List[Snapshot]
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
        if settings.centering is True:
            com = md.compute_center_of_mass(
                selected_frame.atom_slice(
                    selected_frame.topology.select(settings.centering_selection)
                )
            )
            selected_frame.xyz = selected_frame.xyz - com
        selected_frame.save(f"{out_dir}/input{settings.structure_extension}")
