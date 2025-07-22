# AI-Powered Laptop Support System

This monorepo contains the complete source code for the AI-Powered Laptop Support System, a multi-technology project designed to provide automated technical assistance.

<img width="1920" height="1080" alt="Screenshot (49)" src="https://github.com/user-attachments/assets/ef9e1768-a3cc-438c-8311-2129069fa539" />


## Overview

The system is composed of three main applications:
- **Angular Frontend (`apps/angular-frontend`):** A real-time chat interface for user interaction.
- **Django Backend (`apps/django-backend`):** An API layer that handles user requests, manages WebSocket connections, and communicates with the gRPC service.
- **.NET gRPC Service (`apps/dotnet-grpc-service`):** A high-performance C# service that interacts directly with the operating system to perform tasks like installing applications and querying hardware.

## Tech Stack

- **Frontend:** Angular 20, TypeScript, RxJS, WebSockets
- **Backend:** Django 4.2+, Django REST Framework, Django Channels
- **AI Model:** TensorFlow, HuggingFace Transformers (`bert-base-multilingual-cased`)
- **gRPC Service:** C# on .NET 9, ASP.NET Core gRPC
- **Database:** SQLite
- **Containerization:** Docker

## Getting Started

**NOTE:** Download models.7z from (**(https://drive.google.com/file/d/1iSRDumu0ZrKn9Vo3OEl1f-D8UcgrKb7A/view?usp=sharing)**) and extract it in main directory before running the project.

1. Navigate to **`apps`**, then one of the sub-projects listed in the directory
2. **Run projects**
   - .NET: `dotnet run`
   - Angular: `npm install && ng serve`
   - Django: `python3 manage.py runserver`

## Project Structure

- **`apps/`**: Contains the primary, deployable applications (Angular, Django, .NET).
- **`config/`**: Stores all configuration files, including environment variables and the JSON schemas for the AI.
