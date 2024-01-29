# Services Directory

This directory contains critical components that constitute the backend services of the Nalgonda project.
These services enable various functionalities from managing entities like agencies and agents to handling caching,
WebSocket connections, and threading.

## Services and Descriptions

- **Agency Manager**: Manages agencies and their configurations, including retrieval, update, and caching of agency information.

- **Agent Manager**: Manages agents including creating, updating, and retrieving agent information.

- **Cache Manager**: Defines an abstract base for cache management operations.

- **Redis Cache Manager**: Implements cache management using Redis as the backend.

- **Thread Manager**: Manages communication threads between agents within an agency, enabling threaded interactions.

- **Tool Service**: Provides tool description generation using GPT-3.

- **WebSocket Manager**: Manages WebSocket connections between the frontend and backend.
