import os
import grpc
import FileSharing_pb2
import FileSharing_pb2_grpc

def Create(file_location, chunks, file_size):
    # Establecer conexión con el servidor gRPC
    file_extension = os.path.splitext(file_location)[1]
    fileName = os.path.splitext(os.path.basename(file_location))[0]
    with grpc.insecure_channel('localhost:50051',options=[
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.max_receive_message_length', 100 * 1024 * 1024)
    ]) as channel:
        
        # Crear un stub para el servicio ArchivoService
        stub = FileSharing_pb2_grpc.ArchivoServiceStub(channel) 
        chunkSize = int(file_size // chunks) + 1 # Le sumamos un 1 porque para leer el archivo usamos valores exactos y asi el archivo no quedara incompleto
        fileSize = chunkSize * 1024 * 1024
        # Abrir el archivo en modo lectura binaria
        with open(file_location, 'rb') as f:
            contador = 0
            # Leer el primer chunk
            chunk = f.read(fileSize)
            while contador < chunks:
                # Enviar el chunk al servidor
                fileInfo = f'{fileName} {contador} {file_extension}'
                stub.EnviarChunk(FileSharing_pb2.ArchivoChunk(contenido=chunk,fileInfo=fileInfo))
                print(f"Chunk {contador} enviado")
                contador += 1
                # Leer el siguiente chunk
                chunk = f.read(fileSize)
            stub.ArchivoTerminado(FileSharing_pb2.Estado(terminado=True, fileExtension=file_extension))
            print("Todos los chunks han sido enviados")



def main():
    file_location = './testFiles/image.jpg'  
    Create(file_location,2,9.7)

if __name__ == '__main__':
    main()
