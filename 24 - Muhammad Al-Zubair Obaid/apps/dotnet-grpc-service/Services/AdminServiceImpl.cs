// Services/AdminServiceImpl.cs
using Grpc.Core;
using LaptopSupport;
using System.Threading.Tasks;
using Microsoft.Extensions.Logging;
using System.Diagnostics;
using Microsoft.AspNetCore.Cors;

namespace LaptopSupport.Services
{
    // Implements the business logic for the Admin gRPC service.
    public class AdminServiceImpl : AdminService.AdminServiceBase
    {
        private readonly ILogger<AdminServiceImpl> _logger;

        public AdminServiceImpl(ILogger<AdminServiceImpl> logger)
        {
            _logger = logger;
        }

        public override Task<RunCommandResponse> RunCommand(RunCommandRequest request, ServerCallContext context)
        {
            // In a real application, you would add a robust security check here
            // to ensure the caller is an authenticated administrator.
            _logger.LogWarning("--- ADMIN ACTION ---");
            _logger.LogWarning("Received request to run command: {Command} with args: {Args}", request.Command, string.Join(" ", request.Args));
            _logger.LogWarning("Execution is currently disabled for security. Returning a mock response.");

            // For this example, we will NOT execute the command.
            // We will log it and return a mock success response.
            var response = new RunCommandResponse
            {
                ExitCode = 0,
                StandardOutput = $"Mock execution of '{request.Command}'. This is a placeholder for a real admin action.",
                StandardError = ""
            };

            return Task.FromResult(response);
        }
    }
}
