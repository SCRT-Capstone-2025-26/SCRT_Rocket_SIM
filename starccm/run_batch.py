#!/usr/bin/env python3.11
from __future__ import annotations

import argparse
import dataclasses
import math
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

    @property
    def num_values(self) -> int:
        """The number of parameter values contained in this range"""
        return (self.maximum - self.minimum) // self.increment

    def split(self, parts: int) -> list[ParameterRange]:
        """Splits this range into `parts` smaller ranges of similar size"""

        # ceil is used to allow the last part to have fewer values (rather than creating one more part than desired)
        values_per_part = math.ceil(self.num_values / parts)

        part_min = self.minimum

        parts = []
        for _ in range(parts):
            # ensure maximum in each part is at most
            part_max = min(
                self.maximum, part_min + (values_per_part - 1) * self.increment
            )

            # create a copy of this range with the updated minimum and maximum
            part = dataclasses.replace(self, minimum=part_min, maximum=part_max)
            parts.append(part)

            # set the next part minimum past the end of this range (again clamped to overarching maximum)
            part_min = min(self.maximum, part_max + self.increment)

        return parts

    def to_jvm_properties(self) -> list[str]:
        """Converts this range to arguments setting JVM system properties expected by the STAR-CCM+ macro."""
        minimum = jvm_property_argument(MIN_PREFIX + self.parameter, str(self.minimum))
        maximum = jvm_property_argument(MAX_PREFIX + self.parameter, str(self.maximum))
        increment = jvm_property_argument(
            INCREMENT_PREFIX + self.parameter, str(self.increment)
        )
        units = jvm_property_argument(UNITS_PREFIX + self.parameter, self.units)

        return [minimum, maximum, increment, units]

    def __repr__(self):
        return f"ParameterRange {self.parameter} ({self.units}) on range [{self.minimum}, {self.maximum}] with increment {self.increment}"


@dataclass
class SimulationConfig:
    starccm_path: pathlib.Path
    project: str
    design_study: str
    csv_filename: str
    console_output: str
    cpus: int
    gpus: int
    split_into: typing.Optional[int]

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
            split_into=properties.get("split_into", 1),
        )


SlurmFlags = dict[str, str]


@dataclass
class Config:
    sim_config: SimulationConfig
    slurm_flags: SlurmFlags
    param_ranges: list[ParameterRange]

    def split_jobs(self) -> list[Config]:
        if (num_jobs := self.sim_config.split_into) <= 1:
            return [self]
        else:
            # get largest parameter range by number of values to split on
            ranges_sorted_asc = sorted(self.param_ranges, key=ParameterRange.num_values)
            remaining, largest_range = ranges_sorted_asc[:-1], ranges_sorted_asc[-1]

            subranges = largest_range.split(num_jobs)

            new_configs = []
            for i, subrange in enumerate(subranges):
                i_suffix = f"_{i}"

                # update filenames to avoid clobbering previous output
                updated_simconfig = dataclasses.replace(
                    self.sim_config,
                    console_output=self.sim_config.console_output + i_suffix,
                    # TODO: place before csv rather than at very end
                    csv_filename=self.sim_config.csv_filename + i_suffix,
                )

                config = dataclasses.replace(
                    self,
                    param_ranges=remaining + [subrange],
                    sim_config=updated_simconfig,
                )
                new_configs.append(config)

            return new_configs


class BadStarCCMVersion(Exception):
    pass


class ConfigNotFound(Exception):
    pass


class BadParameterName(Exception):
    pass


def main():
    config_path = get_config_path()
    config = parse_config(config_path)

    for job_config in config.split_jobs():
        # TODO: print param range reprs for disambugation

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
    # TODO: include date/shard in filename to avoid clobbering old output
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
