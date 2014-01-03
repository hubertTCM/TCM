echo  %~dp0
cd /d %~dp0
set port=9000
start python %~dp0\manage.py runserver %port%
start http://127.0.0.1:%port%/

