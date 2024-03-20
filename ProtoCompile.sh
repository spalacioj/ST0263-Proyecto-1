
rm -f FileSharing_pb2.py FileSharing_pb2_grpc.py FileSharing_pb2.pyi

python -m grpc_tools.protoc -I ./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/FileSharing.proto

