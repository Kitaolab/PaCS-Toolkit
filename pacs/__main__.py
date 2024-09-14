from typing import Tuple

from ._version import __version__
from .mdrun.analyzer.a_d import A_D
from .mdrun.analyzer.association import Association
from .mdrun.analyzer.dissociation import Dissociation
from .mdrun.analyzer.ee import EdgeExpansion
from .mdrun.analyzer.rmsd import RMSD
from .mdrun.analyzer.superAnalyzer import SuperAnalyzer
from .mdrun.analyzer.target import Target
from .mdrun.analyzer.template import Template
from .mdrun.Cycle import Cycle
from .mdrun.exporter.amber import eAmber
from .mdrun.exporter.gromacs import eGromacs
from .mdrun.exporter.namd import eNamd
from .mdrun.exporter.superExporter import SuperExporter
from .mdrun.simulator.amber import AMBER
from .mdrun.simulator.gromacs import GROMACS
from .mdrun.simulator.namd import NAMD
from .mdrun.simulator.superSimulator import SuperSimulator
from .models.settings import MDsettings
from .utils.logger import generate_logger
from .utils.parser import Parser

parser = Parser()
settings = parser.parse()

LOGGER = generate_logger(__name__)

LOGGER.info(f"PaCS-Toolkit Version: {__version__}")


def prepare_md(
    settings: MDsettings,
) -> Tuple[SuperSimulator, SuperAnalyzer, SuperExporter]:
    simulator: SuperSimulator = {
        "namd": NAMD(),
        "gromacs": GROMACS(),
        "amber": AMBER(),
    }.get(settings.simulator)

    analyzer: SuperAnalyzer = {
        "target": Target(),
        "dissociation": Dissociation(),
        "association": Association(),
        "rmsd": RMSD(),
        "ee": EdgeExpansion(),
        "a_d": A_D(),
        "template": Template(),
    }.get(settings.type)

    exporter: SuperExporter = {
        "namd": eNamd(),
        "gromacs": eGromacs(),
        "amber": eAmber(),
    }.get(settings.simulator)

    LOGGER.info(f"{settings}")

    return (simulator, analyzer, exporter)


def pacs_md(
    settings: MDsettings,
    simulator: SuperSimulator,
    analyzer: SuperAnalyzer,
    exporter: SuperExporter,
) -> None:
    cycle = Cycle(0, settings, simulator, analyzer, exporter)
    for cycle_cnt in range(settings.max_cycle + 1):
        cycle.cycle = cycle_cnt
        LOGGER.info(f"cycle{cycle_cnt:03} starts")
        cycle.run()
        LOGGER.info(f"cycle{cycle_cnt:03} done")
        if cycle.is_finished():
            if cycle_cnt == settings.max_cycle:
                LOGGER.info("max cycle reached!")
            else:
                LOGGER.info("cv reached threshold!")
            break


def main():
    LOGGER.info("PaCS-MD starts")
    (simulator, analyzer, exporter) = prepare_md(settings)
    pacs_md(settings, simulator, analyzer, exporter)
    LOGGER.info("PaCS-MD done")


if __name__ == "__main__":
    main()
