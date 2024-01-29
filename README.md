# Project Nalgonda

## Overview

Project Nalgonda is an advanced platform designed for the orchestration and operational management of AI-driven swarm agencies. Leveraging [OpenAI Assistants API](https://platform.openai.com/docs/assistants/overview), it enriches the capabilities of the AI agencies with specialized tools and a robust management system. Built on a solid FastAPI framework and employing Firebase Firestore along with OpenAI's GPT models, it enables dynamic agency and agent management at scale.

## Key Components

- **Configuration Managers**: Centralized management of configurations for agencies, agents, and individual tools.
- **WebSocket Connection Manager**: Ensures real-time interactive communication between agencies and clients through WebSocket connections.
- **Custom Tools**: A suite of specialized tools including `SearchWeb`, `GenerateProposal`, `BuildDirectoryTree`, among others, designed to augment the functionalities of the AI agents.
- **FastAPI Web Server**: Manages API routing, initializes CORS middleware, sets up Firebase, and facilitates WebSocket communication.
- **Data Models**: Utilizes Pydantic models for defining and validating configurations of agencies, agents, tools, as well as the structure of request data.
- **Repositories**: Utilizes Firestore for robust storage and querying capabilities for tool, agent, and agency configurations -- ensuring a seamless persistence layer.
- **Caching**: Employs Redis for efficient and scalable caching of agency states (sessions) for optimized performance.

## Features

- **Tool Configuration**: Offers extensive flexibility in customizing tools with specific codes and parameters for varied tasks.
- **Agent Configuration**: Allows detailed setup of agents with specialized knowledge areas and toolsets.
- **Agency Configuration**: Facilitates the creation and management of agencies composed of configured agents.
- **Tool Execution**: Executes tools within an established framework for accomplishing a wide range of tasks.
- **User Management**: User access management features for interaction with different agencies.
- **API and WebSocket Routers**: Lays down a comprehensive set of API endpoints and WebSocket routes for external interactions and real-time communications.
- **Security**: Basic implementation of JWT for user authentication and authorization with plans for further enhancements.

## Installation

Follow these steps for setting up the environment and running the Nalgonda project locally:

1. Ensure Python 3.11+ and Node.js 20.10+ are installed.
2. Install Python dependencies either from `requirements.txt` or using Poetry.
3. Configure environment variables in ".env", taking ".env.testing" as a reference point (used only for local development).
4. To set up the frontend:
   - For local development: `npm install && npm run start`
   - For production: `npm install -g gatsby-cli && npm install --global yarn && yarn install && yarn build` (builds to nalgonda/ui/ directory to be served by FastAPI)

### Running the Application
Start the FastAPI server with: `uvicorn nalgonda.main:app --reload`

## Deployment to Heroku

1. Update `requirements.txt` with `poetry export --without dev --without-hashes > requirements.txt`.
2. Log in to Heroku with `heroku login`.
3. Set up Heroku remote: `heroku git:remote -a ainhand`.
4. Deploy: `git push heroku main`.
5. Scale up: `heroku ps:scale web=1`.
6. View logs: `heroku logs --tail`.

## Usage

### API Endpoints
The provided Postman collection encompasses all the necessary routes and variables, facilitating extensive testing and interaction with the platform.

### WebSocket Communication
Outlines the process for establishing WebSocket connections (`/v1/ws/{agency_id}/{session_id}`) for real-time interactions.

## Areas for Improvement
Enhance exception handling, security measures, documentation quality (e.g. docstrings), testing robustness.
