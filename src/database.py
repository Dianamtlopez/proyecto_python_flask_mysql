# Conexión a la base de datos
import mysql.connector  

database = mysql.connector.connect(
    host =  "localhost", 
    user = "root", 
    password= "Jpablo20",  
    database="python_bdd"                        #Nombre de la base de datos
)