"""
reference
Edge expansion parallel cascade selection molecular dynamics simulation for
investigating large-amplitude collective motions of proteins
https://doi.org/10.1063/5.0004654
"""


import pickle
from typing import List

import numpy as np
from pacs.mdrun.analyzer.superAnalyzer import SuperAnalyzer
from pacs.models.settings import MDsettings, Snapshot
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


class EdgeExpansion(SuperAnalyzer):
    def calculate_cv(
        self, settings: MDsettings, cycle: int, replica: int, send_rev
    ) -> List[float]:
        if settings.reference is None:
            settings.reference = f"{settings.each_replica(_cycle=0, _replica=1)}/prd{settings.trajectory_extension}"  # NOQA: B950

        if cycle == 0:
            self.pca(settings, cycle, replica)

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
        from scipy.spatial import ConvexHull

        points = []
        for cv in CVs:
            points.append(cv.cv)
        points = np.array(points)

        sorted_cv = []
        while len(points) > 10:
            hull = ConvexHull(points)
            vertices = hull.vertices
            np.random.shuffle(vertices)
            for v in vertices:
                for snapshot in CVs:
                    if np.allclose(snapshot.cv, points[v]):
                        sorted_cv.append(snapshot)
                        break
            points = np.delete(points, hull.vertices, axis=0)
        for p in points:
            for snapshot in CVs:
                if np.allclose(snapshot.cv, p):
                    sorted_cv.append(snapshot)
                    break
        return sorted_cv

    def is_threshold(self, settings: MDsettings, CVs: List[Snapshot] = None) -> bool:
        # Terminate PaCS-MD only when max_cycle is reached, independent of CV value
        return False

    def pca(self, settings: MDsettings, cycle: int, replica: int):
        import mdtraj as md
        from sklearn.decomposition import PCA

        ref_trj = md.load(settings.reference, top=settings.top_mdtraj)
        ref_trj.superpose(
            ref_trj,
            0,
            atom_indices=ref_trj.top.select(settings.selection3),
            ref_atom_indices=ref_trj.top.select(settings.selection3),
        )
        ref_trj_selected = ref_trj.atom_slice(ref_trj.top.select(settings.selection4))
        pca = PCA(n_components=4)
        pca.fit(
            ref_trj_selected.xyz.reshape(
                ref_trj_selected.n_frames, ref_trj_selected.n_atoms * 3
            )
        )
        pickle.dump(
            pca, open(f"{settings.each_replica(_cycle=0, _replica=1)}/pca.pkl", "wb")
        )

    def cal_by_mdtraj(
        self, settings: MDsettings, cycle: int, replica: int
    ) -> List[float]:
        import mdtraj as md

        ref = md.load(settings.reference, top=settings.top_mdtraj)
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

        trj_selected = trj.atom_slice(trj.top.select(settings.selection2))

        PCAspace = pickle.load(
            open(f"{settings.each_replica(_cycle=0, _replica=1)}/pca.pkl", "rb")
        )
        pca_coor = PCAspace.transform(
            trj_selected.xyz.reshape(trj_selected.n_frames, trj_selected.n_atoms * 3)
        )
        return pca_coor

    def cal_by_gmx(self, settings: MDsettings, cycle: int, replica: int) -> List[float]:
        raise NotImplementedError

    def cal_by_cpptraj(
        self, settings: MDsettings, cycle: int, replica: int
    ) -> List[float]:
        raise NotImplementedError
