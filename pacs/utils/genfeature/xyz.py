import numpy as np
from pacs.utils.genfeature.genfeat import GenFeatureCore
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


def cal_feature(
    trj_path: str,
    topology: str,
    selection: str,
) -> np.ndarray:
    import mdtraj as md

    trj = md.load(
        f"{trj_path}",
        top=topology,
    )
    return trj.atom_slice(trj.topology.select(selection)).xyz


def cal_feature_trial(
    trial: int,
    trj_filename: str,
    topology: str,
    output_directory: str,
    n_parallel: int,
    selection: str,
) -> None:
    gen_core = GenFeatureCore(
        trial=trial,
        trj_filename=trj_filename,
        output_directory=output_directory,
        n_parallel=n_parallel,
    )

    gen_core.prepare()
    gen_core.cal_parallel(cal_feature, topology, selection)
