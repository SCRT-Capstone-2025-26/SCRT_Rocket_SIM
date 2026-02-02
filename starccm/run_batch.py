#!/usr/bin/env python3.11
from __future__ import annotations

import argparse
import pathlib
import shlex
import subprocess
import tomllib
import typing


from dataclasses import dataclass

# prefixes for jvm property arguments
MIN_PREFIX = "min:"
MAX_PREFIX = "max:"
INCREMENT_PREFIX = "inc:"
CONSTANT_PREFIX = "const:"
UNITS_PREFIX = "units:"

BATCH_SCRIPT_TEMPLATE = """\
#!/bin/bash

module load starccm+

{starccm_command}
"""


ParameterDict = dict[str, typing.Union[float, str]]


@dataclass
class ContinuousParameter:
    name: str
    minimum: float
    maximum: float
    increment: float
    units: str

    KEYS = frozenset({"minimum", "maximum", "increment"})

    @classmethod
    def from_name_dict(
        cls, name: str, properties: ParameterDict
    ) -> ContinuousParameter:
        if " " in name:
            raise BadParameterName(
                "design parameters with spaces in their name are not currently supported"
            )
        else:
            return cls(
                name=name,
                maximum=properties["maximum"],
                minimum=properties["minimum"],
                increment=properties["increment"],
                units=properties.get("units", ""),
            )

    def to_jvm_properties(self) -> list[str]:
        """Converts this parameter to arguments setting JVM system properties expected by the STAR-CCM+ macro."""
        minimum = jvm_property_argument(MIN_PREFIX + self.name, str(self.minimum))
        maximum = jvm_property_argument(MAX_PREFIX + self.name, str(self.maximum))
        increment = jvm_property_argument(
            INCREMENT_PREFIX + self.name, str(self.increment)
        )

        properties = [minimum, maximum, increment]

        if self.units:
            units = jvm_property_argument(UNITS_PREFIX + self.name, self.units)
            properties.append(units)

        return properties


@dataclass
class ConstantParameter:
    name: str
    value: float
    units: str

    KEYS = frozenset({"value"})

    @classmethod
    def from_name_dict(cls, name: str, properties: ParameterDict):
        if " " in name:
            raise BadParameterName(
                "design parameters with spaces in their name are not currently supported"
            )
        else:
            return cls(
                name=name,
                value=properties["value"],
                units=properties.get("units", ""),
            )

    def to_jvm_properties(self) -> list[str]:
        """Converts this parameter to arguments setting JVM system properties expected by the STAR-CCM+ macro."""
        value = jvm_property_argument(CONSTANT_PREFIX + self.name, self.value)

        if self.units:
            units = jvm_property_argument(UNITS_PREFIX + self.name, self.units)
            return [value, units]
        else:
            return [units]


Parameter = typing.Union[ContinuousParameter, ConstantParameter]


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
    parameters: list[Parameter]


class BadStarCCMVersion(Exception):
    pass


class ConfigNotFound(Exception):
    pass


class BadParameterName(Exception):
    pass


class BadParameter(Exception):
    pass


def main():
    config_path = get_config_path()
    config = parse_config(config_path)

    # assemble sbatch command and exec into it
    sbatch_command = build_sbatch_command(config)
    starccm_command = build_starccm_command(config)
    batch_script = make_batch_script(starccm_command)

    print("executing sbatch")
    completed_process = subprocess.run(
        sbatch_command, input=batch_script, text=True, capture_output=True
    )

    print("sbatch output:")
    print(completed_process.stdout)

    # print stderr on non-success exit code
    if completed_process.returncode:
        print("sbatch error output:")
        print(completed_process.stderr)


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
    parameters = [parse_parameter(*item) for item in config_dict["parameter"].items()]

    slurm_flags = config_dict["slurm"]

    # also add CPUs/GPUs to flags, if specified
    slurm_flags["cpus-per-task"] = str(sim_config.cpus)

    if sim_config.gpus:
        slurm_flags["gpus"] = str(sim_config.gpus)

    return Config(sim_config=sim_config, slurm_flags=slurm_flags, parameters=parameters)


def parse_parameter(name: str, config_dict: dict) -> Parameter:
    # remove units from check since it's optional
    keys = frozenset(config_dict.keys()) - {"units"}

    if keys == ContinuousParameter.KEYS:
        return ContinuousParameter.from_name_dict(name, config_dict)
    elif keys == ConstantParameter.KEYS:
        return ConstantParameter.from_name_dict(name, config_dict)
    else:
        raise BadParameter(
            f"invalid values set for parameter {name}; please double check your configuration"
        )


def build_sbatch_command(config: Config) -> list[str]:
    # sbatch setup
    command = ["sbatch"]
    command.extend(dict_to_options(config.slurm_flags))

    # output arguments
    out_prefix = config.sim_config.console_output
    command.extend(["--output", out_prefix + ".out"])
    command.extend(["--error", out_prefix + ".err"])

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

    # assemble list of constant/continuous design parameters, and also set the proper system properties
    continuous = []
    constant = []
    parameter_args = []
    for parameter in config.parameters:
        if isinstance(parameter, ContinuousParameter):
            continuous.append(parameter.name)
        elif isinstance(parameter, ConstantParameter):
            constant.append(parameter.name)

        for argpair in parameter.to_jvm_properties():
            parameter_args.extend(argpair)

    # tell the macro which study parameters it's modifying
    starccm_command.extend(
        jvm_property_argument("continuousParameters", ",".join(continuous))
    )
    starccm_command.extend(
        jvm_property_argument("constantParameters", ",".join(constant))
    )
    starccm_command.extend(parameter_args)

    return starccm_command


def make_batch_script(starccm_command: list[str]) -> str:
    # shlex.join quotes arguments in case they contain e.g. spaces
    quoted_command = shlex.join(starccm_command)

    return BATCH_SCRIPT_TEMPLATE.format(starccm_command=quoted_command)


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
