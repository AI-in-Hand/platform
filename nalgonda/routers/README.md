# Routers Directory

This directory defines the API routing logic for the project, organizing routes into specific functionalities
and versions. Key components include:

- `__init__.py` & `v1/__init__.py`: Establish the application's routing logic, categorizing the APIs and handling errors.
- `agency.py`, `agent.py`, `auth.py`, `session.py`, `tool.py`: Define the endpoints for managing agencies, agents,
authentication, sessions, and tools, respectively.
- `websocket.py`: Sets up WebSocket endpoints for real-time messaging.

The Swagger documentation is available at `/v1/docs`.
