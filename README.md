# 1. breve descripción de la actividad
Un sistema de archivos distribuidos, permite compartir y acceder de forma concurrente un conjunto de archivos que se encuentran almacenados en diferentes nodos. Uno de los sistemas más maduros, vigente y antiguo de estos sistemas es el NFS (Network File System) desarrollado en su momento por Sun Microsystems y que hoy en día es ampliamente usado en sistemas Linux. Hay otros sistemas de archivos distribuidos como AFS (Andrew File System) y SMB (Server Message Block) conocido como CIFS

## 1.1. Que aspectos cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)
Se ha completado la implementación de un servidor de metadatos, denominado name-node, encargado de administrar la asignación y ubicación de las particiones o chunks de los archivos cargados, así como de mantener un registro de qué data-node almacena cada chunk correspondiente a los archivos. Además, se ha desarrollado un cliente con la capacidad de comunicarse de manera efectiva tanto con el name-node como con los data-nodes respectivos, permitiendo la subida y descarga de archivos de manera eficiente. Asimismo, se ha establecido un entorno de data-node capaz de almacenar y distribuir los chunks de los archivos, cumpliendo así con los requisitos de almacenamiento y transmisión de datos establecidos en el sistema.

## 1.2. Que aspectos NO cumplió o desarrolló de la actividad propuesta por el profesor (requerimientos funcionales y no funcionales)
Se completaron todas las funciones de este proyecto pero se pudo mejorar mas la funcion de replicacion de los chunks

# 2. información general de diseño de alto nivel, arquitectura, patrones, mejores prácticas utilizadas.
El tipo de arquitectura que se uso para este proyecto es un sistema distribuido que se caracteriza por su enfoque en la redundancia, la alta disponibilidad y la tolerancia a fallos. En el diseño que se hizo, hay un nodo central (el NameNode Leader) que coordina las operaciones y múltiples nodos que almacenan datos (DataNodes). Los clientes interactúan con el sistema a través de varios puntos de entrada, lo que sugiere escalabilidad y capacidad para manejar múltiples solicitudes concurrentes.

# 3. Descripción del ambiente de desarrollo y técnico: lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.
Es recomendable crear un entorno virtual de python para no tener problema con las versiones, para instalar las librerias usar el comando:   
```
pip install -r requirements.txt
```
para que el proyecto lea los archivos que se quieran subir al data node es necesario tenerlos en una carpeta llamada "testFiles"

es necesario crear los archivos de grpc para esto ejecutar "ProtoCompile.sh" de esta manera

```./ProtoCompile.sh```

primero se deben ejecutar los datanode para esto usar este comando
```
python dataNode.py PUERTO
```
el PUERTO de manera local son:
- 50052
- 50053
- 50054

se debe ejecutar el archivo dataNode.py en 3 consolas distintas usando cada uno de estos puertos.

luego se ejecuta el server.py el cual seria el nameNode del proyecto y por ultimo el cliente.py usando estos comandos

```
python server.py
python client.py
```

para hacer las pruebas se recomienda usar una aplicacion como postman y tenemos 3 endpoints para usar:
- "[/createRuta](http://localhost:5000/createRuta)": que es de tipo POST y en el body pasamos 'archivo' que solo es el nombre con la extension ya que los va a buscar dentro de testFiles y tambien pasamos 'chunks' como string que son los chunks en los que quiere que se divida el archivo
- "[/listar](http://localhost:5000/listar)": esta es de tipo GET por lo cual no es necesario pasarle nada y nos retorna los archivo que tiene el server
- "[/descargar](http://localhost:5000/descargar/fileName)" esta es de tipo GET pero al final de la url es necesario pasarle el nombre que el archivo que queremos descargar esto retorna si lo descargo o no encontro el archivo


# 4. Descripción del ambiente de EJECUCIÓN (en producción) lenguaje de programación, librerias, paquetes, etc, con sus numeros de versiones.



