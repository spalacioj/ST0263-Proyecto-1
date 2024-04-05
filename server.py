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
NameDataNodes = {}
listaDataNodes[os.environ['DATA_NODE_1']] = True
listaDataNodes[os.environ['DATA_NODE_2']] = True
listaDataNodes[os.environ['DATA_NODE_3']] = True
NameDataNodes['DN1'] = os.environ['DATA_NODE_1']
NameDataNodes['DN2'] = os.environ['DATA_NODE_2']
NameDataNodes['DN3'] = os.environ['DATA_NODE_3']

print(listaDataNodes)

class ArchivoService(FileSharing_pb2_grpc.ArchivoServiceServicer):
    def __init__(self):
        self.chunkDict = {}
        self.listFiles = {}
        self.SimpleList = []
        
        
    def EnviarArchivo(self, request, context):
        contenido = request.contenido
        fileName = request.fileName
        fileExt = request.fileExt
        Name = f'{fileName}{fileExt}'
        self.SimpleList.append(Name) 
        self.crearDictFile(fileName, fileExt, contenido)
        active_datanodes = []
        for ip, active in listaDataNodes.items():
            if active:
                active_datanodes.append(ip)
        for i, (chunk_name, chunk) in enumerate(self.chunkDict.items()):
            datanode_ip = active_datanodes[i % len(active_datanodes)]
            
            node_name = None
            for name, ip in NameDataNodes.items():
                if ip == datanode_ip:
                    node_name = name
                    break
            
            self.listFiles[chunk_name] = node_name

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
        print(self.listFiles)
        return FileSharing_pb2.Respuesta(mensaje="Chunk recibido exitosamente")
           
    def chunksArchivo(self, request, context):
        keysArray = list(self.listFiles.keys())
        valuesArray = list(self.listFiles.values())
        return FileSharing_pb2.ListaChunks(keys=keysArray, values=valuesArray)
    
    def ListarArchivos(self, request, context):
        return FileSharing_pb2.Lista(archivos=self.SimpleList)

    def Heartbeat(self, request, context):
        nombreNode = request.nombre
        print(nombreNode)
        return FileSharing_pb2.Respuesta(mensaje="Heartbeat recibido")
    
    def crearDictFile(self, fileName,  fileExt ,arrayOfChunks):
        contador = 1
        for chunk in arrayOfChunks:
            dictKey = f'{fileName}_C{contador}{fileExt}'
            self.chunkDict[dictKey] = chunk
            self.listFiles[dictKey] = ''
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
