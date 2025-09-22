#!/usr/bin/env python
"""The run script."""
import logging
import os
import sys

# import flywheel functions
from flywheel_gear_toolkit import GearToolkitContext
from utils.command_line import exec_command
from utils.parser import parse_config
from shared.utils.curate_output import demo
from utils.join_data import housekeeping


# Add top-level package directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Verify sys.path
print("sys.path:", sys.path)

# The gear is split up into 2 main components. The run.py file which is executed
# when the container runs. The run.py file then imports the rest of the gear as a
# module.

log = logging.getLogger(__name__)

def main(context: GearToolkitContext) -> None:
    # """Parses config and runs."""
    subject_label, session_label, input_label, age = parse_config(context)
    
    print("running main.sh...")
    command = "/flywheel/v0/app/main.sh"
    # Add the input path and age to the command
    command = f"{command} {subject_label} {session_label} {age}"
    exec_command(command,shell=True,cont_output=True)

    # Add demographic data to the output
    print("concatenating demographics...")
    demographics = demo (context)
    housekeeping(demographics)

# Only execute if file is run as main, not when imported by another module
if __name__ == "__main__":  # pragma: no cover
    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gear_context:

        # Initialize logging, set logging level based on `debug` configuration
        # key in gear config.
        gear_context.init_logging()

        # Pass the gear context into main function defined above.
        main(gear_context)
