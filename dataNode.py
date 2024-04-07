import sys
from concurrent import futures
import os
import grpc
import FileSharing_pb2
import FileSharing_pb2_grpc
import DataNode_pb2
import DataNode_pb2_grpc
import google.protobuf.empty_pb2 as empty_pb2

class DataService(DataNode_pb2_grpc.DataServiceServicer):

    def __init__(self):
        self.listaArchivos = {}
        
    def EnviarParticion(self, request, context):
        fileName = request.nombre
        contenido = self.listaArchivos[fileName]
        return DataNode_pb2.Particion(
            contenido=contenido,
            fileInfo=""
        )

    def RecibirParticion(self, request, context):
        nombre = request.fileInfo
        contenido = request.contenido
        self.listaArchivos[nombre] = contenido
        print('Chunk recibido')
        print(self.listaArchivos.keys())
        return empty_pb2.Empty()
    
    def heartBeat(self, request, context):
        mensaje = "Datanode Funcionando!"
        size = len(self.listaArchivos)
        return DataNode_pb2.InfoDataNode(
            mensaje=mensaje,
            cantidadChunks=size
        )



def iniciar_servidor(port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),options=[
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.max_receive_message_length', 100 * 1024 * 1024)
    ])
    DataNode_pb2_grpc.add_DataServiceServicer_to_server(DataService(), server)
    server.add_insecure_port(f'[::]:{port}')
    print("Service is running... ")
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    port = int(sys.argv[1])
    iniciar_servidor(port)
    #iniciar_servidor()

