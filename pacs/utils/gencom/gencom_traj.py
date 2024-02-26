from pacs.models.settings import MDsettings
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


def gencom_traj(settings: MDsettings, trj_file: str, out_pdb: str, resid: str) -> None:
    if settings.analyzer == "mdtraj":
        gencom_traj_mdtraj(settings, trj_file, out_pdb, resid)
    else:
        LOGGER.error("this analyzer is not supported.")
        exit(1)


def gencom_traj_mdtraj(
    settings: MDsettings, trj_file: str, out_pdb: str, resid: str
) -> None:
    import mdtraj as md

    structure = settings.top_mdtraj
    lig_selection = settings.selection1

    trj = md.load(trj_file, top=structure)
    lig_com = md.compute_center_of_mass(
        trj.atom_slice(trj.top.select(lig_selection))
    ).reshape(
        1, -1, 3
    )  # frame, atom, xyz

    n_frames = lig_com.shape[1]

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
        xyz=lig_com,
        topology=new_top,
        time=time[0],
        unitcell_lengths=ul,
        unitcell_angles=ua,
    )
    pathway.save(out_pdb)
    LOGGER.info(f"visualized pathway was saved at {out_pdb}")
