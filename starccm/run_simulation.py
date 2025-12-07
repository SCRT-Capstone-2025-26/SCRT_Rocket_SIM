#!/usr/bin/env python3.11
import argparse
import ast
import os
import pathlib
import re
import tempfile
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

BATCH_SCRIPT_TEMPLATE = """\
#!/bin/bash

module load starccm+

{starccm_command}
"""

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
    csvfile: str
    design_study: str
    ranges: [Range]
    slurm_arguments: [str]
    cores: int
    gpu: bool
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

    # output arguments
    command.extend(["-o", config.outfile + ".out"])
    command.extend(["-e", config.outfile + ".err"])

    # bring in starccm
    starccm_command = [str(config.starccm_path), "-batch", "RunStudyWithParameters.java", config.project]

    # specify cores & gpu use
    starccm_command.extend(["-np", str(config.cores)])

    if config.gpu:
        starccm_command.extend(["-gpgpu", "auto"])

    # output CSV file
    starccm_command.extend(jvm_property_argument("outFile", config.csvfile))

    # design study
    starccm_command.extend(jvm_property_argument("studyName", config.design_study))

    parameters = []
    range_args = []
    for range in config.ranges:
        parameters.append(range.parameter)

        for argpair in range.to_jvm_properties():
            range_args.extend(argpair)

    starccm_command.extend(jvm_property_argument("studyParameters", ",".join(parameters)))
    starccm_command.extend(range_args)


    # sbatch requires a shell script, so we create an executable temporary file with the contents we need
    fd, script_path = tempfile.mkstemp(prefix="scrt-sim", text=True)
    os.chmod(script_path, 0o755)

    batch_contents = BATCH_SCRIPT_TEMPLATE.format(starccm_command=" ".join(starccm_command))
    os.write(fd, batch_contents.encode())

    # pass script to sbatch
    command.append(script_path)

    if config.run:
        print("executing via slurm:")
        os.execvp("sbatch", command)
    else:
        print("simulation command:")
        print(command)
        print("script:")
        print(batch_contents)

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
    csvfile = sim_config["csv-filename"]
    project = sim_config["project"]
    design_study = sim_config["design-study"]

    ranges = []
    for range in raw_args.range:
        ranges.append(parse_range(range))

    slurm_dict = config_contents["slurm"]
    slurm_args = [f"--{key}={value}" for key, value in slurm_dict.items()]

    return Config(
        starccm_path=starccm_path,
        project=project,
        outfile=outfile,
        csvfile=csvfile,
        design_study=design_study,
        ranges=ranges,
        run=not raw_args.print_command,
        slurm_arguments=slurm_args,
        cores=slurm_dict["cpus-per-task"],
        gpu=slurm_dict.get("gpus", 0) > 0,
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
    return ["-jvmargs", f"-D{name}={value}"]

if __name__ == "__main__":
    main()
