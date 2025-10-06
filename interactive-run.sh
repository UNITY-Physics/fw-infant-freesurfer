#!/usr/bin/env bash 

GEAR=fw-infant-freesurfer
IMAGE=flywheel/infant-freesurfer:1.0.5
LOG=infant-freesurfer-1.0.5-68dfd97ad582c4bc28ca2806
user=/Users/nbourke/GD/atom/

# Command:
docker run -it --rm --entrypoint bash\
	-v $user/unity/fw-gears/${GEAR}/app/:/flywheel/v0/app\
	-v $user/unity/fw-gears/${GEAR}/utils:/flywheel/v0/utils\
	-v $user/unity/fw-gears/${GEAR}/shared/utils:/flywheel/v0/shared/utils\
	-v $user/unity/fw-gears/${GEAR}/run.py:/flywheel/v0/run.py\
	-v $user/unity/fw-gears/${GEAR}/${LOG}/input:/flywheel/v0/input\
	-v $user/unity/fw-gears/${GEAR}/${LOG}/output:/flywheel/v0/output\
	-v $user/unity/fw-gears/${GEAR}/${LOG}/work:/flywheel/v0/work\
	-v $user/unity/fw-gears/${GEAR}/${LOG}/config.json:/flywheel/v0/config.json\
	$IMAGE
