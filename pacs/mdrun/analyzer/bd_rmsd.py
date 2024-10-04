import subprocess
from typing import List

import numpy as np
from pacs.mdrun.analyzer.superAnalyzer import SuperAnalyzer
from pacs.models.settings import MDsettings, Snapshot, ScoresInCycle, ScoresInOnePair
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


class BD_RMSD(SuperAnalyzer):
    def calculate_scores_in_one_pair(
        self, settings: MDsettings, cycle: int, fore_replica: int, back_replica: int, send_rev
    ) -> ScoresInOnePair:
        if settings.analyzer == "mdtraj":
            ret = self.cal_by_mdtraj(settings, cycle, fore_replica, back_replica)
        elif settings.analyzer == "gromacs":
            raise NotImplementedError
        elif settings.analyzer == "cpptraj":
            raise NotImplementedError
        else:
            raise NotImplementedError
        
        LOGGER.info(f"cycle {cycle} replica ({fore_replica}, {back_replica}) calculated.")
        if send_rev is not None:
            send_rev.send(ret)
        return ret

    def aggregate(self, settings: MDsettings, scores_in_cycle: ScoresInCycle, direction: str) -> np.ndarray:
        aggr_func = np.mean

        if direction == "fore":
            return aggr_func(scores_in_cycle.cv_data, axis=(1, 3))
        elif direction == "back":
            return aggr_func(scores_in_cycle.cv_data, axis=(0, 2))
        else:
            LOGGER.error(f"invalid direction: {direction}")

    def ranking(self, settings: MDsettings, CVs: List[Snapshot]) -> List[Snapshot]:
        sorted_cv = sorted(CVs, key=lambda x: x.cv, reverse=False)
        return sorted_cv

    def is_threshold(self, settings: MDsettings, CVs: List[Snapshot] = None) -> bool:
        if CVs is None:
            CVs = self.CVs
        return CVs[0].cv > settings.threshold
    
    def cal_by_mdtraj(self, settings: MDsettings, cycle: int, fore_replica: int, back_replica: int) -> ScoresInOnePair:
        import mdtraj as md

        fore_dir = settings.each_replica(_cycle=cycle, _direction="fore", _replica=fore_replica)
        back_dir = settings.each_replica(_cycle=cycle, _direction="back", _replica=back_replica)
        fore_trj = md.load(
            f"{fore_dir}/prd{settings.trajectory_extension}",
            top=settings.top_mdtraj_fore,
        )
        back_trj = md.load(
            f"{back_dir}/prd{settings.trajectory_extension}",
            top=settings.top_mdtraj_back,
        )

        # slice (exclude the first frame for gromacs)
        if settings.simulator == "gromacs":
            n_frames_fore = fore_trj.n_frames
            n_frames_back = back_trj.n_frames
            fore_trj = fore_trj.slice(np.arange(1, n_frames_fore))
            back_trj = back_trj.slice(np.arange(1, n_frames_back))
        n_frames_fore = fore_trj.n_frames
        n_frames_back = back_trj.n_frames

        # fit and compute rmsd
        rmsd = np.zeros((n_frames_fore, n_frames_back))
        sel1_arr = fore_trj.top.select(settings.selection1)
        sel2_arr = fore_trj.top.select(settings.selection2)
        sel3_arr = back_trj.top.select(settings.selection3)
        sel4_arr = back_trj.top.select(settings.selection4)

        for frame_i_back in range(n_frames_back):
            back_trj.superpose(
                fore_trj,
                frame_i_back,
                atom_indices=sel1_arr,
                ref_atom_indices=sel3_arr,
            )
            # もうちょい効率化できるかも
            for frame_i_fore in range(n_frames_fore):
                tmp = np.sqrt(
                    3
                    * np.mean(
                        np.square(
                            fore_trj.xyz[frame_i_fore, sel2_arr]
                            - back_trj.xyz[frame_i_back, sel4_arr]
                        ),
                        axis=(0, 1), # xyzのみで平均を取る
                    )
                )
                rmsd[frame_i_fore, frame_i_back] = tmp

        scores_in_one_pair = ScoresInOnePair(
            cycle=cycle,
            fore_replica=fore_replica,
            back_replica=back_replica,
            cv_data=rmsd,
        )

        return scores_in_one_pair