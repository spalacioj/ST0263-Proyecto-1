# Probar de manera local
es recomendable crear un entorno virtual de python para no tener problema con las versiones, para instalar las librerias usar el comando:   
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

