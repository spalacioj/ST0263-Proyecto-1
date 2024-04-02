from concurrent import futures

import os
import grpc
import FileSharing_pb2
import FileSharing_pb2_grpc
import DataNode_pb2
import DataNode_pb2_grpc
import google.protobuf.empty_pb2 as empty_pb2
from dotenv import load_dotenv

load_dotenv()

listaDataNodes = {}
listaDataNodes[os.environ['DATA_NODE_1']] = True
listaDataNodes[os.environ['DATA_NODE_2']] = True
listaDataNodes[os.environ['DATA_NODE_3']] = True
print(listaDataNodes)

class ArchivoService(FileSharing_pb2_grpc.ArchivoServiceServicer):
    def __init__(self):
        self.chunkDict = {}
        
    def EnviarArchivo(self, request, context):
        contenido = request.contenido
        fileInfo = request.fileInfo
        self.crearDictFile(fileInfo, contenido)
        active_datanodes = []
        for ip, active in listaDataNodes.items():
            if active:
                active_datanodes.append(ip)
        for i, (chunk_name, chunk) in enumerate(self.chunkDict.items()):
            datanode_ip = active_datanodes[i % len(active_datanodes)]
            with grpc.insecure_channel(datanode_ip,options=[
            ('grpc.max_send_message_length', 100 * 1024 * 1024),
            ('grpc.max_receive_message_length', 100 * 1024 * 1024)
            ]) as channel:
                stub = DataNode_pb2_grpc.DataServiceStub(channel)
                response = stub.RecibirParticion(DataNode_pb2.Particion(
                    contenido=chunk,
                    fileInfo=chunk_name
                ))
        print("Todos los chunks fueron enviados")
        return FileSharing_pb2.Respuesta(mensaje="Chunk recibido exitosamente")
           
       
    
    def ArchivoTerminado(self, request, context):
    
        Terminado = request.terminado
        FileExtension = request.fileExtension
        print(self.chunkDict)
        if Terminado:
            with open(f'archivo_recibido{FileExtension}', 'wb') as f:
                f.write(self.contenido_archivo)

        print("Archivo guardado exitosamente")
        return empty_pb2.Empty()
    
    def Heartbeat(self, request, context):
        nombreNode = request.nombre
        print(nombreNode)
        return FileSharing_pb2.Respuesta(mensaje="Heartbeat recibido")
    
    def crearDictFile(self, fileName, arrayOfChunks):
        contador = 1
        for chunk in arrayOfChunks:
            dictKey = f'{fileName}_C{contador}'
            self.chunkDict[dictKey] = chunk
            contador += 1

def iniciar_servidor():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),options=[
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.max_receive_message_length', 100 * 1024 * 1024)
    ])
    FileSharing_pb2_grpc.add_ArchivoServiceServicer_to_server(ArchivoService(), server)
    server.add_insecure_port('[::]:50051')
    print("Service is running... ")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    iniciar_servidor()
