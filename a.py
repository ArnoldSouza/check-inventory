from cx_Freeze import setup, Executable


executables = [
    Executable(
        'central.py',
        icon="logo.ico"
    )
]

setup(name='Invente',
      version='0.1',
      description='Programa de auxilio em inventario Endicon',
      executables=executables)
