#!/bin/sh

PYTHON=python3.6
SHEBANG="#!/bin/sh"
ACTIVATION_SCRIPT="ActivateVirtualEnv.sh"
DEACTIVATION_SCRIPT="DeactivateVirtualEnv.sh"

SQLURL="https://dev.mysql.com/get/Downloads/Connector-Python/"
SQLCONNECTOR="mysql-connector-python-2.1.6-1.el7.src.rpm"

VIRTUAL_ENV="friendLocation"

cd ..
mkdir -p .pyEnv
${PYTHON} -m pip install virtualenv
(cd .pyEnv && ${PYTHON} -m virtualenv --python=${PYTHON} ${VIRTUAL_ENV})
echo -e ${SHEBANG}"\nexport VIRTUAL_ENV=\"${VIRTUAL_ENV}\"\nsource .pyEnv/"${VIRTUAL_ENV}"/bin/activate\n" > ${ACTIVATION_SCRIPT}
echo -e ${SHEBANG}"\ndeactivate\nunset VIRTUAL_ENV\n" > ${DEACTIVATION_SCRIPT}
. ${ACTIVATION_SCRIPT}
(cd setup_env && pip install -r requirements.txt --upgrade)

# Download and install mysql-connector-python from mysql.com
(mkdir -p .mysql_build && cd .mysql_build &&\
 mkdir -p .sqlconnector && cd .sqlconnector &&\
  wget ${SQLURL}${SQLCONNECTOR} &&\
   bsdtar -xvf ${SQLCONNECTOR} *.tar.gz &&\
    tar -zxf *.tar.gz && cd $(ls -d */) &&\
     python setup.py install)
rm -r .mysql_build

. RunUnitTests.sh
