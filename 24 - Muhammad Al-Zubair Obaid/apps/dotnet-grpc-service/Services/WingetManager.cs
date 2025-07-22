// Services/WingetManager.cs
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Runtime.CompilerServices;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Threading.Tasks;
using LaptopSupport;
using Microsoft.Extensions.Logging;

namespace LaptopSupport.Services
{
    public class WingetManager
    {
        private readonly ILogger<WingetManager> _logger;
        // Regex to find percentage values in winget's progress bar output.
        private readonly Regex _progressRegex = new Regex(@"(\d+)\s*%", RegexOptions.Compiled);

        public WingetManager(ILogger<WingetManager> logger)
        {
            _logger = logger;
        }

        public async IAsyncEnumerable<ProgressUpdate> InstallAppsAsync(IEnumerable<string> appIds, [EnumeratorCancellation] CancellationToken cancellationToken)
        {
            int totalApps = new List<string>(appIds).Count;
            int appsCompleted = 0;

            foreach (var appId in appIds)
            {
                if (cancellationToken.IsCancellationRequested)
                {
                    yield return new ProgressUpdate { CurrentTask = "Installation cancelled.", Status = ProgressUpdate.Types.Status.Failed };
                    yield break;
                }

                var arguments = $"install --id {appId} --accept-package-agreements --accept-source-agreements --disable-interactivity";
                _logger.LogInformation("Executing WinGet command: winget {Arguments}", arguments);

                yield return new ProgressUpdate
                {
                    CurrentTask = $"Starting installation of {appId}...",
                    OverallPercentage = 0,
                    Status = ProgressUpdate.Types.Status.InProgress
                };

                var processStartInfo = new ProcessStartInfo
                {
                    FileName = "winget",
                    Arguments = arguments,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    StandardOutputEncoding = Encoding.UTF8,
                    StandardErrorEncoding = Encoding.UTF8
                };

                using var process = new Process { StartInfo = processStartInfo };
                
                var stdErrBuilder = new StringBuilder();
                var processCompletionSource = new TaskCompletionSource<bool>();
                int lastReportedPercentage = -1;
                bool downloadComplete = false;

                process.EnableRaisingEvents = true;
                process.Exited += (sender, args) => processCompletionSource.TrySetResult(true);
                
                process.ErrorDataReceived += (sender, args) => {
                    if (args.Data != null) {
                        stdErrBuilder.AppendLine(args.Data);
                    }
                };

                process.Start();
                
                using var cancellationTokenRegistration = cancellationToken.Register(() =>
                {
                    _logger.LogWarning("Cancellation token invoked. Terminating winget process (ID: {ProcessId}).", process.Id);
                    try { process.Kill(true); }
                    catch (Exception ex) { _logger.LogError(ex, "Exception while trying to kill process."); }
                });

                process.BeginErrorReadLine();

                while (!process.StandardOutput.EndOfStream)
                {
                    var line = await process.StandardOutput.ReadLineAsync(cancellationToken);
                    if (line != null)
                    {
                        _logger.LogTrace("WinGet stdout: {Output}", line);

                        var match = _progressRegex.Match(line);
                        if (match.Success && int.TryParse(match.Groups[1].Value, out int percentage))
                        {
                            if (percentage != lastReportedPercentage)
                            {
                                int overallPercentage = (int)((appsCompleted + (percentage / 100.0)) / totalApps * 100);
                                
                                if (percentage == 100 && !downloadComplete)
                                {
                                    downloadComplete = true;
                                    yield return new ProgressUpdate
                                    {
                                        CurrentTask = $"Finalizing installation for {appId}...",
                                        OverallPercentage = (int)((appsCompleted + 0.99) / totalApps * 100),
                                        Status = ProgressUpdate.Types.Status.InProgress
                                    };
                                } 
                                else if (!downloadComplete)
                                {
                                     yield return new ProgressUpdate
                                    {
                                        CurrentTask = $"Downloading/Installing {appId}...",
                                        OverallPercentage = overallPercentage,
                                        Status = ProgressUpdate.Types.Status.InProgress
                                    };
                                }
                                lastReportedPercentage = percentage;
                            }
                        }
                    }
                }

                await processCompletionSource.Task;

                if (process.ExitCode == 0)
                {
                    appsCompleted++;
                    _logger.LogInformation("Successfully installed {AppId}", appId);
                    yield return new ProgressUpdate
                    {
                        CurrentTask = $"✅ Successfully installed {appId}.",
                        OverallPercentage = (int)(((double)appsCompleted / totalApps) * 100),
                        Status = ProgressUpdate.Types.Status.InProgress
                    };
                }
                else
                {
                    var errorOutput = stdErrBuilder.ToString();
                    if (cancellationToken.IsCancellationRequested)
                    {
                         yield return new ProgressUpdate
                        {
                            CurrentTask = $"Installation of {appId} was cancelled.",
                            OverallPercentage = (int)(((double)appsCompleted / totalApps) * 100),
                            Status = ProgressUpdate.Types.Status.Failed
                        };
                    }
                    else
                    {
                        _logger.LogError("Failed to install {AppId}. Exit Code: {ExitCode}. Error: {Error}", appId, process.ExitCode, errorOutput);
                        yield return new ProgressUpdate
                        {
                            CurrentTask = $"❌ Failed to install {appId}. Error: {errorOutput}",
                            OverallPercentage = (int)(((double)appsCompleted / totalApps) * 100),
                            Status = ProgressUpdate.Types.Status.Failed
                        };
                    }
                    yield break;
                }
            }

            yield return new ProgressUpdate { CurrentTask = "All installations completed successfully.", OverallPercentage = 100, Status = ProgressUpdate.Types.Status.Completed };
        }
    }
}
