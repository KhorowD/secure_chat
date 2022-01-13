# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from generated import chat_pb2 as generated_dot_chat__pb2


class ChatServerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ChatStream = channel.unary_stream(
                '/grpc.ChatServer/ChatStream',
                request_serializer=generated_dot_chat__pb2.Empty.SerializeToString,
                response_deserializer=generated_dot_chat__pb2.Note.FromString,
                )
        self.SendNote = channel.unary_unary(
                '/grpc.ChatServer/SendNote',
                request_serializer=generated_dot_chat__pb2.Note.SerializeToString,
                response_deserializer=generated_dot_chat__pb2.Empty.FromString,
                )
        self.RequestPQ = channel.unary_unary(
                '/grpc.ChatServer/RequestPQ',
                request_serializer=generated_dot_chat__pb2.req_pq.SerializeToString,
                response_deserializer=generated_dot_chat__pb2.res_pq.FromString,
                )


class ChatServerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ChatStream(self, request, context):
        """This bi-directional stream makes it possible to send and receive Notes between 2 persons
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def SendNote(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def RequestPQ(self, request, context):
        """Возвращает аутентификационную информацию со стороны сервера
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChatServerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ChatStream': grpc.unary_stream_rpc_method_handler(
                    servicer.ChatStream,
                    request_deserializer=generated_dot_chat__pb2.Empty.FromString,
                    response_serializer=generated_dot_chat__pb2.Note.SerializeToString,
            ),
            'SendNote': grpc.unary_unary_rpc_method_handler(
                    servicer.SendNote,
                    request_deserializer=generated_dot_chat__pb2.Note.FromString,
                    response_serializer=generated_dot_chat__pb2.Empty.SerializeToString,
            ),
            'RequestPQ': grpc.unary_unary_rpc_method_handler(
                    servicer.RequestPQ,
                    request_deserializer=generated_dot_chat__pb2.req_pq.FromString,
                    response_serializer=generated_dot_chat__pb2.res_pq.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'grpc.ChatServer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ChatServer(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ChatStream(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_stream(request, target, '/grpc.ChatServer/ChatStream',
            generated_dot_chat__pb2.Empty.SerializeToString,
            generated_dot_chat__pb2.Note.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def SendNote(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/SendNote',
            generated_dot_chat__pb2.Note.SerializeToString,
            generated_dot_chat__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def RequestPQ(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/grpc.ChatServer/RequestPQ',
            generated_dot_chat__pb2.req_pq.SerializeToString,
            generated_dot_chat__pb2.res_pq.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
