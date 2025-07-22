**/apps**:
This directory contains the primary, deployable applications of the monorepo. Each subdirectory is a self-contained project that can be run, tested, and deployed independently.

## Applications
**angular-frontend/**: The user-facing web interface built with Angular 20. It communicates with the Django backend via REST APIs and WebSockets.

**django-backend/**: The core API layer built with Django. It handles business logic, user authentication, and orchestrates communication between the frontend and the .NET gRPC service.

**dotnet-grpc-service/**: A high-performance service built with C# and .NET 8. It is responsible for executing system-level tasks on the host machine, such as running PowerShell scripts, interacting with WinGet, and querying hardware information.