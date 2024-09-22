import sqlite3

""" Se extraen los diámetros disponibles de las base de datos 
y se guardarán en la lista 'diametros_ES'
"""

conexion = sqlite3.connect("MechPropES")
cursor = conexion.cursor()
cursor.execute("SELECT DISTINCT diametro FROM PROPIEDADES_ES")
diametros_ES = [row[0] for row in cursor.fetchall()]
conexion.close()
