#!/usr/bin/env python3.11
import argparse
import ast
import os
import pathlib
import re
import tomllib

from dataclasses import dataclass

# matches e.g. 12 or 0.34
DECIMAL_PATTERN = r"\d+(\.\d+)?"
RANGE_RE = re.compile(rf"(?P<name>\w+):(?P<range>\[{DECIMAL_PATTERN},\s*{DECIMAL_PATTERN}]):(?P<increment>{DECIMAL_PATTERN}):(?P<units>[a-z]+)")

# prefixes for jvm property arguments
MIN_PREFIX = "min:"
MAX_PREFIX = "max:"
INCREMENT_PREFIX = "inc:"
UNITS_PREFIX = "units:"

@dataclass
class Range:
    parameter: str
    minimum: float
    maximum: float
    increment: float
    units: str

    def to_jvm_properties(self):
        minimum = jvm_property_argument(MIN_PREFIX + self.parameter, str(self.minimum))
        maximum = jvm_property_argument(MAX_PREFIX + self.parameter, str(self.maximum))
        increment = jvm_property_argument(INCREMENT_PREFIX + self.parameter, str(self.increment))
        units = jvm_property_argument(UNITS_PREFIX + self.parameter, self.units)

        return [minimum, maximum, increment, units]


@dataclass
class Config:
    starccm_path: str
    project: str
    outfile: str
    ranges: [Range]
    slurm_arguments: [str]
    run: bool


class BadStarCCMVersion(Exception):
    pass


class BadRange(Exception):
    pass


class ConfigNotFound(Exception):
    pass


def main():
    config = parse_config()

    # sbatch setup
    command = ["sbatch"]
    command.extend(config.slurm_arguments)

    # bring in starccm
    command.extend([str(config.starccm_path), "-batch", "RunStudyWithParameters.java", config.project])

    parameters = []
    range_args = []
    for range in config.ranges:
        parameters.append(range.parameter)
        range_args.extend(range.to_jvm_properties())

    command.append(jvm_property_argument("studyParameters", ",".join(parameters)))
    command.extend(range_args)

    if config.run:
        print("executing via slurm:")
        print(" ".join(command))
        os.execl(command)
    else:
        print("simulation command:")
        print(" ".join(command))

def parse_config() -> Config:
    parser = argparse.ArgumentParser()

    parser.add_argument("-c", "--config", default="simulation.toml", help="the path to the simulation config (defualt %(default)s)")
    parser.add_argument("--print-command", action="store_true", help="whether to just print the command and exit")

    # TODO: just move to config file? probably better ux
    parser.add_argument("range", action="extend", nargs="+", help="the parameter range to set in format name:[min,max]:increment:unit (e.g., AoA:[0,10]:1:deg)")

    raw_args = parser.parse_args()

    config_file = pathlib.Path(raw_args.config)

    if not config_file.exists:
        raise ConfigNotFound("configuration file not found:" + config_file)

    with open(config_file, "rb") as f:
        config_contents = tomllib.load(f)

    sim_config = config_contents["simulation"]

    starccm_path = starccm_version_to_path(sim_config["starccm-version"])
    outfile = sim_config["output-filename"]
    project = sim_config["project"]

    ranges = []
    for range in raw_args.range:
        ranges.append(parse_range(range))

    slurm_args = [f"--{key}={value}" for key, value in config_contents["slurm"].items()]

    return Config(
        starccm_path=starccm_path,
        project=project,
        outfile=outfile,
        ranges=ranges,
        run=not raw_args.print_command,
        slurm_arguments=slurm_args
    )

def starccm_version_to_path(version: str) -> str:
    base_path = pathlib.Path("/usr/local/apps/star-ccm+/")    
    starccm_exes = base_path.glob(f"{version}*/STAR-CCM+*/star/bin/starccm+")

    try:
        return next(starccm_exes)
    except StopIteration as e:
        raise BadStarCCMVersion(f"STAR-CCM+ version not found: {version}") from e


def parse_range(range_str: str):
    matches = RANGE_RE.match(range_str)

    if not matches:
        raise BadRange(f"invalid range string: `{range_str}`")

    name = matches.group("name")
    increment = float(matches.group("increment"))
    range_min, range_max = ast.literal_eval(matches.group("range"))
    units = matches.group("units")

    return Range(
        parameter=name,
        minimum=range_min,
        maximum=range_max,
        increment=increment,
        units=units
    )

def jvm_property_argument(name: str, value: str) -> str:
    return f"-jvmargs -D{name}={value}"

if __name__ == "__main__":
    main()
