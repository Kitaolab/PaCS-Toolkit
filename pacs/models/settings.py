import dataclasses
import re
import subprocess
import tempfile
from pathlib import Path

from pacs.utils.logger import generate_logger

LOGGER = generate_logger(__name__)


@dataclasses.dataclass
class MDsettings:

    """
    settings for MD simulation

    Attributes:
        trial (int): id of trial
        max_cycle (int): maximum number of cycles
        n_replica (int): number of replicas
        n_parallel (int): number of replicas which are calculated at same time
        centering (bool): whether to center the structure or not in export
        centering_selection (str): selection for centering
        working_dir (Path): working directory
        simulator (str): simulator for MD simulation(gromacs, namd, amber)
        structure (Path): structure file
        topology (Path): topology file
        mdconf (Path): parameter file
        index_file (Path): index file
        trajectory_extension (str): extension of trajectory file
        cmd_mpi (str): command for mpi
        cmd_parallel (str): command for parallel simulation
        cmd_serial (str): command for serial simulation
        analyzer (str): tool for analysis
        type (str): evaluation type
        threshold (float): threshold for evaluation type
        skip_frame (int): number of frames to skip
        reference (Path): reference file
        selection1 (str): selection for evaluation type
        selection2 (str): selection for evaluation type
        selection3 (str): selection for evaluation type
        selection4 (str): selection for evaluation type
        pbc_level (int): level of PBC treatment before CV calculation
            1: no PBC treatment (fastest, risky)
            2: gromacs: trjconv -pbc mol / cpptraj: image
               mdtraj: same as -pbc mol (medium, risky)
            3: gromacs: trjconv -center, then -pbc atom, then -pbc mol
               cpptraj: center <centering atom>, then image
               mdtraj: same as gromacs (slowest, safest)
        centering_atom_for_PBC (int or str): the single atom centered in the box
            when pbc_level = 3. int: atom number (1-based).
            str: index group name (gromacs), atom mask (cpptraj)
            or selection (mdtraj).
            It must select exactly one atom.
    """

    # basic
    trial: int = 1
    max_cycle: int = 1
    n_replica: int = 1
    n_parallel: int = 1
    centering: bool = True
    centering_selection: str = None
    working_dir: Path = Path("./.")

    # simulator
    simulator: str = None
    structure: Path = None
    topology: Path = None
    mdconf: Path = None
    index_file: Path = None
    trajectory_extension: str = None
    cmd_mpi: str = ""
    cmd_parallel: str = None
    cmd_serial: str = None

    # analyzer
    analyzer: str = "mdtraj"
    type: str = None
    threshold: float = None
    skip_frame: int = 1
    reference: Path = None
    selection1: str = None
    selection2: str = None
    selection3: str = None
    selection4: str = None

    # hidden option
    cmd_gmx: str = None
    top_mdtraj: str = None
    structure_extension: str = None

    # genrepresent option
    # genrepresent: bool = False

    # rmmol option
    rmmol: bool = False
    keep_selection: str = None

    # rmfile option
    rmfile: bool = False

    # PBC treatment option for gromacs analyzer
    pbc_level: int = 2
    centering_atom_for_PBC: int = None

    def each_replica(
        self, _trial: int = None, _cycle: int = None, _replica: int = None
    ) -> str:
        if _trial is None:
            _trial = self.trial
        if _cycle is None:
            _cycle = self.max_cycle
        if _replica is None:
            _replica = self.n_replica
        return (
            f"{self.working_dir}/trial{_trial:03}/cycle{_cycle:03}/replica{_replica:03}"
        )

    def each_cycle(self, _trial: int = None, _cycle: int = None) -> str:
        if _trial is None:
            _trial = self.trial
        if _cycle is None:
            _cycle = self.cycle
        return f"{self.working_dir}/trial{_trial:03}/cycle{_cycle:03}"

    def each_trial(self, _trial: int = None) -> str:
        if _trial is None:
            _trial = self.trial
        return f"{self.working_dir}/trial{_trial:03}"

    def log_file(self) -> str:
        return f"{self.working_dir}/trial{self.trial:03}.log"

    def rmmol_top(self) -> None:
        c0r1_dir = self.each_replica(_cycle=0, _replica=1)
        self.top_mdtraj = f"{c0r1_dir}/rmmol_top.pdb"

    def check_bool(self, value: str) -> bool:
        if isinstance(value, str):
            flag = value.lower()
            return flag in ["true", "1"]
        else:
            return value

    def update(self):
        if self.selection3 is None:
            self.selection3 = self.selection1
        if self.selection4 is None:
            self.selection4 = self.selection2
        if self.cmd_parallel is None:
            if self.n_parallel > 1:
                LOGGER.warning(
                    ".".join(
                        [
                            "n_parallel is greater than 1",
                            "but cmd_parallel is not set.",
                            "Use cmd_serial instead.",
                        ]
                    )
                )
            self.cmd_parallel = self.cmd_serial

    # def __post_init__(self) -> None:
    def check(self) -> None:
        # int
        self.trial = int(self.trial)
        self.max_cycle = int(self.max_cycle)
        self.n_replica = int(self.n_replica)
        self.n_parallel = int(self.n_parallel)
        self.skip_frame = int(self.skip_frame)
        if self.threshold is not None:
            self.threshold = float(self.threshold)
        if self.trial < 0 or self.trial > 999:
            LOGGER.error(f"trial number {self.trial} is out of range 1..999")
            exit(1)
        if self.max_cycle < 0 or self.max_cycle > 999:
            LOGGER.error(f"cycle number {self.max_cycle} is out of range 1..999")
            exit(1)
        if self.n_replica < 0 or self.n_replica > 999:
            LOGGER.error(f"n_replica number {self.replica} is out of range 1..999")
            exit(1)
        if self.n_parallel < 0 or self.n_parallel > 999:
            LOGGER.error(f"n_parallel number {self.replica} is out of range 1..999")
            exit(1)

        # bool
        self.centering = self.check_bool(self.centering)
        self.rmmol = self.check_bool(self.rmmol)
        # self.genrepresent = self.check_bool(self.genrepresent)
        self.rmfile = self.check_bool(self.rmfile)

        # lower
        if self.type is None:
            LOGGER.error("type is None")
            exit(1)
        if self.simulator is None:
            LOGGER.error("simulator is None")
            exit(1)
        self.simulator = self.simulator.lower()
        self.type = self.type.lower()
        self.analyzer = self.analyzer.lower()

        # simulator
        if self.simulator not in ["gromacs", "namd", "amber"]:
            LOGGER.error(f"{self.simulator} is not supported")
            exit(1)

        # analyzer
        if self.analyzer not in ["mdtraj", "gromacs", "cpptraj"]:
            LOGGER.error(f"{self.analyzer} is not supported")
            exit(1)

        if self.type not in [
            "target",
            "association",
            "dissociation",
            "rmsd",
            "ee",
            "a_d",
            "template",
        ]:
            LOGGER.error(f"{self.type} is not supported")
            exit(1)

        # nojump (removed): replaced by pbc_level and centering_atom_for_PBC
        if "nojump" in self.__dict__:
            LOGGER.error(
                '"nojump" option was removed. Please delete it from the input file '
                "and use the new PBC options instead (valid for gromacs analyzer):\n"
                "  pbc_level = 1  # no PBC treatment (fastest, risky)\n"
                "  pbc_level = 2  # trjconv -pbc mol, default (medium, risky)\n"
                "  pbc_level = 3  # -center -> -pbc atom -> -pbc mol (slowest, safest)\n"
                "  centering_atom_for_PBC = <atom number>  # required for pbc_level = 3"
            )
            exit(1)

        # PBC treatment level
        try:
            self.pbc_level = int(self.pbc_level)
        except (TypeError, ValueError):
            LOGGER.error(f"pbc_level must be 1, 2 or 3 (got {self.pbc_level})")
            exit(1)
        if self.pbc_level not in [1, 2, 3]:
            LOGGER.error(f"pbc_level must be 1, 2 or 3 (got {self.pbc_level})")
            exit(1)
        if self.pbc_level == 3:
            atom = self.centering_atom_for_PBC
            if atom is None or (isinstance(atom, str) and atom.strip() == ""):
                LOGGER.error("centering_atom_for_PBC is required when pbc_level = 3")
                exit(1)
            if isinstance(atom, bool) or not isinstance(atom, (int, str)):
                LOGGER.error(
                    "centering_atom_for_PBC must be an atom number or a selection "
                    f"string (got {atom!r})"
                )
                exit(1)
            # "123" is treated as atom number 123
            if isinstance(atom, str) and atom.strip().isdigit():
                atom = int(atom.strip())
            if isinstance(atom, int) and atom < 1:
                LOGGER.error("centering_atom_for_PBC must be >= 1 (1-based)")
                exit(1)
            self.centering_atom_for_PBC = atom

        # change centering_selection to match analyzer
        if self.analyzer == "mdtraj" and self.centering_selection is None:
            self.centering_selection = "protein"
        if self.analyzer == "cpptraj" and self.centering_selection is None:
            self.centering_selection = "@CA,C,O,N,H"
        if self.analyzer == "gromacs" and self.centering_selection is None:
            self.centering_selection = "Protein"

        # threshold check
        if self.threshold is None and self.type in [
            "target",
            "association",
            "dissociation",
            "rmsd",
        ]:
            LOGGER.error(f"{self.type} requires threshold")
            exit(1)

        if self.simulator != "gromacs" and self.analyzer == "gromacs":
            LOGGER.error("simulator must be gromacs if analyzer is gromacs")
            exit(1)

        # cmd_parallel
        if self.cmd_serial is None:
            LOGGER.error("cmd_serial must be specified")
            exit(1)

        # mpi parallel check
        if self.n_parallel > 1 and self.cmd_mpi == "":
            LOGGER.warning(
                "multiprocessing is used for parallel simulation. \
                        It could be inefficient however. \
                        Therefore, it is recommended to set n_parallel to 1 or cmd_mpi."
            )

        # Check if indexfile is set when gromacs
        if self.simulator == "gromacs" and self.index_file is None:
            LOGGER.error("index file is required for gromacs")
            exit(1)

        if self.type in ["target", "rmsd"] and self.reference is None:
            LOGGER.error(f"reference is required for {self.type}")
            exit(1)

        # Whether the required seletion is set in the analyzer
        if self.type == "dissociation":
            if self.selection1 is None:
                LOGGER.error("selection1 is required for dissociation")
                exit(1)
            if self.selection2 is None:
                LOGGER.error("selection2 is required for dissociation")
                exit(1)

        self.update()

        if self.topology is None:
            LOGGER.error("topology is None")
            exit(1)
        if self.structure is None:
            LOGGER.error("structure is None")
            exit(1)
        if self.mdconf is None:
            LOGGER.error("mdconf is None")
            exit(1)
        if self.trajectory_extension is None:
            LOGGER.error("trajectory_extension is None")
            exit(1)
        self.structure = Path(self.structure)
        self.topology = Path(self.topology)
        self.mdconf = Path(self.mdconf)
        self.working_dir = Path(self.working_dir)
        if self.simulator == "gromacs":
            self.index_file = Path(self.index_file)

        # analyzer
        if self.type in ["target", "rmsd"]:
            self.reference = Path(self.reference)

        # relative path to absolute path
        """
        self.structure = Path(self.structure).resolve()
        self.topology = Path(self.topology).resolve()
        self.mdconf = Path(self.mdconf).resolve()
        self.working_dir = Path(self.working_dir).resolve()
        if self.simulator == "gromacs":
            self.index_file = Path(self.index_file).resolve()

        # analyzer
        if self.type in ["target", "rmsd"]:
            self.reference = Path(self.reference).resolve()
        """

        # gmx command
        if self.simulator == "gromacs" and self.cmd_gmx is None:
            self.cmd_gmx = re.findall(r"\S+", self.cmd_serial)[0]

        # rmmol
        if self.rmmol and self.keep_selection is None:
            LOGGER.error("keep_selection is necessary if rmmol is True")
            exit(1)

        # top_mdtraj
        top_extension = [
            ".pdb",
            ".pdb.gz",
            ".h5",
            ".lh5",
            ".prmtop",
            ".parm7",
            ".prm7",
            ".psf",
            ".mol2",
            ".hoomdxml",
            ".gro",
            ".arc",
            ".hdf5",
            ".gsd",
        ]
        # Retrieve the topology file from the input
        top_mdtraj = next(
            (
                v
                for v in vars(self).values()
                if hasattr(v, "as_posix") and v.suffix in top_extension
            ),
            None,
        )
        if top_mdtraj is not None:
            self.top_mdtraj = top_mdtraj
        else:
            LOGGER.error("a topology file required to read the trajectory is missing.")
            exit(1)

        # structure_extension
        init_structure_extension = [
            ".xtc",
            ".trr",
            ".pdb",
            ".pdb.gz",
            ".dcd",
            ".h5",
            ".binpos",
            ".nc",
            ".netcdf",
            ".ncrst",
            ".crd",
            ".mdcrd",
            ".ncdf",
            ".lh5",
            ".lammpstrj",
            ".xyz",
            ".xyz.gz",
            ".gro",
            ".rst7",
            ".tng",
            ".dtr",
            ".gsd",
        ]
        tmp = self.structure.suffix
        if tmp in init_structure_extension:
            self.structure_extension = tmp
        else:
            LOGGER.error("cannot start PaCSMD with this STRUCTURE.")
            exit(1)

        # centering_atom_for_PBC must select exactly one atom
        if self.pbc_level == 3:
            self.check_centering_atom_for_PBC()

    def centering_mask_cpptraj(self) -> str:
        # atom number -> cpptraj atom mask, a string is used as a mask as it is
        if isinstance(self.centering_atom_for_PBC, int):
            return f"@{self.centering_atom_for_PBC}"
        return self.centering_atom_for_PBC

    def centering_atom_index_mdtraj(self, topology) -> int:
        # atom number (1-based) or mdtraj selection -> 0-based atom index
        if isinstance(self.centering_atom_for_PBC, int):
            return self.centering_atom_for_PBC - 1
        return int(topology.select(self.centering_atom_for_PBC)[0])

    def check_centering_atom_for_PBC(self) -> None:
        atom = self.centering_atom_for_PBC
        if self.analyzer == "gromacs":
            if isinstance(atom, int):
                return  # an atom number is always exactly one atom
            n_atoms = self.count_atoms_in_ndx_group(atom)
            where = f'index group "{atom}" in {self.index_file}'
        elif self.analyzer == "mdtraj":
            import mdtraj as md

            top = md.load_topology(str(self.top_mdtraj))
            if isinstance(atom, int):
                if atom > top.n_atoms:
                    LOGGER.error(
                        f"centering_atom_for_PBC = {atom} is larger than the number "
                        f"of atoms ({top.n_atoms}) in {self.top_mdtraj}"
                    )
                    exit(1)
                n_atoms = 1
                where = f"atom number {atom} in {self.top_mdtraj}"
            else:
                try:
                    n_atoms = len(top.select(atom))
                except Exception as e:
                    LOGGER.error(f'invalid mdtraj selection "{atom}": {e}')
                    exit(1)
                where = f'mdtraj selection "{atom}" in {self.top_mdtraj}'
        else:
            n_atoms = self.count_atoms_in_cpptraj_mask(self.centering_mask_cpptraj())
            where = f'cpptraj mask "{self.centering_mask_cpptraj()}"'

        if n_atoms != 1:
            LOGGER.error(
                f"centering_atom_for_PBC must select exactly 1 atom, "
                f"but {where} selects {n_atoms} atoms. "
                "Please specify a single atom."
            )
            exit(1)
        LOGGER.info(f"centering_atom_for_PBC: {where} selects 1 atom")

    def count_atoms_in_ndx_group(self, group: str) -> int:
        groups = {}
        current = None
        with open(self.index_file, "r") as f:
            for line in f:
                line = line.strip()
                header = re.match(r"^\[\s*(.+?)\s*\]$", line)
                if header:
                    current = header.group(1)
                    # gromacs uses the first group when names are duplicated
                    if current in groups:
                        current = None
                    else:
                        groups[current] = 0
                elif current is not None and line:
                    groups[current] += len(line.split())
        if group not in groups:
            LOGGER.error(f'index group "{group}" was not found in {self.index_file}')
            exit(1)
        return groups[group]

    def count_atoms_in_cpptraj_mask(self, mask: str) -> int:
        # strip everything except the mask from the initial structure and
        # count the atoms left in the output pdb
        with tempfile.TemporaryDirectory() as tmp_dir:
            cmd_cpptraj = [
                f"parm {Path(self.topology).resolve()}",
                f"trajin {Path(self.structure).resolve()} 1 1",
                f"strip !({mask})",
                f"trajout {tmp_dir}/selected.pdb",
                "run",
                "quit",
            ]
            with open(f"{tmp_dir}/count.cpptraj", "w") as f:
                f.write("\n".join(cmd_cpptraj))
            res = subprocess.run(
                f"cpptraj -i {tmp_dir}/count.cpptraj",
                shell=True,
                capture_output=True,
                text=True,
            )
            pdb = Path(f"{tmp_dir}/selected.pdb")
            if res.returncode != 0 or not pdb.exists():
                LOGGER.error(
                    f'cpptraj could not select centering_atom_for_PBC "{mask}"\n'
                    + res.stdout[-2000:]
                    + res.stderr[-2000:]
                )
                exit(1)
            with open(pdb, "r") as f:
                return sum(1 for line in f if line.startswith(("ATOM", "HETATM")))


class Snapshot:

    """
    information about a snapshot of a trajectory

    Attributes:
        replica (int): id of replica
        frame (int): id of frame
        cv (float or List[float]): value of collective variable
    """

    def __init__(self, replica: int, frame: int, cv: float):
        self.replica = replica
        self.frame = frame
        self.cv = cv

    def __str__(self):
        return f"replica {self.replica} frame {self.frame} cv {self.cv}"

    def __eq__(self, other) -> bool:
        return self.cv == other.cv

    def __lt__(self, other) -> bool:
        return self.cv < other.cv
