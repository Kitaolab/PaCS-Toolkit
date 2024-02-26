import multiprocessing as mp
import subprocess
from pathlib import Path

from pacs.models.settings import MDsettings
from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


def fit(settings: MDsettings, trj_file: str, out_file: str) -> None:
    if settings.analyzer == "mdtraj":
        fit_mdtraj(settings, trj_file, out_file)
    else:
        raise NotImplementedError


def fit_trial(settings: MDsettings, trj_file: str, out_file: str) -> None:
    job_list = []
    for path in Path(".").glob(f"./trial{settings.trial:03}/cycle*/replica*"):
        if not Path(f"{path}/{trj_file}").exists():
            LOGGER.error(f"trajectory file {path}/{trj_file} is not found.")
            exit(1)
        p = mp.Process(target=fit, args=(settings, f"{path}/{trj_file}", out_file))
        p.start()
        job_list.append(p)

        if len(job_list) == settings.n_parallel:
            for proc in job_list:
                proc.join()
            for proc in job_list:
                if proc.exitcode != 0:
                    LOGGER.error("error occurred at child process")
                    exit(1)
            for proc in job_list:
                proc.close()
            job_list = []

    if len(job_list) != 0:
        for proc in job_list:
            proc.join()
        for proc in job_list:
            if proc.exitcode != 0:
                LOGGER.error("error occurred at child process")
                exit(1)
        for proc in job_list:
            proc.close()
        job_list = []


def fit_mdtraj(settings: MDsettings, trj_file: str, out_file: str) -> None:
    import mdtraj as md

    ext = Path(trj_file).suffix
    parent = Path(trj_file).parent
    stem = Path(trj_file).stem
    fit_trj_file = (
        f"{parent}/{stem}_fit{ext}" if out_file == None else f"{parent}/{out_file}"
    )

    ref_structure = settings.reference
    trj_selection = settings.selection1
    ref_selection = settings.selection2

    trj = md.load(trj_file, top=settings.top_mdtraj)
    ref = md.load(ref_structure)
    fit_trj = trj.superpose(
        ref,
        atom_indices=trj.top.select(trj_selection),
        ref_atom_indices=ref.top.select(ref_selection),
    )

    fit_trj.save(fit_trj_file)
    LOGGER.info(f"a new trajectory file is saved as {fit_trj_file}")
