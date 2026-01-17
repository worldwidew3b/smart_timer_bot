# Code Review and Refactoring Plan (BAD.md)

This document outlines the identified issues, bad practices, and deviations from the architecture proposed in `TODO.md`. The goal is to refactor the code to be more robust, maintainable, and secure.

## 🚨 Critical Issues

### 1. Hardcoded User IDs and Lack of Authentication
- **Problem**: Both the FastAPI backend and the Telegram bot use a hardcoded `user_id = 1` for all operations. This makes the application entirely non-functional for multiple users and is a critical security flaw.
- **Location**:
    - `src/api/endpoints/*.py` (all endpoint files)
    - `src/bot/handlers/**/*.py` (all handler files making API calls)
- **Proposed Solution**:
    - **Backend**: Implement a proper authentication system (e.g., using JWT or a simple token-based system). Create a `User` model as planned in `TODO.md`. Add a dependency to get the current authenticated user from a token.
    - **Bot**: Implement a user registration flow. When a user first starts the bot, create a corresponding user in the backend via the API and store the mapping between `telegram_id` and the backend `user_id`.

### 2. Inconsistent Layering and Business Logic in API Endpoints
- **Problem**: The `get_tasks` endpoint in `src/api/endpoints/tasks.py` contains complex query-building logic for filtering. This logic belongs in the service or repository layer, not the presentation (API) layer. This violates the "Separation of Concerns" principle.
- **Location**: `src/api/endpoints/tasks.py`
- **Proposed Solution**: Move the query-building and filtering logic from the `get_tasks` endpoint into the `TaskService` and/or `TaskRepository`. The API endpoint should only be responsible for receiving the request, calling the service, and returning the response.

### 3. Severe Performance Issue (N+1 Query Problem)
- **Problem**: The `get_tasks` endpoint in `src/api/endpoints/tasks.py` first fetches a list of tasks and then, inside a loop, executes a new query for each task to get its tags. This will result in a large number of database queries and cripple performance.
- **Location**: `src/api/endpoints/tasks.py`
- **Proposed Solution**: Use a single, more efficient query to fetch tasks and their associated tags together. SQLAlchemy's `selectinload` or `joinedload` options are designed for this purpose. This should be implemented in the `TaskRepository`.

### 4. Hardcoded Configuration and Secrets
- **Problem**: The database URL (including credentials) and the Telegram bot token are hardcoded. This is a major security risk and makes the application difficult to configure for different environments.
- **Location**:
    - `src/core/config.py` (default `database_url`)
    - `bot_runner.py` (hardcoded `token`)
- **Proposed Solution**: Remove all hardcoded secrets. Load these values strictly from environment variables using `pydantic-settings`. The application should fail to start if essential variables are missing.

##  architectural and Design Flaws

### 1. Leaky Abstractions and Incorrect Dependencies
- **Problem**: The domain layer (`src/domain/`) has direct dependencies on the infrastructure layer (`src/infrastructure/`). For example, `TaskService` imports `TaskRepository` directly. The `api_client` in the bot also directly imports domain models from the backend's source, tightly coupling two separate applications.
- **Location**:
    - `src/domain/services/*.py`
    - `src/bot/services/api_client.py`
- **Proposed Solution**:
    - **Backend**: Introduce an abstraction layer (e.g., Port/Adapter pattern). The `TaskService` should depend on an abstract `ITaskRepository` interface defined in the domain layer. The concrete implementation will be in the infrastructure layer and injected at runtime.
    - **Bot**: The bot is a separate client application. It should **not** share code with the backend. The `api_client` should define its own data transfer objects (DTOs) or Pydantic models to represent the data it gets from the API.

### 2. Code Duplication and Lack of Service Layer Usage
- **Problem**: The logic for filtering tasks exists in the `tasks.py` API endpoint but is missing from the `TaskService`. The service layer is being bypassed. This leads to code duplication if another part of the system needs to get tasks with the same filtering.
- **Location**: `src/api/endpoints/tasks.py`, `src/domain/services/task_service.py`
- **Proposed Solution**: Enhance the `TaskService` to handle all business logic, including filtering, pagination, and sorting. The API endpoints should be thin and delegate all work to the service layer.

### 3. Inconsistent Project Structure
- **Problem**: The file tree shows the bot's code inside `src/bot/`, whereas the `TODO.md` implies `bot/` and `src/` are separate, top-level directories for two distinct applications. The current structure incorrectly merges them.
- **Proposed Solution**: Restructure the project to have two distinct top-level directories: `backend/` (containing the `src/` for FastAPI) and `bot/` (for the Aiogram bot). This will enforce the separation between the two applications.

## 💻 Other Issues and Refinements

- **Inconsistent Response Formatting**: Responses are sometimes created with `TaskResponse.from_orm(task)` and sometimes constructed manually from a dictionary. This is inconsistent.
- **Redundant API Client Instantiation**: A new `ApiClient` is created for every single command in the bot. This should be managed centrally, for example, by creating it once or using middleware for injection.
- **Incomplete Bot Features**: Many bot commands are placeholders and do not have a full implementation.
- **Hardcoded API URL**: The bot's `ApiClient` uses a hardcoded `http://localhost:8000`. This should be configurable via an environment variable.

