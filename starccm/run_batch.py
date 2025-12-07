#!/usr/bin/env python3.11
from __future__ import annotations

import argparse
import ast
import os
import pathlib
import tempfile
import tomllib
import typing

from dataclasses import dataclass

# prefixes for jvm property arguments
MIN_PREFIX = "min:"
MAX_PREFIX = "max:"
INCREMENT_PREFIX = "inc:"
UNITS_PREFIX = "units:"

BATCH_SCRIPT_TEMPLATE = """\
#!/bin/bash

module load starccm+

{starccm_command}
"""


@dataclass
class ParameterRange:
    parameter: str
    minimum: float
    maximum: float
    increment: float
    units: str

    @classmethod
    def from_name_dict(
        cls, name: str, properties: dict[str, typing.Union[float, str]]
    ) -> ParameterRange:
        if " " in name:
            raise BadParameterName(
                "design parameters with spaces in their name are not currently supported"
            )
        else:
            return cls(
                parameter=name,
                maximum=properties["maximum"],
                minimum=properties["minimum"],
                increment=properties["increment"],
                units=properties["units"],
            )

    def to_jvm_properties(self) -> list[str]:
        """Converts this range to arguments setting JVM system properties expected by the STAR-CCM+ macro."""
        minimum = jvm_property_argument(MIN_PREFIX + self.parameter, str(self.minimum))
        maximum = jvm_property_argument(MAX_PREFIX + self.parameter, str(self.maximum))
        increment = jvm_property_argument(
            INCREMENT_PREFIX + self.parameter, str(self.increment)
        )
        units = jvm_property_argument(UNITS_PREFIX + self.parameter, self.units)

        return [minimum, maximum, increment, units]


@dataclass
class SimulationConfig:
    starccm_path: pathlib.Path
    project: str
    design_study: str
    csv_filename: str
    console_output: str
    cpus: int
    gpus: int

    @classmethod
    def from_dict(
        cls, properties: dict[str, typing.Union[int, str]]
    ) -> SimulationConfig:
        starccm_version = properties["starccm-version"]

        return cls(
            starccm_path=starccm_version_to_path(starccm_version),
            project=properties["project"],
            design_study=properties["design-study"],
            csv_filename=properties["csv-filename"],
            console_output=properties["console-output"],
            cpus=properties["cpus"],
            gpus=properties.get("gpus", 0),
        )


SlurmFlags = dict[str, str]


@dataclass
class Config:
    sim_config: SimulationConfig
    slurm_flags: SlurmFlags
    param_ranges: list[ParameterRange]


class BadStarCCMVersion(Exception):
    pass


class ConfigNotFound(Exception):
    pass


class BadParameterName(Exception):
    pass


def main():
    config_path = get_config_path()
    config = parse_config(config_path)

    # assemble sbatch command and exec into it
    sbatch_command = build_sbatch_command(config)

    print("executing sbatch")
    os.execvp("sbatch", sbatch_command)


def get_config_path() -> pathlib.Path:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "config",
        help="the path to the simulation config",
    )

    raw_args = parser.parse_args()

    config_path = pathlib.Path(raw_args.config)

    if not config_path.exists():
        raise ConfigNotFound(f"configuration file not found at path {config_path}")
    else:
        return config_path


def parse_config(config_path: pathlib.Path) -> Config:
    with open(config_path, "rb") as config_file:
        config_dict = tomllib.load(config_file)

    sim_config = SimulationConfig.from_dict(config_dict["simulation"])
    ranges = [
        ParameterRange.from_name_dict(*item)
        for item in config_dict["parameter"].items()
    ]

    slurm_flags = config_dict["slurm"]

    # also add CPUs/GPUs to flags, if specified
    slurm_flags["cpus-per-task"] = str(sim_config.cpus)

    if sim_config.gpus:
        slurm_flags["gpus"] = str(sim_config.gpus)

    return Config(sim_config=sim_config, slurm_flags=slurm_flags, param_ranges=ranges)

    slurm_dict = config_contents["slurm"]
    slurm_args = [f"--{key}={value}" for key, value in slurm_dict.items()]


def build_sbatch_command(config: Config) -> list[str]:
    # sbatch setup
    command = ["sbatch"]
    command.extend(dict_to_options(config.slurm_flags))

    # output arguments
    out_prefix = config.sim_config.console_output
    command.extend(["--output", out_prefix + ".out"])
    command.extend(["--error", out_prefix + ".err"])

    # build starccm study run command
    starccm_command = build_starccm_command(config)

    # put starccm command in batch script & pass to sbatch
    script_path = write_batch_script(starccm_command)
    command.append(script_path)

    return command


def build_starccm_command(config: Config) -> list[str]:
    sim_config = config.sim_config

    # build initial batch command stem
    starccm_command = [
        str(sim_config.starccm_path),
        "-batch",
        "RunStudyWithParameters.java",
        sim_config.project,
    ]

    # specify cores & gpu use
    starccm_command.extend(["-np", str(sim_config.cpus)])

    if sim_config.gpus:
        starccm_command.extend(["-gpgpu", "auto"])

    # macro arguments via JVM system properties

    # output CSV file
    starccm_command.extend(jvm_property_argument("outFile", sim_config.csv_filename))

    # design study
    starccm_command.extend(jvm_property_argument("studyName", sim_config.design_study))

    # assemble list of design parameters, and also set the range system properties
    parameters = []
    range_args = []
    for range in config.param_ranges:
        parameters.append(range.parameter)

        for argpair in range.to_jvm_properties():
            range_args.extend(argpair)

    # tell the macro which study parameters it's modifying
    starccm_command.extend(
        jvm_property_argument("studyParameters", ",".join(parameters))
    )
    starccm_command.extend(range_args)

    return starccm_command


def write_batch_script(starccm_command: list[str]) -> str:
    # sbatch requires a shell script, so we create an executable temporary file with the contents we need
    fd, script_path = tempfile.mkstemp(prefix="scrt-sim", text=True)
    os.chmod(fd, 0o755)  # 0o755 -> rwxr-xr-x

    # quote any arguments that have spaces (e.g., due to parameter name having a space)
    quoted = [f'"{arg}"' if " " in arg else arg for arg in starccm_command]

    # write script from template to tempfile
    batch_contents = BATCH_SCRIPT_TEMPLATE.format(starccm_command=" ".join(quoted))
    os.write(fd, batch_contents.encode())

    return script_path


def starccm_version_to_path(version: str) -> pathlib.Path:
    base_path = pathlib.Path("/usr/local/apps/star-ccm+/")
    starccm_exes = base_path.glob(f"{version}*/STAR-CCM+*/star/bin/starccm+")

    try:
        return next(starccm_exes)
    except StopIteration as e:
        raise BadStarCCMVersion(f"STAR-CCM+ version not found: {version}") from e


def dict_to_options(options_dict: dict[str, str]) -> list[str]:
    return [f"--{key}={value}" for key, value in options_dict.items()]


def jvm_property_argument(name: str, value: str) -> str:
    return ["-jvmargs", f"-D{name}={value}"]


if __name__ == "__main__":
    main()
