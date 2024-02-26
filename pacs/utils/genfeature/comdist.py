import numpy as np
from pacs.utils.genfeature.genfeat import GenFeatureCore
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


def cal_feature(
    trj_path: str,
    topology: str,
    selection1: str,
    selection2: str,
) -> np.ndarray:
    import mdtraj as md

    trj = md.load(
        f"{trj_path}",
        top=topology,
    )
    com1 = md.compute_center_of_mass(trj.atom_slice(trj.topology.select(selection1)))
    com2 = md.compute_center_of_mass(trj.atom_slice(trj.topology.select(selection2)))
    return np.array([np.linalg.norm(com1[i] - com2[i]) for i in range(len(com1))])


def cal_feature_trial(
    trial: int,
    trj_filename: str,
    topology: str,
    output_directory: str,
    n_parallel: int,
    selection1: str,
    selection2: str,
) -> None:
    gen_core = GenFeatureCore(
        trial=trial,
        trj_filename=trj_filename,
        output_directory=output_directory,
        n_parallel=n_parallel,
    )

    gen_core.prepare()
    gen_core.cal_parallel(cal_feature, topology, selection1, selection2)
