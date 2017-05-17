@setlocal
@set PYTHON=python3.6
@set PYPATH=C:\Python36
@set ACTIVATION_SCRIPT=ActivateVirtualEnv.bat
@set DEACTIVATION_SCRIPT=DeactivateVirtualEnv.bat

@set SQLURL=https://dev.mysql.com/get/Downloads/Connector-Python/
@set SQLCONNECTOR=mysql-connector-python-2.1.6.zip

@set VIRTUAL_ENV=friendLocation

@cd ..
%PYTHON% -m pip install setuptools --upgrade
%PYTHON% -m pip install virtualenv --upgrade
@mkdir .pyEnv & cd .pyEnv
%PYTHON% -m virtualenv --python=%PYPATH%\%PYTHON%.exe %VIRTUAL_ENV%
@cd ..
@echo call ".pyEnv\%VIRTUAL_ENV%\Scripts\activate"> %ACTIVATION_SCRIPT% & echo.>> %ACTIVATION_SCRIPT%
@echo deactivate> %DEACTIVATION_SCRIPT%
@call %ACTIVATION_SCRIPT%
@cd setup_env
pip install -r requirements.txt --upgrade
@cd ..

:: Download and install mysql-connector-python from mysql.com
bitsadmin.exe /transfer "downloading mysql-connector-python" %SQLURL%%SQLCONNECTOR% %cd%\%SQLCONNECTOR%
::python setup.py install

@call RunUnitTests.bat
