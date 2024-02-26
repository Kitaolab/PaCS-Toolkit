import numpy as np
from pacs.utils.genfeature.genfeat import GenFeatureCore
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


def cal_feature(
    trj_path: str,
    topology: str,
    reference: str,
    selection_fit_trj: str,
    selection_fit_ref: str,
    selection1: str,
    selection2: str,
) -> np.ndarray:
    import mdtraj as md

    trj = md.load(
        f"{trj_path}",
        top=topology,
    )
    ref = md.load(reference)
    trj.superpose(
        ref,
        0,
        atom_indices=trj.top.select(selection_fit_trj),
        ref_atom_indices=ref.top.select(selection_fit_ref),
    )
    com1 = md.compute_center_of_mass(trj.atom_slice(trj.topology.select(selection1)))
    com2 = md.compute_center_of_mass(trj.atom_slice(trj.topology.select(selection2)))
    return np.array([com1[i] - com2[i] for i in range(len(com1))])


def cal_feature_trial(
    trial: int,
    trj_filename: str,
    topology: str,
    output_directory: str,
    n_parallel: int,
    reference: str,
    selection_fit_trj: str,
    selection_fit_ref: str,
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
    gen_core.cal_parallel(
        cal_feature,
        topology,
        reference,
        selection_fit_trj,
        selection_fit_ref,
        selection1,
        selection2,
    )
