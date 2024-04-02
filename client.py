import os
import grpc
import FileSharing_pb2
import FileSharing_pb2_grpc

def Create(file_location, chunks, file_size):
    # Establecer conexión con el servidor gRPC
    fileExtension = os.path.splitext(file_location)[1]
    fileName = os.path.splitext(os.path.basename(file_location))[0]
    with grpc.insecure_channel('localhost:50051',options=[
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.max_receive_message_length', 100 * 1024 * 1024)
    ]) as channel:
        
        # Crear un stub para el servicio ArchivoService
        stub = FileSharing_pb2_grpc.ArchivoServiceStub(channel) 
        fileInfo = f'{fileName}{fileExtension}'
        chunkSize = int(file_size // chunks) + 1 # Le sumamos un 1 porque para leer el archivo usamos valores exactos y asi el archivo no quedara incompleto
        chunkSize = chunkSize * 1024 * 1024

        ArrayChunks = ObtenerChunks(file_location, chunkSize, chunks) 
        response = stub.EnviarArchivo(FileSharing_pb2.Archivo(
            contenido=ArrayChunks,
            fileInfo=fileInfo
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
        
        
def main():
    file_location = './testFiles/image.jpg'  
    Create(file_location,4,9.7)

if __name__ == '__main__':
    main()
