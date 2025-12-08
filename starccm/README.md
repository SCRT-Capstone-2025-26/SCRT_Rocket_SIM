# STAR-CCM+ Batch Design Testing

Currently the only macro in this folder is [`RunStudyWithParameters.java`](macros/RunStudyWithParameters.java).

A convenience script ([`run_batch.py`](run_batch.py)) is also provided, since the `sbatch` command and corresponding batch script can get long.

## Running

First, copy `run_batch.py` and `RunStudyWithParameters.java` to the same directory on the HPC submission server.
You'll also want to make a copy of [the sample configuration](simulation.example.toml), updating its values as necessary.

Assuming everything is in the proper place and configured properly, running the study should be as simple as running `./run_batch.py path/to/simulation.toml`.

## Testing

A sample simulation and design project with corresponding `simulation.toml` are included in the [`sample-project/`](sample-project/) directory.

To run with the sample project, follow the process in the [Running](#running) section, also making sure to copy the simulation files to the same directory.
