:: muda de lugar a fonte de execução
cd C:\Users\Endicon\PycharmProjects\rotativo

:: unicia as configurações para criação de autoexec
pyinstaller ^
	--log-level=INFO ^
	--upx-dir "C:\upx394w" ^
	--nowindowed ^
    --add-data="client_secret.json;." ^
    --add-data="logo.ico;img" ^
    --icon="logo.ico" ^
    central.py

pause