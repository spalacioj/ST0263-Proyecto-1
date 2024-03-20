import grpc
import FileSharing_pb2
import FileSharing_pb2_grpc

def enviar_chunks_al_servidor(file_location):
    # Establecer conexión con el servidor gRPC
    with grpc.insecure_channel('localhost:50051') as channel:
        # Crear un stub para el servicio ArchivoService
        stub = FileSharing_pb2_grpc.ArchivoServiceStub(channel)
        fileSize = 2 * 1024 * 1024
        # Abrir el archivo en modo lectura binaria
        with open(file_location, 'rb') as f:
            contador = 1
            # Leer el primer chunk
            chunk = f.read(fileSize)
            while True:
                if not chunk:
                    stub.ArchivoTerminado(FileSharing_pb2.Estado(terminado=True)) 
                    break
                # Enviar el chunk al servidor
                stub.EnviarChunk(FileSharing_pb2.ArchivoChunk(contenido=chunk))
                print(f"Chunk {contador} enviado")
                contador += 1
                # Leer el siguiente chunk
                chunk = f.read(fileSize)
                
            print("Todos los chunks han sido enviados")

def main():
    file_location = './testFiles/test.txt'  # Reemplazar con la ubicación del archivo
    enviar_chunks_al_servidor(file_location)

if __name__ == '__main__':
    main()
