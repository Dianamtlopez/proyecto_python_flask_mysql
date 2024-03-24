################################################################################
# Investigado por: DIANA MARIA TORO LOPEZ                                      #
# Descripción: Este ejemplo muestra cómo interactuar con una base de datos     #
# MySQL utilizando Python y Flask. Implementa un CRUD (Create, Read, Update,   #
# Delete) para gestionar datos en la base de datos. Además, proporciona la     #
# funcionalidad de descargar la información de la base de datos en un archivo  #
# .csv y cargar información desde un archivo .csv.                             #
################################################################################

# importamos los módulos a utilizar
from flask import Flask, render_template, request, redirect, url_for, make_response
import os
import pandas as pd
import database as db


# Accedemos a la carpeta del proyecto
template_dir = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
# unimos el path a las dos carpetas creadas
template_dir = os.path.join(template_dir, 'src','templates') 

# Inicializamos flask para lanzar la aplicacion a traves de un puerto
# Rutas de la aplicación, directorio donde está index html  y su controlador 
# y pueda renderizarlo en pantalla
app =  Flask(__name__, template_folder=template_dir)

# Rutas de la aplicación
@app.route('/', methods=['GET'])
def home():
    # Creamos un cursor para acceder a la base de datos
    cursor = db.database.cursor()
    # Obteneos  todos los registros de la tabla "usuarios"
    # Obtener los datos en un objeto SQL 
    cursor.execute("SELECT * FROM users")
    myresult = cursor.fetchall()
    # Convertir los datos a diccionario para obtener un key de los datos y poder acceder desde la vista
    insertObject = []
    # obtener los nombres de columnas
    columnNames = [column[0] for column in cursor.description]
    # itera  cada fila y añade al array con los valores correspondientes a las columnas
    for record in myresult:
        insertObject.append(dict(zip(columnNames,record)))
    # Cerramos el cursor
        cursor.close()

    # Renderizamos
    return render_template('index.html', data=insertObject)

# Ruta para guardar usuarios en la base de datos
@app.route('/user', methods=['POST'])
def addUser():
    # Recogemos los valores introducidos por POST
    # Obtener el valor del campo 'username' enviado por POST
    username = request.form['username']
    # Obtener el valor del campo 'name' enviado por POST
    name = request.form['name']  
    # Obtener el valor del campo 'password' enviado por POST
    password = request.form['password']
    # Verificar que los campos no estén vacíos
    if username and name and password:
        # Obtener un cursor para interactuar con la base de datos
        cursor = db.database.cursor()
        # Definir la consulta SQL para insertar un usuario
        sql = "INSERT INTO users (username, name, password) VALUES (%s, %s, %s)"
        # Crear una tupla con los datos del usuario
        data = (username, name, password)
        # Ejecutar la consulta SQL con los datos proporcionados
        cursor.execute(sql, data)
        # Confirmar los cambios en la base de datos
        db.database.commit()
    # Redirigir a la página de inicio después de añadir un usuario
    return redirect(url_for('home'))
    
# Ruta para eliminar usuarios en la base de datos
@app.route("/delete/<string:id>", )
def deleteUser(id):
    # Obtener un cursor para interactuar con la base de datos
    cursor = db.database.cursor()
    # Definir la consulta SQL para eliminar un usuario
    sql = "DELETE FROM users where id=%s"
    # Crear una tupla con el ID del usuario a eliminar
    data = (id,)
    # Ejecutar la consulta SQL con el ID proporcionado
    cursor.execute(sql, data)
    # Confirmar los cambios en la base de datos
    db.database.commit()
    # Acctualiza la vista y re dirige a index.html
    return redirect(url_for('home'))

# Ruta para actualizar
@app.route("/edit/<string:id>", methods=["POST"])
def edit(id):
    # Recogemos los valores introducidos por POST
    # Obtener el valor del campo 'username' enviado por POST
    username = request.form['username']
    # Obtener el valor del campo 'name' enviado por POST
    name = request.form['name']  
    # Obtener el valor del campo 'password' enviado por POST
    password = request.form['password']
    # Verificar que los campos no estén vacíos
    if username and name and password:
        # Obtener un cursor para interactuar con la base de datos
        cursor = db.database.cursor()
        # Definir la consulta SQL para actualizar un usuario
        sql = "UPDATE users SET username = %s, name= %s, password = %s WHERE id = %s"
        # Crear una tupla con los datos actualizados del usuario
        data = (username, name, password, id)
        # Ejecutar la consulta SQL con los datos proporcionados
        cursor.execute(sql, data)
        # Confirmar los cambios en la base de datos
        db.database.commit()
    # Acctualiza la vista y re dirige a index.html
    return redirect(url_for('home'))

