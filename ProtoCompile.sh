
rm -f *_pb2.py *_pb2_grpc.py *_pb2.pyi


python -m grpc_tools.protoc -I ./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/FileSharing.proto
python -m grpc_tools.protoc -I ./protos --python_out=. --pyi_out=. --grpc_python_out=. ./protos/DataNode.proto
