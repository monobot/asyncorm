from constructor import MigrationConstructor
import os


filename = os.path.join('hola.py')

mc = MigrationConstructor(filename)
mc.set_models({'totorota': {'2': 1}})
