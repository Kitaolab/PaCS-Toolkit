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
    selection_cal_trj: str,
    selection_cal_ref: str,
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
    # md.rmsd performs superposition automatically, so we don't use that typeality here
    rmsd = np.sqrt(
        3
        * np.mean(
            np.square(
                trj.xyz[:, trj.top.select(selection_cal_trj)]
                - ref.xyz[:, ref.top.select(selection_cal_ref)]
            ),
            axis=(1, 2),
        )
    )
    return rmsd


def cal_feature_trial(
    trial: int,
    trj_filename: str,
    topology: str,
    output_directory: str,
    n_parallel: int,
    reference: str,
    selection_fit_trj: str,
    selection_fit_ref: str,
    selection_cal_trj: str,
    selection_cal_ref: str,
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
        selection_cal_trj,
        selection_cal_ref,
    )
