import os
import grpc
import FileSharing_pb2
import FileSharing_pb2_grpc
import DataNode_pb2
import DataNode_pb2_grpc
import time
import google.protobuf.empty_pb2 as empty_pb2



def Create(file_location, chunks):
    # Establecer conexión con el servidor gRPC
    fileExtension = os.path.splitext(file_location)[1]
    fileName = os.path.splitext(os.path.basename(file_location))[0]
    fileSize = os.path.getsize(file_location)
    with grpc.insecure_channel('localhost:50051',options=[
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.max_receive_message_length', 100 * 1024 * 1024)
    ]) as channel:
        
        # Crear un stub para el servicio ArchivoService
        stub = FileSharing_pb2_grpc.ArchivoServiceStub(channel) 
        
        chunkBytes = chunks * 1024 * 1024
        chunkSize = (fileSize // chunkBytes) + 1 # Le sumamos un 1 porque para leer el archivo usamos valores exactos y asi el archivo no quedara incompleto
        chunkSize = chunkSize * 1024 * 1024

        ArrayChunks = ObtenerChunks(file_location, chunkSize, chunks) 
        response = stub.EnviarArchivo(FileSharing_pb2.Archivo(
            contenido=ArrayChunks,
            fileName=fileName,
            fileExt=fileExtension
        ))     

        print(response.mensaje)
       


def ObtenerChunks(file_location, chunkSize, numberOfChunks):
    chunks = []
    with open(file_location, 'rb') as f:
        contador = 0
        while contador < numberOfChunks:
            chunk = f.read(chunkSize)
            if not chunk:
                break
            chunks.append(chunk)
    return chunks
        

def ListChunks():
    with grpc.insecure_channel('localhost:50051',options=[
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.max_receive_message_length', 100 * 1024 * 1024)
    ]) as channel:
        stub = FileSharing_pb2_grpc.ArchivoServiceStub(channel)
        response = stub.chunksArchivo(empty_pb2.Empty())
        file_dict = dict(zip(response.keys, response.values))
        print(file_dict)
        
def SimpleList():
    with grpc.insecure_channel('localhost:50051',options=[
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.max_receive_message_length', 100 * 1024 * 1024)
    ]) as channel:
        stub = FileSharing_pb2_grpc.ArchivoServiceStub(channel)
        response = stub.ListarArchivos(empty_pb2.Empty())
        
        print(response.archivos)
        return str(response.archivos)

def Download(fileName):
    contenido = b''
    with grpc.insecure_channel('localhost:50051',options=[
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.max_receive_message_length', 100 * 1024 * 1024)
    ]) as channel:
        stub = FileSharing_pb2_grpc.ArchivoServiceStub(channel)
        response = stub.descargarArchivo(FileSharing_pb2.Nombre(
            nombre=fileName
        ))
        file_dict = dict(zip(response.keys, response.values))
    for chunkName, ip in file_dict.items():
        with grpc.insecure_channel(ip,options=[
            ('grpc.max_send_message_length', 100 * 1024 * 1024),
            ('grpc.max_receive_message_length', 100 * 1024 * 1024)
        ]) as channel:
            stub = DataNode_pb2_grpc.DataServiceStub(channel)
            response = stub.EnviarParticion(DataNode_pb2.NombreChunk(
                nombre=chunkName
            ))
            contenido += response.contenido
    with open(fileName, 'wb') as f:
        f.write(contenido)
        print('Archivo descargado')
    
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/createRuta',methods=['POST'])
def createRuta():
    body = request.json
    
    nombreArchivo = body['archivo']
    chunks = body["chunks"]
    ruta = f'./testFiles/{nombreArchivo}'
    try:
        with open(ruta,'rb') as f:
            Create(ruta, int(chunks))
            print("lei el archivo")
            return jsonify({"message": "archivo subido"})
    except Exception as e:
        print("no lei el archivo")
        print(e)
        return jsonify({"message": "No pude leer el archivo"})

@app.route('/listar')
def listar():
    res = SimpleList()
    return jsonify({"Lista de archivos": res})

@app.route("/descargar/<string:name>")
def descargar(name):
    try:
        Download(name)
        return jsonify({"message": "Archivo descargado"})
    except:
        return jsonify({"error":"El archivo no existe"})



if __name__ == '__main__':
    app.run(debug=True, port=5000)

""" def main():
    file_location = './testFiles/hola.mp4'  
    Create(file_location,3)
    time.sleep(3)
    SimpleList()
    #time.sleep(3)
    #Download('image.jpg')

if __name__ == '__main__':
    main() """

