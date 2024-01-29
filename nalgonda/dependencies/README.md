# Dependencies Directory

This directory is crucial for managing the external dependencies and service interfaces used throughout the project.
It contains:

- `auth.py`: Handles user authentication and authorization with OAuth2, including JWT token management.
- `dependencies.py`: Centralizes dependency injections for Redis, Agency, Agent, and Thread managers among others,
ensuring modularity and ease of use.
- `websocket_connection_manager.py`: Manages WebSocket connections enabling real-time communication in the application.