@app.route('/downloader-csv', methods=['GET'])
def procesarDescarga():
    if request.method == 'GET':
        # Obtener un cursor para interactuar con la base de datos
        cursor = db.database.cursor()
        # Ejecutar una consulta SQL para seleccionar todos los usuarios
        cursor.execute("SELECT * FROM users")
        # Obtener todos los resultados de la consulta
        myresult = cursor.fetchall()
        # Cerramos el cursor
        cursor.close()

        '''  
        En este ejemplo, he usado la variable csv_data += para agregar cada registro de la lista
        a una cadena de texto en formato CSV. 
        '''
        # Crear una cadena de texto en formato CSV el cual será el encabezado
        columnNames = [column[0] for column in cursor.description]
        # Agregar el encabezado al contenido CSV
        csv_header  = ','.join(columnNames) + "\n"
        # Crear una cadena de texto en formato CSV para cada registro
        csv_data = csv_header
        # itera sobre cada fila de los resultados e ingresa sus valores separados por comas
        for record in myresult:
            # une los elementos de la tupla en una sola cadena de texto separada por ","
            csv_row = ','.join(str(value) for value in record) + "\n"
            # agrega cada fila al contenido total de csv_data
            csv_data += csv_row

        # Crear una respuesta y establecer encabezados
        response = make_response(csv_data)
        # Establecer el nombre del archivo que se descargará como "my_data.csv"
        response.headers['Content-Disposition'] = 'attachment; filename=my_data.csv'
        # Indicar que el tipo MIME es text/csv
        response.headers['Content-Type'] = 'text/csv'
        # retorna la respuesta
        return response
    else:
        # retorna  un mensaje si no se realiza correctamente la solicitud HTTP GET
        return 'Método HTTP incorrecto'

# cargar archivo
UPLOAD_FOLDER = "uploads"
# establece la ubicación donde se guardarán los archivos cargados por los usuarios.
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# si no existe  la carpeta uploads la creamos
if not os.path.exists(UPLOAD_FOLDER):
    # creamos la carpeta uploads
    os.makedirs(UPLOAD_FOLDER)

@app.route('/cargar-csv', methods=['POST'])
def uploadFiles():
    # Obtener el archivo enviado mediante POST
    uploaded_file = request.files['file']
    # Verificar que se haya seleccionado un archivo
    if uploaded_file.filename != '':
        # agregamos el nombre completo del archivo a la lista
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename) 
        # Guardar el archivo en su lugar correspondiente
        uploaded_file.save(file_path)   
        # para procesar el archivo CSV que ha sido cargado por el usuario.
        parseCSV(file_path)
    # Acctualiza la vista y re dirige a index.html, mostrando un mensaje 
    # indicando que el archivo fue subido exitosamente
    return redirect(url_for('home'))

# Función para analizar un archivo CSV y insertar sus datos en la base de datos
def parseCSV (filepath):
    # Crea un cursor para interactuar con la base de datos.
    cursor = db.database.cursor()
    #  Ejecuta una consulta SQL para seleccionar todos los registros de la tabla users en la bd.
    cursor.execute("SELECT * FROM users")
    # Obtiene todos los resultados de la consulta ejecutada anteriormente y los almacena en la variable result.
    result = cursor.fetchall()

    # Comprobar si no hay resultados
    if not result:
        # Si no hay resultados, proceder con la inserción de datos desde el archivo CSV
        print("No se encontraron resultados en la consulta.")
        return

    # Obtener los nombres de las columnas de la tabla 'users' 
    col_names = [column[0] for column in cursor.description]

    # Leer el archivo CSV utilizando pandas y asignar los nombres de las columnas
    csvData = pd.read_csv(filepath, names=col_names, header=None)

    # Iterar sobre cada fila del DataFrame 'csvData' e insertar los valores en la BD
    for i, row in csvData.iterrows():
        # Definir la consulta SQL para insertar los datos en la tabla 'users'
        sql = "INSERT INTO users (username, name, password) VALUES (%s, %s, %s)"
        # Crear una tupla con los valores de la fila actual del DataFrame
        data = (row['username'], row['name'], row['password'])
        # Ejecutar la consulta SQL con los valores de la tupla 'data'
        cursor.execute(sql, data)
        # Confirmar los cambios en la base de datos
        db.database.commit()


# Lanzar la aplicacion  en el puerto 5000
if __name__ == "__main__":
    # Indicamos que estamos en modo de desarrollo
    app.run(debug=True)