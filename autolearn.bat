@ECHO OFF
ECHO startup batch file for thutodo

@REM find python on path
For %%G In (python.exe) Do Set "PYTHONPATH=%%~$PATH:G"

@REM SET PYTHONPATH=%%p

@REM ECHO %PYTHONPATH%

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

ECHO running learn.py
"%PYTHONPATH%" "%LEARN_PY_PATH%"
ECHO running dida.py
"%PYTHONPATH%" "%DIDA_PY_PATH%"

@REM PAUSE

@REM notes
@REM auto.bat must be in the same folder as learn.py and dida.py
