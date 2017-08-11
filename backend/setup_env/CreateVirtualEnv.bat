@setlocal
@set PYTHON=python3.6
@set PYPATH=C:\Python36
@set ACTIVATION_SCRIPT=ActivateVirtualEnv.bat
@set DEACTIVATION_SCRIPT=DeactivateVirtualEnv.bat
@set RUN_UT_SCRIPT=RunUnitTests.bat

@set VIRTUAL_ENV=friendLocation

@cd ..
@%PYTHON% -m pip install setuptools --upgrade
@%PYTHON% -m pip install virtualenv --upgrade
@mkdir .pyEnv & cd .pyEnv
@%PYTHON% -m virtualenv --python=%PYPATH%\%PYTHON%.exe %VIRTUAL_ENV%
@cd ..
@echo @call ".pyEnv\%VIRTUAL_ENV%\Scripts\activate.bat"> %ACTIVATION_SCRIPT%
:: & echo.>> %ACTIVATION_SCRIPT%
@echo @deactivate> %DEACTIVATION_SCRIPT%
@call %ACTIVATION_SCRIPT%
@cd setup_env
@pip install -r requirements.txt --upgrade
@cd ..

@call %RUN_UT_SCRIPT%
@endlocal

@cd ..

@call ActivateVirtualEnv.bat