from concurrent import futures

import grpc
import FileSharing_pb2
import FileSharing_pb2_grpc
import google.protobuf.empty_pb2 as empty_pb2



class ArchivoService(FileSharing_pb2_grpc.ArchivoServiceServicer):
    def __init__(self):
        self.contenido_archivo = b''

    def EnviarChunk(self, request, context):
        self.contenido_archivo += request.contenido
        print("Chunk recibido")

        return FileSharing_pb2.Respuesta(mensaje="Chunk recibido exitosamente")
    
    def ArchivoTerminado(self, request, context):
    
        Terminado = request.terminado
        if Terminado:
            with open('archivo_recibido.txt', 'wb') as f:
                f.write(self.contenido_archivo)

        print("Archivo guardado exitosamente")
        return empty_pb2.Empty()

def iniciar_servidor():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    FileSharing_pb2_grpc.add_ArchivoServiceServicer_to_server(ArchivoService(), server)
    server.add_insecure_port('[::]:50051')
    print("Service is running... ")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    iniciar_servidor()
