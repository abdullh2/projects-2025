// Services/ServerLoggingInterceptor.cs
using Grpc.Core;
using Grpc.Core.Interceptors;
using Microsoft.Extensions.Logging;
using System.Threading.Tasks;

namespace LaptopSupport.Services
{
    /// <summary>
    /// A gRPC server interceptor that logs details about incoming RPC calls.
    /// </summary>
    public class ServerLoggingInterceptor : Interceptor
    {
        private readonly ILogger<ServerLoggingInterceptor> _logger;

        public ServerLoggingInterceptor(ILogger<ServerLoggingInterceptor> logger)
        {
            _logger = logger;
        }

        public override async Task<TResponse> UnaryServerHandler<TRequest, TResponse>(
            TRequest request,
            ServerCallContext context,
            UnaryServerMethod<TRequest, TResponse> continuation)
        {
            _logger.LogDebug(
                "[gRPC Server] Starting Unary call. Method: {Method}, Peer: {Peer}, Request: {Request}",
                context.Method, context.Peer, request);
            try
            {
                var response = await continuation(request, context);
                _logger.LogInformation(
                    "[gRPC Server] Finished Unary call successfully. Method: {Method}",
                    context.Method);
                return response;
            }
            catch (RpcException e)
            {
                _logger.LogError(e,
                    "[gRPC Server] Error in Unary call. Method: {Method}, Status: {Status}",
                    context.Method, e.Status);
                throw;
            }
        }

        public override async Task ServerStreamingServerHandler<TRequest, TResponse>(
            TRequest request,
            IServerStreamWriter<TResponse> responseStream,
            ServerCallContext context,
            ServerStreamingServerMethod<TRequest, TResponse> continuation)
        {
            _logger.LogDebug(
                "[gRPC Server] Starting Server-Streaming call. Method: {Method}, Peer: {Peer}, Request: {Request}",
                context.Method, context.Peer, request);
            try
            {
                await continuation(request, responseStream, context);
                _logger.LogInformation(
                    "[gRPC Server] Finished Server-Streaming call successfully. Method: {Method}",
                    context.Method);
            }
            catch (RpcException e)
            {
                _logger.LogError(e,
                    "[gRPC Server] Error in Server-Streaming call. Method: {Method}, Status: {Status}",
                    context.Method, e.Status);
                throw;
            }
        }
    }
}
