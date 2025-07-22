// Program.cs
using LaptopSupport.Services;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Server.Kestrel.Core;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;

var builder = WebApplication.CreateBuilder(args);

// --- Add detailed debug logging ---
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.SetMinimumLevel(LogLevel.Debug);

// --- Configure Kestrel to listen on ALL network interfaces ---
builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenAnyIP(5220, o => o.Protocols = HttpProtocols.Http1AndHttp2);
});


// Define a CORS policy
builder.Services.AddCors(o => o.AddPolicy("strict-origin-when-cross-origin", builder =>
{
    builder.AllowAnyOrigin()
            .AllowAnyMethod()
            .AllowAnyHeader()
            .WithExposedHeaders("Grpc-Status", "Grpc-Message",
                "Grpc-Encoding", "Grpc-Accept-Encoding",
                "Grpc-Status-Details-Bin");
}));


// --- Register Services and Interceptors ---
builder.Services.AddSingleton<ServerLoggingInterceptor>();
builder.Services.AddGrpc(options =>
{
    options.Interceptors.Add<ServerLoggingInterceptor>();
    options.EnableDetailedErrors = true;
});
builder.Services.AddSingleton<WingetManager>();
builder.Services.AddSingleton<SystemInfoService>();
builder.Services.AddSingleton<EnvironmentManager>();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
}

app.UseRouting();

app.UseCors("strict-origin-when-cross-origin");
app.UseGrpcWeb(new GrpcWebOptions { DefaultEnabled = true });


app.MapGrpcService<SupportServiceImpl>().EnableGrpcWeb().RequireCors("strict-origin-when-cross-origin");
app.MapGrpcService<AdminServiceImpl>().EnableGrpcWeb().RequireCors("strict-origin-when-cross-origin");

app.MapGet("/", () => "Communication with gRPC endpoints must be made through a gRPC client.");

var logger = app.Services.GetRequiredService<ILogger<Program>>();
var addresses = app.Urls;
logger.LogInformation("==================================================================");
logger.LogInformation($"Application is running. Listening on addresses: {string.Join(", ", addresses)}");
logger.LogInformation("The Python gRPC client should connect to one of these addresses.");
logger.LogInformation("==================================================================");


app.Run();
