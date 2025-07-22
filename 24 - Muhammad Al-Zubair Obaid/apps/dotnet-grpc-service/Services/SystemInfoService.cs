// Services/SystemInfoService.cs
using LaptopSupport;
using Microsoft.Extensions.Logging;
using System;
using System.IO;
using System.Linq;
using System.Management;
using System.Threading.Tasks;

namespace LaptopSupport.Services
{
    // Retrieves system hardware and driver information using WMI.
    // NOTE: This service uses System.Management and is therefore Windows-specific.
    // It will not run on other operating systems.
    public class SystemInfoService
    {
        private readonly ILogger<SystemInfoService> _logger;

        public SystemInfoService(ILogger<SystemInfoService> logger)
        {
            _logger = logger;
        }

        public Task<SystemInfoResponse> GetSystemInfoAsync(QuerySystemInfoRequest request)
        {
            _logger.LogInformation("Gathering system information via WMI...");
            var response = new SystemInfoResponse();

            try
            {
                // Using ManagementObjectSearcher for various queries
                response.CpuName = GetWmiProperty("Win32_Processor", "Name");
                response.OsVersion = GetWmiProperty("Win32_OperatingSystem", "Caption");

                // Get RAM
                var ramQuery = new ManagementObjectSearcher("SELECT TotalVisibleMemorySize FROM Win32_OperatingSystem");
                var ram = ramQuery.Get().OfType<ManagementObject>().FirstOrDefault();
                if (ram != null)
                {
                    ulong totalRamKb = (ulong)ram["TotalVisibleMemorySize"];
                    response.RamTotalGb = $"{Math.Round(totalRamKb / (1024.0 * 1024.0), 2)} GB";
                }

                // Get GPU if requested
                if (request.IncludeGpuInfo)
                {
                    response.GpuName = GetWmiProperty("Win32_VideoController", "Name");
                }

                // Get Storage if requested
                if (request.IncludeStorageInfo)
                {
                    var diskQuery = new ManagementObjectSearcher("SELECT Model, Size, FreeSpace FROM Win32_LogicalDisk WHERE DriveType=3"); // Fixed disks
                    foreach (ManagementObject disk in diskQuery.Get())
                    {
                        response.StorageDevices.Add(new StorageDevice
                        {
                            Model = disk["Model"]?.ToString() ?? "N/A",
                            SizeGb = $"{Math.Round(Convert.ToDouble(disk["Size"]) / (1024.0 * 1024.0 * 1024.0), 2)}",
                            FreeSpaceGb = $"{Math.Round(Convert.ToDouble(disk["FreeSpace"]) / (1024.0 * 1024.0 * 1024.0), 2)}"
                        });
                    }
                }

                // FIX: Add driver information query if requested
                if (request.IncludeDrivers)
                {
                    var driverQuery = new ManagementObjectSearcher("SELECT DeviceName, DriverVersion, Status FROM Win32_PnPSignedDriver");
                    foreach (ManagementObject driver in driverQuery.Get())
                    {
                        response.Drivers.Add(new DriverInfo
                        {
                            DeviceName = driver["DeviceName"]?.ToString() ?? "N/A",
                            DriverVersion = driver["DriverVersion"]?.ToString() ?? "N/A",
                            Status = driver["Status"]?.ToString() ?? "Unknown"
                        });
                    }
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to retrieve system info from WMI.");
                response.Error = new Error { Code = "WMI_FAILURE", Message = ex.Message };
            }

            return Task.FromResult(response);
        }

        private string GetWmiProperty(string wmiClass, string property)
        {
            try
            {
                var searcher = new ManagementObjectSearcher($"SELECT {property} FROM {wmiClass}");
                var result = searcher.Get().OfType<ManagementObject>().FirstOrDefault();
                return result?[property]?.ToString() ?? "N/A";
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex, "Could not retrieve WMI property {Property} from {WmiClass}", property, wmiClass);
                return "Error";
            }
        }
    }
}
