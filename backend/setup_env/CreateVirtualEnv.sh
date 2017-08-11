#!/bin/sh

PYTHON=python3.6
SHEBANG="#!/bin/sh"
ACTIVATION_SCRIPT="ActivateVirtualEnv.sh"
DEACTIVATION_SCRIPT="DeactivateVirtualEnv.sh"

VIRTUAL_ENV="friendLocation"

cd ..
mkdir -p .pyEnv
${PYTHON} -m pip install virtualenv
(cd .pyEnv && ${PYTHON} -m virtualenv --python=${PYTHON} ${VIRTUAL_ENV})
echo -e ${SHEBANG}"\nexport VIRTUAL_ENV=\"${VIRTUAL_ENV}\"\nsource .pyEnv/"${VIRTUAL_ENV}"/bin/activate\n" > ${ACTIVATION_SCRIPT}
echo -e ${SHEBANG}"\ndeactivate\nunset VIRTUAL_ENV\n" > ${DEACTIVATION_SCRIPT}
. ${ACTIVATION_SCRIPT}
(cd setup_env && pip install -r requirements.txt --upgrade)

. RunUnitTests.sh
