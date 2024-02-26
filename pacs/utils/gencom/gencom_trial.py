from pathlib import Path

from pacs.models.settings import MDsettings
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


def gencom_trial(
    settings: MDsettings,
    trial: int,
    trjfile_name: str,
    out_pdb: str,
    stride_frame: int,
    resid: str,
) -> None:
    if settings.analyzer == "mdtraj":
        gencom_trial_mdtraj(settings, trial, trjfile_name, out_pdb, stride_frame, resid)
    else:
        LOGGER.error("this analyze is not supported.")
        exit(1)


def gencom_trial_mdtraj(
    settings: MDsettings,
    trial: int,
    trjfile_name: str,
    out_pdb: str,
    stride_frame: int,
    resid: str,
) -> None:
    import mdtraj as md
    import numpy as np

    trjfile_name = Path(trjfile_name).name
    structure = settings.top_mdtraj
    lig_selection = settings.selection1
    LOGGER.info("This command is strongly recommended after fitting the trajectory.")

    concat_lig_com = []
    for cycle in range(1, 10000):
        cycle_dir = settings.each_cycle(_trial=trial, _cycle=cycle)
        if not Path(f"{cycle_dir}/summary/cv_ranked.log").exists():
            break
        for rep in range(1, 10000):
            rep_dir = settings.each_replica(_trial=trial, _cycle=cycle, _replica=rep)
            trj_file = f"{rep_dir}/{trjfile_name}"
            if Path(trj_file).exists():
                trj = md.load(trj_file, top=structure, stride=stride_frame)
                lig_com = md.compute_center_of_mass(
                    trj.atom_slice(trj.top.select(lig_selection))
                ).reshape(
                    1, -1, 3
                )  # frame, atom, xyz
            else:
                break
            concat_lig_com.append(lig_com)

    concat_lig_com = np.concatenate(concat_lig_com, axis=1)
    n_frames = concat_lig_com.shape[1]

    new_top = md.Topology()
    new_top.add_chain()
    new_res = new_top.add_residue(
        "COM",
        new_top.chain(0),
        resSeq=resid,
    )
    for i_frame in range(n_frames):
        new_ele = md.element.Element.getBySymbol("VS")  # virtual site
        new_top.add_atom("VS", new_ele, new_res, serial=1 + i_frame)
    time, ul, ua = trj.time, trj.unitcell_lengths[[0], :], trj.unitcell_angles[[0], :]
    pathway = md.Trajectory(
        xyz=concat_lig_com,
        topology=new_top,
        time=time[0],
        unitcell_lengths=ul,
        unitcell_angles=ua,
    )
    pathway.save(out_pdb)
    LOGGER.info(f"number of extracted frames: {n_frames}")
    LOGGER.info("If number of frames is too large, consider increasing stride_frame.")
    LOGGER.info(f"visualized pathway was saved at {out_pdb}")
