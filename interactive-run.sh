#!/usr/bin/env bash 

GEAR=fw-recon-all-clinical
IMAGE=flywheel/recon-all-clinical:$1
LOG=recon-all-clinical-$1-$2

# Command:
docker run -it --rm --entrypoint bash\
	-v $3/unity/fw-gears/${GEAR}/app/:/flywheel/v0/app\
	-v $3/unity/fw-gears/${GEAR}/utils:/flywheel/v0/utils\
	-v $3/unity/fw-gears/${GEAR}/shared/utils:/flywheel/v0/shared/utils\
	-v $3/unity/fw-gears/${GEAR}/run.py:/flywheel/v0/run.py\
	-v $3/unity/fw-gears/${GEAR}/${LOG}/input:/flywheel/v0/input\
	-v $3/unity/fw-gears/${GEAR}/${LOG}/output:/flywheel/v0/output\
	-v $3/unity/fw-gears/${GEAR}/${LOG}/work:/flywheel/v0/work\
	-v $3/unity/fw-gears/${GEAR}/${LOG}/config.json:/flywheel/v0/config.json\
	$IMAGE
