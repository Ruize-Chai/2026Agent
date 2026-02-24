# Oriflow Agent

A Python-based workflow engine with a FastAPI backend, featuring a plugin-based skill system, DAG (Directed Acyclic Graph) workflow execution, and a user authentication system.

## Features

- **Workflow Engine**: Execute workflows defined as DAGs with multiple interconnected nodes
- **Plugin System**: Extensible skill-based architecture for custom node implementations
- **User Authentication**: Secure user registration and login with SHA-256 password hashing
- **JSON Schema Validation**: Built-in validation for workflow and skill configurations
- **Comprehensive Logging**: Multi-level logging with colored console output and file persistence
- **Error Recovery**: Built-in error handling with retry mechanisms and recovery strategies

## Project Structure

```
Oriflow-Agent/
├── main.py                 # FastAPI application entry point
├── Front/                  # Frontend components
│   ├── login.html          # Login page
│   ├── register.html       # Registration page
│   ├── login.py            # Login verification logic
│   ├── register.py         # User registration logic
│   ├── userlist.json       # User data storage
│   └── HTTPLists.md        # API endpoint documentation
├── core/                   # Core engine components
│   ├── workflow/           # Workflow management
│   │   ├── Workflow.py     # Workflow class with DAG execution
│   │   └── workflow_schema.json  # Workflow JSON schema
│   ├── skill/              # Skill (node) system
│   │   ├── Skill.py        # Abstract base skill class
│   │   ├── Skill_search.py # Plugin loader
│   │   └── plugin_manifest_schema.json  # Skill schema
│   ├── json_util/          # JSON utilities
│   │   ├── json_utils_confirm.py  # Schema validation
│   │   ├── json_utils_seq.py      # Serialization/deserialization
│   │   └── json_utils_write.py    # File I/O operations
│   └── logging/            # Logging system
│       ├── logging.py      # Logger with colored output
│       └── error_lists.json  # Error code definitions
└── plugins/                # Plugin directory (for custom skills)
```

## Installation

### Prerequisites

- Python 3.10+
- pip (Python package manager)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Ruize-Chai/Oriflow-Agent.git
   cd Oriflow-Agent
   ```

2. Install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic jsonschema
   ```

3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

4. Open your browser and navigate to:
   - Registration: `http://localhost:8000/`
   - Login: `http://localhost:8000/login`
   - Health Check: `http://localhost:8000/health`

## API Endpoints

| Method | Endpoint    | Description                          |
|--------|-------------|--------------------------------------|
| GET    | `/`         | Serves the registration page         |
| GET    | `/login`    | Serves the login page                |
| GET    | `/health`   | Health check endpoint                |
| POST   | `/register` | Register a new user                  |
| POST   | `/login`    | Authenticate an existing user        |

### Request Payloads

**Register Payload:**
```json
{
  "username": "string (1-64 chars)",
  "password": "string (6-128 chars)"
}
```

**Login Payload:**
```json
{
  "username": "string (1-64 chars)",
  "password": "string (1-128 chars)"
}
```

## Core Components

### Workflow Engine

The workflow engine executes DAG-based workflows. Each workflow contains:

- **workflow_id**: Unique identifier for the workflow
- **entry**: Starting node ID
- **nodes**: Array of node definitions
- **meta**: Optional metadata

Example workflow structure:
```json
{
  "workflow_id": "example_workflow",
  "entry": 1,
  "nodes": [
    {
      "id": 1,
      "type": "skill_name",
      "inputs": [],
      "outputs": [2, null],
      "params": {}
    },
    {
      "id": 2,
      "type": "another_skill",
      "inputs": [1],
      "outputs": [null],
      "params": {}
    }
  ]
}
```

### Skill System

Skills are the building blocks of workflows. Each skill:

- Extends the abstract `Skill` base class
- Implements the `execute(context)` method
- Returns the next node ID or `None` to end execution

To create a custom skill:

```python
from core.skill.Skill import Skill
from typing import Any, Dict

class Self_skill(Skill):
    def execute(self, context: Dict[str, Any]) -> int | None:
        # Your skill logic here
        return self.outputs[0]  # Return next node ID or None
```

Place your skill in `plugins/<skill_name>/__init__.py` with the class named `Self_skill`.

### Logging System

The logging module provides:

- **Error Levels**: FATAL, CRITICAL, ERROR, RETRY, WARN, INFO, DEBUG, IGNORE
- **Colored Console Output**: Cross-platform support (Windows, macOS, Linux)
- **File Logging**: JSON-formatted log entries
- **Error Recovery**: Automatic retry mechanisms with configurable strategies

```python
from core.logging.logging import get_logger

logger = get_logger()
logger.info("Operation completed")
logger.warning("Low disk space")
logger.error("Failed to connect", code="3001")
```

### JSON Utilities

The JSON utility modules provide:

- **Schema Validation**: Validate workflow and skill data against JSON schemas
- **Serialization**: Pack/unpack JSON with optional validation
- **File Operations**: Read/write JSON files with automatic directory creation

```python
from core.json_util.json_utils_write import read_workflow_file, write_workflow_file

# Read a workflow file with validation
workflow_data = read_workflow_file("path/to/workflow.json")

# Write a workflow file with validation
write_workflow_file(workflow_data, "path/to/output.json")
```

## Security

- Passwords are hashed using SHA-256 (consider upgrading to bcrypt/argon2 for production)
- Usernames are case-insensitive and trimmed
- Input validation through Pydantic models
- JSON schema validation for workflow and skill configurations

## Development

### Running Tests

```bash
# Run the application in development mode
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Project Dependencies

- **FastAPI**: Web framework for building APIs
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation using Python type annotations
- **jsonschema**: JSON Schema validation library (optional)

## License

This project is under development.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
