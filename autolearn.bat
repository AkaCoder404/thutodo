@ECHO OFF
ECHO startup batch file for thutodo

@REM find python on path
For %%G In (python.exe) Do SET "PYTHONPATH=%%~$PATH:G"

@REM SET PYTHONPATH=%%p 

@REM ECHO %PYTHONPATH%
IF "%PYTHONPATH%"=="" Do EXIT 

@REM path to file
SET "FILE_PATH=%~f0"
@REM path to folder which bat is in
SET "CURR_PATH=%~dp0"
SET "MY_PATH=%cd%"

@REM ECHO %FILE_PATH%
@REM ECHO %CURR_PATH%
@REM ECHO %MY_PATH%

SET "LEARN_PY_PATH=%CURR_PATH%learn.py"
SET "DIDA_PY_PATH=%CURR_PATH%dida.py"

@REM ECHO %LEARN_PY_PATH%

@REM Insert Username and Password Here 
ECHO running learn.py
SET /P "USERNAME=Info Username: "
SET /P "PASSWORD=Info Password: "

"%PYTHONPATH%" "%LEARN_PY_PATH%" "%USERNAME%" "%PASSWORD%" 

ECHO running dida.py
SET /P "DIDA_USERNAME=Dida Username: "
SET /P "DIDA_PASSWORD=Dida Password: "
"%PYTHONPATH%" "%DIDA_PY_PATH%" "%DIDA_USERNAME%" "%DIDA_PASSWORD%"

@REM PAUSE

@REM notes
@REM auto.bat must be in the same folder as learn.py and dida.py
