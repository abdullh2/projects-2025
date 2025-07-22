// Services/SupportServiceImpl.cs
using Grpc.Core;
using LaptopSupport;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using System;
using Microsoft.AspNetCore.Cors;

namespace LaptopSupport.Services
{
    // Implements the business logic for the gRPC service.
    public class SupportServiceImpl : SupportService.SupportServiceBase
    {
        private readonly ILogger<SupportServiceImpl> _logger;
        private readonly WingetManager _wingetManager;
        private readonly SystemInfoService _systemInfoService;
        private readonly EnvironmentManager _environmentManager;

        public SupportServiceImpl(ILogger<SupportServiceImpl> logger, WingetManager wingetManager, SystemInfoService systemInfoService, EnvironmentManager environmentManager)
        {
            _logger = logger;
            _wingetManager = wingetManager;
            _systemInfoService = systemInfoService;
            _environmentManager = environmentManager;
        }

        // Handles the InstallApps RPC call.
        public override async Task InstallApps(InstallAppsRequest request, IServerStreamWriter<ProgressUpdate> responseStream, ServerCallContext context)
        {
            _logger.LogInformation("Received InstallApps request for {AppCount} apps.", request.AppIds.Count);
            await foreach (var update in _wingetManager.InstallAppsAsync(request.AppIds, context.CancellationToken))
            {
                if (context.CancellationToken.IsCancellationRequested)
                {
                    _logger.LogWarning("InstallApps operation was cancelled by the client.");
                    break;
                }
                await responseStream.WriteAsync(update);
            }
            _logger.LogInformation("Finished InstallApps request.");
        }

        // Handles the InstallEnvironment RPC call.
        public override async Task InstallEnvironment(InstallEnvironmentRequest request, IServerStreamWriter<ProgressUpdate> responseStream, ServerCallContext context)
        {
            _logger.LogInformation("Received InstallEnvironment request for '{EnvironmentId}'.", request.EnvironmentId);
            await foreach (var update in _environmentManager.SetupEnvironmentAsync(request.EnvironmentId, context.CancellationToken))
            {
                if (context.CancellationToken.IsCancellationRequested)
                {
                    _logger.LogWarning("InstallEnvironment operation was cancelled by the client.");
                    break;
                }
                await responseStream.WriteAsync(update);
            }
            _logger.LogInformation("Finished InstallEnvironment request for '{EnvironmentId}'.", request.EnvironmentId);
        }

        // Handles the QuerySystemInfo RPC call.
        public override async Task<SystemInfoResponse> QuerySystemInfo(QuerySystemInfoRequest request, ServerCallContext context)
        {
            _logger.LogInformation("Received QuerySystemInfo request.");
            try
            {
                var systemInfo = await _systemInfoService.GetSystemInfoAsync(request);
                return systemInfo;
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error occurred while querying system info.");
                return new SystemInfoResponse
                {
                    Error = new Error { Code = "QUERY_FAILED", Message = ex.Message }
                };
            }
        }
    }
}
