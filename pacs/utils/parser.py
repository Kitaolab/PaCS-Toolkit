import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

import tomli
from pacs._version import __version__
from pacs.models.settings import MDsettings
from pacs.utils.fit import fit, fit_trial
from pacs.utils.gencom.gencom_traj import gencom_traj
from pacs.utils.gencom.gencom_trial import gencom_trial
from pacs.utils.genfeature import comdist, comvec, rmsd, xyz
from pacs.utils.genrepresent import genrepresent
from pacs.utils.logger import generate_logger
from pacs.utils.rmfile import rmfile_all
from pacs.utils.rmmol import make_top, rmmol_all, rmmol_log_add_info

# toml lib is not used


LOGGER = generate_logger(__name__)


class Parser:
    def parse(self) -> MDsettings:
        parser = argparse.ArgumentParser(
            description="PaCS-Toolkit: Tool Kit for \
                    Parallel Cascade Selection Molecular Dynamic Simulation"
        )
        parser.add_argument("-V", "--version", action="store_true", help="show version")
        subparsers = parser.add_subparsers()

        # mdrun
        parser_mdrun = subparsers.add_parser("mdrun", help="run PaCS-MD")
        parser_mdrun.add_argument(
            "-t",
            "--trial",
            type=str,
            required=True,
            help="trial number without 0-fill when pacsmd was conducted (e.g. -t 1)",
        )
        parser_mdrun.add_argument(
            "-f",
            "--file",
            type=str,
            required=True,
            help="input file name",
        )

        # genrepresent
        parser_genrepresent = subparsers.add_parser(
            "genrepresent",
            help="generate representative pathways along the PaCS-MD cycles.",
        )
        parser_genrepresent_sub = parser_genrepresent.add_subparsers()

        # genrepresent mdtraj
        parser_genrepresent_mdtraj = parser_genrepresent_sub.add_parser(
            "mdtraj", help="using mdtraj"
        )
        parser_genrepresent_mdtraj.add_argument(
            "-t",
            "--trial",
            type=int,
            required=True,
            help="trial number without 0-fill when pacsmd was conducted (e.g. -t 1)",
        )
        parser_genrepresent_mdtraj.add_argument(
            "-trj",
            "--trajectory",
            type=str,
            required=True,
            help="trajectory file name (e.g. prd.xtc, prd_rmmol.nc)",
        )
        parser_genrepresent_mdtraj.add_argument(
            "-top",
            "--topology",
            type=str,
            required=True,
            help="topology file path for mdtraj (e.g. pdb, gro, parm7, etc)",
        )

        # genrepresent gmx
        parser_genrepresent_gmx = parser_genrepresent_sub.add_parser(
            "gmx", help="using gromacs"
        )
        parser_genrepresent_gmx.add_argument(
            "-t",
            "--trial",
            type=int,
            required=True,
            help="trial number without 0-fill when pacsmd was conducted (e.g. -t 1)",
        )
        parser_genrepresent_gmx.add_argument(
            "-trj",
            "--trajectory",
            type=str,
            required=True,
            help="trajectory file name (e.g. prd.xtc, prd_rmmol.trr)",
        )
        parser_genrepresent_gmx.add_argument(
            "-top",
            "--topology",
            type=str,
            required=True,
            help="topology file path for gromacs (e.g. tpr, gro, top, etc)",
        )
        parser_genrepresent_gmx.add_argument(
            "-g",
            "--cmd_gmx",
            type=str,
            required=True,
            help="gromacs command prefix. (e.g. --cmd_gmx gmx, --cmd_gmx gmx_mpi)",
        )

        # genrepresent cpptraj
        parser_genrepresent_cpptraj = parser_genrepresent_sub.add_parser(
            "cpptraj", help="using cpptraj"
        )
        parser_genrepresent_cpptraj.add_argument(
            "-t",
            "--trial",
            type=int,
            required=True,
            help="trial number without 0-fill when pacsmd was conducted (e.g. -t 1)",
        )
        parser_genrepresent_cpptraj.add_argument(
            "-trj",
            "--trajectory",
            type=str,
            required=True,
            help="trajectory file name (e.g. prd.nc, prd_rmmol.nc)",
        )
        parser_genrepresent_cpptraj.add_argument(
            "-top",
            "--topology",
            type=str,
            help="amber topology file path.",
        )

        # rmmol
        parser_rmmol = subparsers.add_parser(
            "rmmol",
            help="reduce the size of MD trajectories by selecting necessary molecules",
        )
        parser_rmmol_sub = parser_rmmol.add_subparsers()

        # rmmol mdtraj
        parser_rmmol_mdtraj = parser_rmmol_sub.add_parser("mdtraj", help="using mdtraj")
        parser_rmmol_mdtraj.add_argument(
            "-t",
            "--trial",
            type=int,
            required=True,
            help="trial number without 0-fill when pacsmd was conducted (e.g. -t 1)",
        )

        parser_rmmol_mdtraj.add_argument(
            "-k",
            "--keep_selection",
            type=str,
            required=True,
            help='selection to be retained in trajectory files. (e.g. "not water")',
        )
        parser_rmmol_mdtraj.add_argument(
            "-e",
            "--trajectory_extension",
            type=str,
            help="gromacs trajectory extension. (e.g. -e .xtc, -e .trr)",
        )
        parser_rmmol_mdtraj.add_argument(
            "-m",
            "--top_mdtraj",
            type=str,
            required=True,
            help="topology file for mdtraj (e.g. pdb, gro, parm7, etc)",
        )

        # rmmol gmx
        parser_rmmol_gmx = parser_rmmol_sub.add_parser("gmx", help="using gmx")
        parser_rmmol_gmx.add_argument(
            "-t",
            "--trial",
            type=int,
            required=True,
            help="trial number without 0-fill when pacsmd was conducted (e.g. -t 1)",
        )

        parser_rmmol_gmx.add_argument(
            "-k",
            "--keep_selection",
            type=str,
            required=True,
            help="index group to be retained in trajectory files.",
        )
        parser_rmmol_gmx.add_argument(
            "-n", "--index_file", type=str, required=True, help="index file"
        )
        parser_rmmol_gmx.add_argument(
            "-g",
            "--cmd_gmx",
            type=str,
            required=True,
            help="gromacs command prefix. (e.g. --cmd_gmx gmx, --cmd_gmx gmx_mpi)",
        )
        parser_rmmol_gmx.add_argument(
            "-e",
            "--trajectory_extension",
            type=str,
            default=".xtc",
            choices=[".xtc", ".trr"],
            help="gromacs trajectory extension. (e.g. -e .xtc, -e .trr)",
        )
        parser_rmmol_gmx.add_argument(
            "--nojump",
            action="store_true",
            help="execute gromacs pbc nojump treatment",
        )

        # rmmol cpptraj
        parser_rmmol_cpptraj = parser_rmmol_sub.add_parser(
            "cpptraj", help="using cpptraj"
        )
        parser_rmmol_cpptraj.add_argument(
            "-t",
            "--trial",
            type=int,
            required=True,
            help="trial number without 0-fill when pacsmd was conducted (e.g. -t 1)",
        )

        parser_rmmol_cpptraj.add_argument(
            "-k",
            "--keep_selection",
            type=str,
            required=True,
            help='index grop to be retained in trajectory files. (e.g. "not water")',
        )
        parser_rmmol_cpptraj.add_argument(
            "-e",
            "--trajectory_extension",
            type=str,
            help="amber trajectory extension. (e.g. -e .nc)",
        )
        parser_rmmol_cpptraj.add_argument(
            "-p", "--topology", type=str, help="amber topology file path"
        )

        # rmfile
        parser_rmfile = subparsers.add_parser(
            "rmfile", help="remove unnecessary files for PaCS-MD and analysis"
        )

        parser_rmfile.add_argument(
            "-t",
            "--trial",
            type=int,
            required=True,
            help="trial number without 0-fill when pacsmd was conducted (e.g. -t 1)",
        )

        parser_rmfile.add_argument(
            "-s",
            "--simulator",
            required=True,
            choices=["gromacs", "namd", "amber"],
            help="Name of simulator used in when using PaCS-MD",
        )

        # fit
        parser_fit = subparsers.add_parser(
            "fit",
            help="regenerate MD trajectories by best-fitting selected regions/molecules.",
        )
        parser_fit_sub = parser_fit.add_subparsers()

        # fit traj
        parser_fit_traj = parser_fit_sub.add_parser(
            "traj",
            help="apply to single trajectory file",
        )
        parser_fit_traj_sub = parser_fit_traj.add_subparsers()

        # mdtraj
        parser_fit_traj_mdtraj = parser_fit_traj_sub.add_parser(
            "mdtraj", help="using mdtraj"
        )
        parser_fit_traj_mdtraj.add_argument(
            "-tf", "--trj-file", type=str, required=True, help="trajectory file path"
        )
        parser_fit_traj_mdtraj.add_argument(
            "-top",
            "--topology",
            type=str,
            required=True,
            help="structure file path for mdtraj",
        )
        parser_fit_traj_mdtraj.add_argument(
            "-r",
            "--ref-structure",
            type=str,
            required=True,
            help="reference structure file path for fitting",
        )
        parser_fit_traj_mdtraj.add_argument(
            "-ts",
            "--trj-selection",
            type=str,
            required=True,
            help="selection for fitting in trajectory",
        )
        parser_fit_traj_mdtraj.add_argument(
            "-rs",
            "--ref-selection",
            type=str,
            required=True,
            help="selection for fitting in reference",
        )
        parser_fit_traj_mdtraj.add_argument(
            "-p",
            "--n_parallel",
            type=int,
            default=1,
            help="number of parallel [default: 1]",
        )
        parser_fit_traj_mdtraj.add_argument(
            "-o",
            "--out",
            type=str,
            default=None,
            help="output file name [default: {traj}_fit{ext}]",
        )

        # trial
        parser_fit_trial = parser_fit_sub.add_parser(
            "trial",
            help="apply to single pacsmd trial",
        )
        parser_fit_trial_sub = parser_fit_trial.add_subparsers()

        # mdtraj
        parser_fit_trial_mdtraj = parser_fit_trial_sub.add_parser(
            "mdtraj", help="using mdtraj"
        )
        parser_fit_trial_mdtraj.add_argument(
            "-t",
            "--trial",
            type=int,
            required=True,
            help="trial number without 0-fill when pacsmd was conducted (e.g. -t 1)",
        )
        parser_fit_trial_mdtraj.add_argument(
            "-tf", "--trj-file", type=str, required=True, help="trajectory file name"
        )
        parser_fit_trial_mdtraj.add_argument(
            "-top",
            "--topology",
            type=str,
            required=True,
            help="topology file path for mdtraj",
        )
        parser_fit_trial_mdtraj.add_argument(
            "-r",
            "--ref-structure",
            type=str,
            required=True,
            help="reference structure file path for fitting",
        )
        parser_fit_trial_mdtraj.add_argument(
            "-ts",
            "--trj-selection",
            type=str,
            required=True,
            help="selection for fitting in trajectory",
        )
        parser_fit_trial_mdtraj.add_argument(
            "-rs",
            "--ref-selection",
            type=str,
            required=True,
            help="selection for fitting in reference",
        )
        parser_fit_trial_mdtraj.add_argument(
            "-p",
            "--n_parallel",
            type=int,
            default=1,
            help="number of parallel [default: 1]",
        )
        parser_fit_trial_mdtraj.add_argument(
            "-o",
            "--out",
            type=str,
            default=None,
            help="output file name [default: {traj}_fit{ext}]",
        )

        # gmx
        # parser_fit_gmx = parser_fit_sub.add_parser("gmx", help="using gmx")
        # parser_fit_gmx.add_argument(
        #    "-t",
        #    "--trial",
        #    type=int,
        #    required=True,
        #    help="trial number without 0-fill when pacsmd was conducted (e.g. -t 1)",
        # )
        # parser_fit_gmx.add_argument(
        #    "-tf", "--trj-file", type=str, required=True, help="trajectory file path"
        # )
        # parser_fit_gmx.add_argument(
        #    "-p",
        #    "--n_parallel",
        #    type=int,
        #    default=1,
        #    help="number of parallel [default: 1]",
        # )
        # parser_fit_gmx.add_argument(
        #    "-r",
        #    "--ref-structure",
        #    type=str,
        #    required=True,
        #    help="reference tpr file path for fitting",
        # )
        # parser_fit_gmx.add_argument(
        #    "-ts",
        #    "--trj-selection",
        #    type=str,
        #    required=True,
        #    help="selection group for fitting in trajectory",
        # )
        # parser_fit_gmx.add_argument(
        #    "-g",
        #    "--cmd_gmx",
        #    type=str,
        #    required=True,
        #    help="gromacs command prefix. (e.g. --cmd_gmx gmx, --cmd_gmx gmx_mpi)",
        # )

        # gencom
        parser_gencom = subparsers.add_parser(
            "gencom",
            help="generate COM trajectories of a molecule in PDB format (.pdb).",
        )
        parser_gencom_sub = parser_gencom.add_subparsers()

        # gencom_traj
        parser_gencom_traj = parser_gencom_sub.add_parser(
            "traj", help="apply single trajectory file"
        )
        parser_gencom_traj_sub = parser_gencom_traj.add_subparsers()

        # gencom_traj_mdtraj
        parser_gencom_traj_mdtraj = parser_gencom_traj_sub.add_parser(
            "mdtraj", help="using mdtraj"
        )
        parser_gencom_traj_mdtraj.add_argument(
            "-trj",
            "--trj-file",
            type=str,
            required=True,
            help="trajectory file path (e.g. repr.xtc, repr_fit.xtc)",
        )
        parser_gencom_traj_mdtraj.add_argument(
            "-top",
            "--topology",
            type=str,
            required=True,
            help="topology file path for mdtraj topology",
        )
        parser_gencom_traj_mdtraj.add_argument(
            "-s",
            "--selection",
            type=str,
            required=True,
            help="selection string to visualize the COM",
        )
        parser_gencom_traj_mdtraj.add_argument(
            "-r",
            "--resid",
            type=int,
            default=1,
            help="resid for vitual site of com of ligand [default: 1]",
        )
        parser_gencom_traj_mdtraj.add_argument(
            "-o",
            "--out-pdb",
            type=str,
            default="pathway.pdb",
            help="output pdb file path [default: pathway.pdb]",
        )

        # gencom_trial
        parser_gencom_trial = parser_gencom_sub.add_parser(
            "trial", help="apply single pacsmd trial"
        )
        parser_gencom_trial_sub = parser_gencom_trial.add_subparsers()

        # gencom_trial_mdtraj
        parser_gencom_trial_mdtraj = parser_gencom_trial_sub.add_parser(
            "mdtraj", help="using mdtraj"
        )
        parser_gencom_trial_mdtraj.add_argument(
            "-t",
            "--trial",
            type=int,
            required=True,
            help="trial number without 0-fill when pacsmd was conducted (e.g. -t 1)",
        )
        parser_gencom_trial_mdtraj.add_argument(
            "-trj",
            "--trjfile-name",
            type=str,
            default="prd_rmmol_fit.xtc",
            help="trajectory file name [default: prd_rmmol_fit.xtc].",
        )
        parser_gencom_trial_mdtraj.add_argument(
            "-top",
            "--topology",
            type=str,
            required=True,
            help="topology file path for mdtraj topology",
        )
        parser_gencom_trial_mdtraj.add_argument(
            "-s",
            "--selection",
            type=str,
            required=True,
            help="selection string to visualize the COM",
        )
        parser_gencom_trial_mdtraj.add_argument(
            "-r",
            "--resid",
            type=int,
            default=1,
            help="resid for vitual site of com of ligand [default: 1]",
        )
        parser_gencom_trial_mdtraj.add_argument(
            "-o",
            "--out-pdb",
            type=str,
            default="all_pathway.pdb",
            help="output pdb file path [default: pathway.pdb]",
        )
        parser_gencom_trial_mdtraj.add_argument(
            "-sf",
            "--stride-frame",
            type=int,
            default=10,
            help="stride to skip when extracting the com for visualization [default: 10]",
        )

        # genfeature
        parser_genfeature = subparsers.add_parser(
            "genfeature",
            help="calculate features and output(.npy) for the MSM analysis",
        )
        parser_genfeature_sub = parser_genfeature.add_subparsers()

        # comvec
        parser_genfeature_comvec = parser_genfeature_sub.add_parser(
            "comvec", help="COM Vector(3D) based feature"
        )
        parser_genfeature_comvec_sub = parser_genfeature_comvec.add_subparsers()

        # mdtraj
        parser_genfeature_comvec_mdtraj = parser_genfeature_comvec_sub.add_parser(
            "mdtraj", help="using mdtraj"
        )
        parser_genfeature_comvec_mdtraj.add_argument(
            "-t", "--trial", type=int, required=True, help="trial number without 0-fill"
        )
        parser_genfeature_comvec_mdtraj.add_argument(
            "-tf",
            "--trj-file",
            type=str,
            required=True,
            help="trajectory file name (e.g. prd.xtc prd_rmmol.trr)",
        )
        parser_genfeature_comvec_mdtraj.add_argument(
            "-top",
            "--topology",
            type=str,
            required=True,
            help="topology file path for mdtraj",
        )
        parser_genfeature_comvec_mdtraj.add_argument(
            "-od",
            "--outdir",
            type=str,
            default="comvec-genfeature",
            help="output directory path [default: comvec-genfeature]",
        )
        parser_genfeature_comvec_mdtraj.add_argument(
            "-p",
            "--n_parallel",
            type=int,
            default=1,
            help="number of parallel [default: 1]",
        )
        parser_genfeature_comvec_mdtraj.add_argument(
            "-ref",
            "--reference",
            type=str,
            required=True,
            help="reference structure file path for fitting",
        )
        parser_genfeature_comvec_mdtraj.add_argument(
            "-ft",
            "--fit-trj",
            type=str,
            required=True,
            help="mdtraj selection for fitting in trajectory",
        )
        parser_genfeature_comvec_mdtraj.add_argument(
            "-fr",
            "--fit-ref",
            type=str,
            required=True,
            help="mdtraj selection for fitting in reference",
        )
        parser_genfeature_comvec_mdtraj.add_argument(
            "-s1",
            "--selection1",
            type=str,
            required=True,
            help="mdtraj selection1 for calculating comvec in trajectory",
        )
        parser_genfeature_comvec_mdtraj.add_argument(
            "-s2",
            "--selection2",
            type=str,
            required=True,
            help="mdtraj selection2 for calculating comvec in trajectory",
        )

        # rmsd
        parser_genfeature_rmsd = parser_genfeature_sub.add_parser(
            "rmsd", help="RMSD based feature"
        )
        parser_genfeature_rmsd_sub = parser_genfeature_rmsd.add_subparsers()

        # mdtraj
        parser_genfeature_rmsd_mdtraj = parser_genfeature_rmsd_sub.add_parser(
            "mdtraj", help="using mdtraj"
        )
        parser_genfeature_rmsd_mdtraj.add_argument(
            "-t", "--trial", type=int, required=True, help="trial number without 0-fill"
        )
        parser_genfeature_rmsd_mdtraj.add_argument(
            "-tf",
            "--trj-file",
            type=str,
            required=True,
            help="trajectory file name (e.g. prd.xtc prd_rmmol.trr)",
        )
        parser_genfeature_rmsd_mdtraj.add_argument(
            "-top",
            "--topology",
            type=str,
            required=True,
            help="topology file path for mdtraj topology",
        )
        parser_genfeature_rmsd_mdtraj.add_argument(
            "-od",
            "--outdir",
            type=str,
            default="rmsd-genfeature",
            help="output directory path [default: rmsd-genfeature]",
        )
        parser_genfeature_rmsd_mdtraj.add_argument(
            "-p",
            "--n_parallel",
            type=int,
            default=1,
            help="number of parallel [default: 1]",
        )
        parser_genfeature_rmsd_mdtraj.add_argument(
            "-ref",
            "--reference",
            type=str,
            required=True,
            help="reference structure file path for fitting",
        )
        parser_genfeature_rmsd_mdtraj.add_argument(
            "-ft",
            "--fit-trj",
            type=str,
            required=True,
            help="mdtraj selection for fitting in trajectory",
        )
        parser_genfeature_rmsd_mdtraj.add_argument(
            "-fr",
            "--fit-ref",
            type=str,
            required=True,
            help="mdtraj selection for fitting in reference",
        )
        parser_genfeature_rmsd_mdtraj.add_argument(
            "-ct",
            "--cal-trj",
            type=str,
            required=True,
            help="mdtraj selection for calculating in trajectory",
        )
        parser_genfeature_rmsd_mdtraj.add_argument(
            "-cr",
            "--cal-ref",
            type=str,
            required=True,
            help="mdtraj selection for calculating in reference",
        )

        # xyz
        parser_genfeature_xyz = parser_genfeature_sub.add_parser(
            "xyz", help="XYZ based feature"
        )
        parser_genfeature_xyz_sub = parser_genfeature_xyz.add_subparsers()

        # mdtraj
        parser_genfeature_xyz_mdtraj = parser_genfeature_xyz_sub.add_parser(
            "mdtraj", help="using mdtraj"
        )
        parser_genfeature_xyz_mdtraj.add_argument(
            "-t", "--trial", type=int, required=True, help="trial number without 0-fill"
        )
        parser_genfeature_xyz_mdtraj.add_argument(
            "-tf",
            "--trj-file",
            type=str,
            required=True,
            help="trajectory file name (e.g. prd.xtc prd_rmmol.trr)",
        )
        parser_genfeature_xyz_mdtraj.add_argument(
            "-top",
            "--topology",
            type=str,
            required=True,
            help="topoology file path for mdtraj",
        )
        parser_genfeature_xyz_mdtraj.add_argument(
            "-od",
            "--outdir",
            type=str,
            default="xyz-genfeature",
            help="output directory path [default: xyz-genfeature]",
        )
        parser_genfeature_xyz_mdtraj.add_argument(
            "-p",
            "--n_parallel",
            type=int,
            default=1,
            help="number of parallel [default: 1]",
        )
        parser_genfeature_xyz_mdtraj.add_argument(
            "-s",
            "--selection",
            type=str,
            required=True,
            help="mdtraj selection extracted in trajectory",
        )

        # comdist
        parser_genfeature_comdist = parser_genfeature_sub.add_parser(
            "comdist", help="COM distance(1D) based feature"
        )
        parser_genfeature_comdist_sub = parser_genfeature_comdist.add_subparsers()

        # mdtraj
        parser_genfeature_comdist_mdtraj = parser_genfeature_comdist_sub.add_parser(
            "mdtraj", help="usgin mdtraj"
        )
        parser_genfeature_comdist_mdtraj.add_argument(
            "-t", "--trial", type=int, required=True, help="trial number without 0-fill"
        )
        parser_genfeature_comdist_mdtraj.add_argument(
            "-tf",
            "--trj-file",
            type=str,
            required=True,
            help="trajectory file name (e.g. prd.xtc prd_rmmol.trr)",
        )
        parser_genfeature_comdist_mdtraj.add_argument(
            "-top",
            "--topology",
            type=str,
            required=True,
            help="topology file path for mdtraj",
        )
        parser_genfeature_comdist_mdtraj.add_argument(
            "-od",
            "--outdir",
            type=str,
            default="comdist-genfeature",
            help="output directory path [default: comdist-genfeature]",
        )
        parser_genfeature_comdist_mdtraj.add_argument(
            "-p",
            "--n_parallel",
            type=int,
            default=1,
            help="number of parallel [default: 1]",
        )
        parser_genfeature_comdist_mdtraj.add_argument(
            "-s1",
            "--selection1",
            type=str,
            required=True,
            help="mdtraj selection1 for calculating distance",
        )
        parser_genfeature_comdist_mdtraj.add_argument(
            "-s2",
            "--selection2",
            type=str,
            required=True,
            help="mdtraj selection2 for calculating distance",
        )

        args = parser.parse_args()

        # pacsmd -> error
        if len(sys.argv) == 1:
            LOGGER.error('Use "pacs -h" to view help messages')
            exit(1)

        # version
        if args.version is True:
            print("pacs", __version__)
            exit(0)

        # run, input file
        if sys.argv[1] == "mdrun":
            if args.file is None:
                LOGGER.error("please specify input file")
                exit(1)
            toml = self.read_input(args.file)
            toml["trial"] = args.trial
            try:
                conf = MDsettings(**toml)
            except Exception:
                conf = MDsettings.__new__(MDsettings)
                conf.__dict__.update(toml)

                def find_user_defined_variable(toml) -> str:
                    tmp = MDsettings()
                    user_defined_variable = []

                    for key, value in toml.items():
                        if not hasattr(tmp, key):
                            user_defined_variable.append(f"{key} = {value}")

                    return ", ".join(user_defined_variable)

                user_defined_variable = find_user_defined_variable(toml)
                LOGGER.warning(
                    f"User-defined variable was specified. {user_defined_variable}"
                )

            conf.check()
            LOGGER.info(f"{args.file} was read successfully")
            return conf

        if sys.argv[1] == "genrepresent":
            if len(sys.argv) == 2:
                LOGGER.error("Use -h")
                exit(1)
            dic = defaultdict()
            dic["trial"] = int(args.trial)
            dic["max_cycle"] = 1000
            dic["trajectory"] = args.trajectory
            dic["topology"] = args.topology
            dic["trajectory_extension"] = "." + args.trajectory.split(".")[-1]
            if sys.argv[2] == "mdtraj":
                dic["analyzer"] = "mdtraj"
            elif sys.argv[2] == "gmx":
                dic["analyzer"] = "gromacs"
                dic["cmd_gmx"] = args.cmd_gmx
            elif sys.argv[2] == "cpptraj":
                dic["analyzer"] = "cpptraj"
            conf = MDsettings.__new__(MDsettings)
            conf.__dict__.update(dic)
            self.check_version(f"./trial{args.trial:03}")
            genrepresent(conf)
            exit(0)

        if sys.argv[1] == "rmmol":
            if len(sys.argv) == 2:
                LOGGER.error("Use -h")
                exit(1)
            dic = defaultdict()
            dic["trial"] = int(args.trial)
            dic["max_cycle"] = 1000
            dic["trajectory_extension"] = args.trajectory_extension
            dic["keep_selection"] = args.keep_selection
            if sys.argv[2] == "mdtraj":
                dic["analyzer"] = "mdtraj"
                dic["top_mdtraj"] = Path(args.top_mdtraj).resolve()
            elif sys.argv[2] == "gmx":
                dic["analyzer"] = "gromacs"
                dic["cmd_gmx"] = args.cmd_gmx
                dic["index_file"] = args.index_file
                dic["nojump"] = args.nojump
            elif sys.argv[2] == "cpptraj":
                dic["analyzer"] = "cpptraj"
                dic["topology"] = args.topology
            conf = MDsettings(**dic)
            self.check_version(f"./trial{args.trial:03}")
            make_top(conf)
            rmmol_all(conf)
            rmmol_log_add_info(conf)
            exit(0)

        if sys.argv[1] == "rmfile":
            dic = defaultdict()
            dic["trial"] = int(args.trial)
            dic["simulator"] = args.simulator
            conf = MDsettings(**dic)
            self.check_version(f"./trial{args.trial:03}")
            rmfile_all(conf)
            exit(0)

        if sys.argv[1] == "fit":
            if len(sys.argv) == 2:
                LOGGER.error("Use -h")
                exit(1)
            if sys.argv[2] == "traj":
                if len(sys.argv) == 3:
                    LOGGER.error("Use -h")
                    exit(1)
                if sys.argv[3] == "mdtraj":
                    dic = defaultdict()
                    dic["analyzer"] = "mdtraj"
                    dic["top_mdtraj"] = args.topology
                    dic["reference"] = args.ref_structure
                    dic["selection1"] = args.trj_selection
                    dic["selection2"] = args.ref_selection
                    dic["n_parallel"] = int(args.n_parallel)
                    conf = MDsettings(**dic)
                    fit(conf, args.trj_file, args.out)
                    exit(0)
            if sys.argv[2] == "trial":
                if len(sys.argv) == 3:
                    LOGGER.error("Use -h")
                    exit(1)
                if sys.argv[3] == "mdtraj":
                    dic = defaultdict()
                    dic["analyzer"] = "mdtraj"
                    dic["trial"] = int(args.trial)
                    dic["top_mdtraj"] = args.topology
                    dic["reference"] = args.ref_structure
                    dic["selection1"] = args.trj_selection
                    dic["selection2"] = args.ref_selection
                    dic["n_parallel"] = int(args.n_parallel)
                    conf = MDsettings(**dic)
                    self.check_version(f"./trial{args.trial:03}")
                    fit_trial(conf, args.trj_file, args.out)
                    exit(0)

        if sys.argv[1] == "gencom":
            if len(sys.argv) == 2:
                LOGGER.error("use -h")
                exit(1)
            if sys.argv[2] == "traj":
                if len(sys.argv) == 3:
                    LOGGER.error("Use -h")
                    exit(1)
                if sys.argv[3] == "mdtraj":
                    dic = defaultdict()
                    dic["top_mdtraj"] = args.topology
                    dic["selection1"] = args.selection
                    dic["analyzer"] = "mdtraj"
                    conf = MDsettings(**dic)
                    gencom_traj(conf, args.trj_file, args.out_pdb, args.resid)
                    exit(0)
            if sys.argv[2] == "trial":
                if len(sys.argv) == 3:
                    LOGGER.error("Use -h")
                    exit(1)
                if sys.argv[3] == "mdtraj":
                    dic = defaultdict()
                    dic["top_mdtraj"] = args.topology
                    dic["selection1"] = args.selection
                    dic["analyzer"] = "mdtraj"
                    conf = MDsettings(**dic)
                    self.check_version(f"./trial{args.trial:03}")
                    gencom_trial(
                        conf,
                        args.trial,
                        args.trjfile_name,
                        args.out_pdb,
                        args.stride_frame,
                        args.resid,
                    )
                    exit(0)

        if sys.argv[1] == "genfeature":
            if len(sys.argv) == 2:
                LOGGER.error("Use -h")
                exit(1)
            self.check_version(f"./trial{args.trial:03}")
            if sys.argv[2] == "comvec":
                comvec.cal_feature_trial(
                    args.trial,
                    args.trj_file,
                    args.topology,
                    args.outdir,
                    args.n_parallel,
                    args.reference,
                    args.fit_trj,
                    args.fit_ref,
                    args.selection1,
                    args.selection2,
                )
            elif sys.argv[2] == "comdist":
                comdist.cal_feature_trial(
                    args.trial,
                    args.trj_file,
                    args.topology,
                    args.outdir,
                    args.n_parallel,
                    args.selection1,
                    args.selection2,
                )
            elif sys.argv[2] == "rmsd":
                rmsd.cal_feature_trial(
                    args.trial,
                    args.trj_file,
                    args.topology,
                    args.outdir,
                    args.n_parallel,
                    args.reference,
                    args.fit_trj,
                    args.fit_ref,
                    args.cal_trj,
                    args.cal_ref,
                )
            elif sys.argv[2] == "xyz":
                xyz.cal_feature_trial(
                    args.trial,
                    args.trj_file,
                    args.topology,
                    args.outdir,
                    args.n_parallel,
                    args.selection,
                )
            exit(0)

    def parse_line(self, line: str):
        pattern = re.compile(r"([^=]+)\s*=\s*(.+)")
        match = pattern.match(line)
        if match:
            return match.groups()
        else:
            LOGGER.error(f"{line} is not matched to toml format")
            return None

    def read_input(self, file: str) -> dict:
        with open(file, "rb") as f:
            toml_dict = tomli.load(f)
        return toml_dict
        # dic = defaultdict(str)
        # with open(file, "r") as f:
        #     for line in f.readlines():
        #         line = line.strip()
        #         if line.startswith("#"):
        #             continue
        #         if "=" not in line:
        #             continue
        #         result = self.parse_line(line)
        #         if result is None:
        #             continue
        #         if len(result) != 2:
        #             continue
        #         key, value = result[0].strip(), result[1].strip()
        #         key = key.replace('"', "").replace("'", "")
        #         value = value.replace('"', "").replace("'", "")
        #         if "#" in value:
        #             value = value.split("#")[0].strip()
        #         dic[key] = value
        # return dic

    def check_version(self, trial_dir: str):
        version_file = f"{trial_dir}/pacstk.version"
        if Path(version_file).exists():
            with open(version_file) as f:
                line = f.readline().strip()
                if __version__ != line:
                    LOGGER.error("PaCS-Toolkit version error")
                    LOGGER.error(
                        f"Version used in {self.settings.each_trial()} is {line},"
                    )
                    LOGGER.error(f"But you're using PaCS-Toolkit {__version__}")
                    exit(1)
        else:
            LOGGER.error(f"Version file: {version_file} is not found")
            exit(1)
