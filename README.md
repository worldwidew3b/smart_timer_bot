# Smart Timer Bot

An intelligent Todo List with time tracking, tags, priorities, and detailed statistics similar to Steam's clock system.

## Features

- **Task Management**: Create, update, delete, and organize tasks
- **Time Tracking**: Start/stop timers for tasks with automatic duration calculation
- **Tagging System**: Organize tasks with customizable tags
- **Prioritization**: Set priority levels (1-5) for tasks
- **Statistics**: Detailed analytics on time spent, completed tasks, and productivity trends
- **Filtering**: Search and filter tasks by various criteria
- **Telegram Integration**: Full-featured bot interface

## Architecture

### Backend (FastAPI + PostgreSQL)
- RESTful API with async support
- SQLAlchemy ORM with async support
- Repository pattern for data access
- Pydantic models for request/response validation

### Frontend (Telegram Bot - Aiogram)
- Interactive bot interface
- FSM for complex workflows
- Inline keyboards for easy navigation
- Real-time updates

## Installation

### Prerequisites
- Python 3.11+
- PostgreSQL
- Docker (optional, for containerized deployment)

### Local Development

1. Clone the repository:
```bash
git clone <repository-url>
cd smart-timer-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Set up the database:
```bash
alembic upgrade head
```

6. Run the backend:
```bash
uvicorn src.main:app --reload
```

7. Run the bot:
```bash
python bot_runner.py
```

### Docker Deployment

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

## API Endpoints

### Tasks
- `GET /api/tasks` - Get all tasks with optional filtering
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{id}` - Get a specific task
- `PUT /api/tasks/{id}` - Update a task
- `DELETE /api/tasks/{id}` - Delete a task

### Tags
- `GET /api/tags` - Get all tags for user
- `POST /api/tags` - Create a new tag

### Timer
- `POST /api/timer/start` - Start a timer for a task
- `POST /api/timer/stop` - Stop a timer session
- `GET /api/timer/active` - Get active timer for user

### Statistics
- `GET /api/stats/daily` - Get daily statistics
- `GET /api/stats/weekly` - Get weekly statistics
- `GET /api/stats/tags` - Get statistics by tags
- `GET /api/stats/trends` - Get productivity trends

## Bot Commands

- `/start` - Show welcome message
- `/help` - Show help information
- `/newtask` - Create a new task
- `/mytasks` - List all tasks
- `/starttimer <task_id>` - Start timer for a task
- `/stoptimer` - Stop current timer
- `/current` - Show current task
- `/stats` - Show statistics menu
- `/statstoday` - Show today's statistics
- `/statsweek` - Show weekly statistics
- `/search` - Search tasks with filters

## Environment Variables

- `DATABASE_URL` - PostgreSQL connection string
- `TELEGRAM_BOT_TOKEN` - Telegram bot token
- `DEBUG` - Enable/disable debug mode

## Project Structure

```
smart_timer_bot/
├── src/                    # Backend source code
│   ├── api/               # API routes
│   ├── core/              # Configuration and database setup
│   ├── domain/            # Business logic and models
│   ├── infrastructure/    # Database models and repositories
│   └── main.py            # Application entry point
├── bot/                   # Telegram bot source code
│   ├── handlers/          # Message handlers
│   ├── keyboards/         # Keyboard builders
│   ├── services/          # Service classes
│   ├── utils/             # Utility functions
│   └── models/            # Data models
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── alembic.ini            # Database migration configuration
└── README.md              # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.