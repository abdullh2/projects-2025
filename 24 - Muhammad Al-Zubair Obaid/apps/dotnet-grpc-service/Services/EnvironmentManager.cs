// Services/EnvironmentManager.cs
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using System.Runtime.CompilerServices;
using System.Threading;
using System.Threading.Tasks;
using LaptopSupport;
using Microsoft.Extensions.Logging;

namespace LaptopSupport.Services
{
    public class EnvironmentManager
    {
        private readonly ILogger<EnvironmentManager> _logger;
        private readonly WingetManager _wingetManager;
        private readonly Dictionary<string, JsonElement> _environments;

        public EnvironmentManager(ILogger<EnvironmentManager> logger, WingetManager wingetManager)
        {
            _logger = logger;
            _wingetManager = wingetManager;
            // The path is relative to the C# project's execution directory
            _environments = LoadEnvironmentsFromFile("config/ai/environments.json");
        }

        private Dictionary<string, JsonElement> LoadEnvironmentsFromFile(string filePath)
        {
            var envs = new Dictionary<string, JsonElement>();
            try
            {
                _logger.LogInformation("Loading environment configs from: {FilePath}", Path.GetFullPath(filePath));
                var jsonString = File.ReadAllText(filePath);
                var config = JsonSerializer.Deserialize<JsonElement>(jsonString);
                foreach (var envElement in config.GetProperty("environments").EnumerateArray())
                {
                    envs.Add(envElement.GetProperty("id").GetString()!, envElement);
                }
                _logger.LogInformation("Successfully loaded {Count} environment templates.", envs.Count);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to load or parse environments.json");
            }
            return envs;
        }

        public async IAsyncEnumerable<ProgressUpdate> SetupEnvironmentAsync(string environmentId, [EnumeratorCancellation] CancellationToken ct)
        {
            var appInstallationPlan = new List<string>();
            var resolvedDependencies = new HashSet<string>();

            // Resolve dependencies recursively
            ResolveDependencies(environmentId, resolvedDependencies, appInstallationPlan);

            if (!appInstallationPlan.Any())
            {
                yield return new ProgressUpdate { CurrentTask = $"Environment '{environmentId}' not found or has no apps.", Status = ProgressUpdate.Types.Status.Failed };
                yield break;
            }

            _logger.LogInformation("Starting environment setup for '{EnvironmentId}' with apps: {Apps}", environmentId, string.Join(", ", appInstallationPlan));

            // Stream installation progress from WingetManager
            await foreach (var update in _wingetManager.InstallAppsAsync(appInstallationPlan, ct))
            {
                yield return update;
            }
        }

        private void ResolveDependencies(string environmentId, ISet<string> resolved, List<string> plan)
        {
            if (resolved.Contains(environmentId) || !_environments.TryGetValue(environmentId, out var envConfig))
            {
                return; // Already resolved or does not exist
            }

            // Recurse for dependencies first
            if (envConfig.TryGetProperty("dependencies", out var deps))
            {
                foreach (var dep in deps.EnumerateArray())
                {
                    ResolveDependencies(dep.GetString()!, resolved, plan);
                }
            }

            // Add this environment's apps to the plan
            if (envConfig.TryGetProperty("apps", out var apps))
            {
                foreach (var app in apps.EnumerateArray())
                {
                    var appId = app.GetString()!;
                    if (!plan.Contains(appId))
                    {
                        plan.Add(appId);
                    }
                }
            }

            resolved.Add(environmentId);
        }
    }
}
