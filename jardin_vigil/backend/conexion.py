import mysql.connector
from mysql.connector import Error

def conexion():
    conexion = None
    try:
        conexion = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = '',
            database = 'jardin_vigil'
        )
        print("Conexion Exitosa")
    except Error as e:
        print(f"error al conectar con la BDD: {e}")
    return conexion
def cerrar_conexion(conexion):
    if conexion.is_connected():
        conexion.close()
        print("Conexion Cerrada")
