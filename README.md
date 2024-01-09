# Project Nalgonda

## Overview

Project Nalgonda is an innovative platform for managing and executing AI-driven swarm agencies.
Built upon the [OpenAI Assistants API](https://platform.openai.com/docs/assistants/overview),
it extends functionality through specialized tools and a sophisticated management system for AI agencies.
It combines robust FastAPI architecture, Firebase Firestore, and OpenAI's GPT models for dynamic agency
and agent management.

## Key Components

- **Agency Configuration Manager**: Manages configurations for AI agencies.
- **WebSocket Connection Manager**: Handles WebSocket connections for interactive agency-client communication.
- **Custom Tools**: Includes tools like `SearchWeb`, `GenerateProposal`, `BuildDirectoryTree`, and more.
- **Data Persistence**: Uses Firestore for storing tool, agent, and agency configurations.
- **FastAPI Web Server**: For API routing, CORS middleware, Firebase initialization, and WebSocket communication.
- **Data Models**: Pydantic models for agencies, agents, and tool configurations.
- **Caching**: Redis for efficient caching of agency states.

## Features

- **Tool Configuration**: Configure tools with code and parameters.
- **Agent Configuration**: Configure agents with knowledge and tools.
- **Agency Configuration**: Set up agencies with agents.
- **Tool Execution**: Execute tools for various tasks.
- **User Management**: Manage user access to different agencies [TODO].
- **API and WebSocket Routers**: Define API endpoints and WebSocket routes.
- **Security**: Basic implementations of JWT authentication and authorization [TBD].

## Installation

1. Ensure Python 3.11+ and Node.js (version above 14.15.0) are installed.
2. Install Python dependencies (from `requirements.txt` or using Poetry).
3. Set up environment variables in ".env", reference in ".env.testing".
   - Use `cat ~/ai-in-hand-firebase-adminsdk-....json | jq -c .` for Google Credentials.
4. In `frontend` directory, run:
   ```
   npm install -g gatsby-cli
   npm install --global yarn
   cd frontend
   yarn install
   yarn build
   ```

### Running the Application
Start the FastAPI server: `uvicorn nalgonda.main:app --reload`

## Deployment to Heroku

1. Update `requirements.txt` with `poetry export --without dev --without-hashes > requirements.txt`.
2. Log in to Heroku with `heroku login`.
3. Set up Heroku remote: `heroku git:remote -a ainhand`.
4. Deploy: `git push heroku main`.
5. Scale up: `heroku ps:scale web=1`.
6. View logs: `heroku logs --tail`.

## Usage

### API Endpoints
To interact with the platform, use the Postman collection, which includes all necessary routes and variables for testing.

### WebSocket Communication
Connect to WebSocket endpoints (`/v1/ws/{agency_id}`, `/v1/ws/{agency_id}/{thread_id}`)
for real-time communication with AI agencies.

## Key Components
- Agency Configuration Manager: Manages configurations for AI agencies.
- WebSocket Connection Manager: Handles WebSocket connections for interactive agency-client communication.
- Custom Tools: Includes tools like SearchWeb, GenerateProposal, BuildDirectoryTree, and more.
- Data Persistence: Uses JSON-based configurations and Firestore for maintaining agency states.
- FastAPI Web Server: For API routing, CORS middleware, Firebase initialization, and WebSocket communication.
- Data Models: Pydantic models for agencies, agents, and tool configurations.
- Caching: Redis for efficient configuration management.

## Areas for Improvement
- Enhanced exception handling, security, documentation, testing, caching logic, and database interactions.
