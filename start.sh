#!/bin/env bash 

# Ensure script is interpreted with bash
set -e  # Exit on error
set -u  # Exit on undefined variables

# Set FSL environment variable
FSLDIR=/opt/conda
export FSLDIR

# Log the current shell and environment
echo "Current shell: $SHELL"
echo "Current interpreter: $(readlink -f /proc/$$/exe)"
echo "FSLDIR set to: $FSLDIR"

# Add FSL to PATH if needed
export PATH=$FSLDIR/bin:$PATH

# Optional: Source FSL configuration
if [ -f "${FSLDIR}/etc/fslconf/fsl.sh" ]; then
    source "${FSLDIR}/etc/fslconf/fsl.sh"
fi

# Run the gear
python3 -u /flywheel/v0/run.py
