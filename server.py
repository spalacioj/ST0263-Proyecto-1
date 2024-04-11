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
        self.chunkDict = {} #guarda el nombre del chunk con el contenido para enviarlo al datanode
        self.listFiles = {} #guarda el nombre del chunk y en que datanode se encuentra
        self.SimpleList = [] #guarda los archivos disponibles
        self.dictList = [] # guarda un array con los dicts de cada archivo
        self.replicaList = [] #guarda un array con los dicts de replica de cada archivo
        self.ipsDisponibles = [os.environ['DATA_NODE_1'], os.environ['DATA_NODE_2'], os.environ['DATA_NODE_3']]
        
        
    def EnviarArchivo(self, request, context):
        contenido = request.contenido
        fileName = request.fileName
        fileExt = request.fileExt
        Name = f'{fileName}{fileExt}'
        self.SimpleList.append(Name) 
        self.crearDictFile(fileName, fileExt, contenido)
        active_datanodes = self.Heartbeat()
        tempDict = {}
        for i, (chunk_name, chunk) in enumerate(self.chunkDict.items()):
            datanode_ip = active_datanodes[i % len(active_datanodes)]
            0
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

            #Enviar al nodo siguiente una replica
            nexDataNodeIP = active_datanodes[(i + 1) % len(active_datanodes)]
            with grpc.insecure_channel(nexDataNodeIP,options=[
                ('grpc.max_send_message_length', 100 * 1024 * 1024),
                ('grpc.max_receive_message_length', 100 * 1024 * 1024)
            ]) as channel:
                stub = DataNode_pb2_grpc.DataServiceStub(channel)
                response = stub.RecibirParticion(DataNode_pb2.Particion(
                    contenido=chunk,
                    fileInfo=chunk_name
                ))
            tempDict[chunk_name] = nexDataNodeIP
        self.replicaList.append(tempDict)
        print("Todos los chunks fueron enviados")
        print(self.listFiles)
        self.DownloadDict()
        print('principal download dict')
        print(self.dictList)
        print('Replica download dict')
        print(self.replicaList)
        return FileSharing_pb2.Respuesta(mensaje="Chunk recibido exitosamente")
           
    def chunksArchivo(self, request, context):
        keysArray = list(self.listFiles.keys())
        valuesArray = list(self.listFiles.values())
        return FileSharing_pb2.Dict(
            keys=keysArray, 
            values=valuesArray
            )
    
    def ListarArchivos(self, request, context):
        return FileSharing_pb2.Lista(archivos=self.SimpleList)

    def Heartbeat(self):
        dataNodeSize = []
        for ip in listaDataNodes.keys():
            try:
                with grpc.insecure_channel(ip,options=[
                ('grpc.max_send_message_length', 100 * 1024 * 1024),
                ('grpc.max_receive_message_length', 100 * 1024 * 1024)
                ]) as channel:
                    stub = DataNode_pb2_grpc.DataServiceStub(channel)
                    response = stub.heartBeat(empty_pb2.Empty())
                    size = response.cantidadChunks
                    dataNodeSize.append((ip, size))
            except:
                listaDataNodes[ip] = False
                self.replicarChunks(ip)
                        

        data_nodes_sizes_sorted = sorted(dataNodeSize, key=lambda x: x[1])
        sortedIPs = []
        for ip, size in data_nodes_sizes_sorted:
            sortedIPs.append(ip)
        print(sortedIPs)
        return sortedIPs
    
    def descargarArchivo(self, request, context):
        FileName = request.nombre
        diccionario = self.EncontrarDict(FileName)
        diccionarioReplica = self.EncontrarDictReplica(FileName)
        activeIPs = self.Heartbeat()
        if(len(activeIPs) == 3):
            keysArray = list(diccionario.keys())
            valuesArray = list(diccionario.values())
            return FileSharing_pb2.Dict(
                keys=keysArray, 
                values=valuesArray
                )
        else:
            for name, ip in diccionario.items():
                if ip not in activeIPs:
                    ipReplica = diccionarioReplica[name]
                    diccionario[name] = ipReplica
            keysArray = list(diccionario.keys())
            valuesArray = list(diccionario.values())
            return FileSharing_pb2.Dict(
                keys=keysArray, 
                values=valuesArray
                )

    #metodos que no son de grpc pero ayudan para no tener tanto codigo en el mismo metodo
    def crearDictFile(self, fileName,  fileExt ,arrayOfChunks):
        self.chunkDict = {}
        contador = 1
        for chunk in arrayOfChunks:
            dictKey = f'{fileName}_C{contador}{fileExt}'
            self.chunkDict[dictKey] = chunk
            self.listFiles[dictKey] = ''
            contador += 1

    def DownloadDict(self):
        for key, value in self.listFiles.items():
            self.listFiles[key] = NameDataNodes[value]
        self.dictList.append(self.listFiles)
        self.listFiles = {}

    def EncontrarDict(self, file):
        for diccionario in self.dictList:
            for clave in diccionario.keys():
                FileWithoutExt, Ext = file.split(".")
                if FileWithoutExt in clave and Ext in clave:
                    return diccionario
    
    def EncontrarDictReplica(self, file):
        for diccionario in self.replicaList:
            for clave in diccionario.keys():
                FileWithoutExt, Ext = file.split(".")
                if FileWithoutExt in clave and Ext in clave:
                    return diccionario

    def replicarChunks(self, ip):
    # Recorrer el diccionario principal para buscar qué chunks tienen la IP del datanode caído
        chunk_sin_replica_main = []
        chunk_sin_replica_secondary = []

        for diccionario in self.dictList + self.replicaList:
            for key, value in diccionario.items():
                if value == ip:
                    if diccionario in self.dictList:
                        chunk_sin_replica_main.append(key)
                    else:
                        chunk_sin_replica_secondary.append(key)

        for chunk in chunk_sin_replica_main:
            indice = self.ipsDisponibles.index(ip)
            nueva_posicion = (indice + 2) % len(self.ipsDisponibles)
            siguiente_ip = self.ipsDisponibles[nueva_posicion]
            ipChunkSecundario = self.buscarIP(chunk, 1)
            for diccionario in self.dictList:
                for key, value in diccionario.items():
                    if key == chunk:
                        diccionario[key] = siguiente_ip
            with grpc.insecure_channel(ipChunkSecundario,options=[
                ('grpc.max_send_message_length', 100 * 1024 * 1024),
                ('grpc.max_receive_message_length', 100 * 1024 * 1024)
            ]) as channel:
                stub = DataNode_pb2_grpc.DataServiceStub(channel)
                stub.Replicar(DataNode_pb2.InfoReplicar(
                    ipReplicar=siguiente_ip,
                    nombre=chunk
                ))
            #se hace la conexion grpc con esta ip y se le pasa el nombre del chunk y la ip de a donde debe enviarlo, definir el metodo en grpc 
                    

        for chunk in chunk_sin_replica_secondary:
            indice = self.ipsDisponibles.index(ip)
            nueva_posicion = (indice + 1) % len(self.ipsDisponibles)
            siguiente_ip = self.ipsDisponibles[nueva_posicion]
            ipChunkPrincipal = self.buscarIP(chunk, 2)
            for diccionario in self.replicaList:
                for key, value in diccionario.items():
                    if key == chunk:
                        diccionario[key] = siguiente_ip 
            with grpc.insecure_channel(ipChunkPrincipal,options=[
                ('grpc.max_send_message_length', 100 * 1024 * 1024),
                ('grpc.max_receive_message_length', 100 * 1024 * 1024)
            ]) as channel:
                stub = DataNode_pb2_grpc.DataServiceStub(channel)
                stub.Replicar(DataNode_pb2.InfoReplicar(
                    ipReplicar=siguiente_ip,
                    nombre=chunk
                ))
        

    def buscarIP(self, chunkName, dictType):
        if dictType == 1:
            for diccionario in self.replicaList:
                if chunkName in diccionario:
                    return diccionario[chunkName]
        else: 
            for diccionario in self.dictList:
                if chunkName in diccionario:
                    return diccionario[chunkName]
    

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
