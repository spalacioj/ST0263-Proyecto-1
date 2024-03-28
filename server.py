from concurrent import futures

import grpc
import FileSharing_pb2
import FileSharing_pb2_grpc
import google.protobuf.empty_pb2 as empty_pb2



class ArchivoService(FileSharing_pb2_grpc.ArchivoServiceServicer):
    def __init__(self):
        self.contenido_archivo = b''
        self.chunkDict = {}

    def EnviarChunk(self, request, context):
        self.contenido_archivo += request.contenido
        print(request.fileInfo)
        fileParts = request.fileInfo.split()
        fileName = fileParts[0] + fileParts[2]
        fileName = f'{fileName}_c{fileParts[1]}'
        self.chunkDict[fileName] = request.contenido
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
