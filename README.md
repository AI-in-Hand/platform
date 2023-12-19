# Project Nalgonda

## Overview

Project Nalgonda is an innovative platform for managing and executing AI-driven swarm agencies.
It is built upon the foundational [OpenAI Assistants API](https://platform.openai.com/docs/assistants/overview)
and extends its functionality through a suite of specialized tools and a sophisticated management system for AI agencies.

## Key Components

- **Agency Configuration Manager**: Manages configurations for AI agencies, ensuring they're loaded and saved properly.
- **WebSocket Connection Manager**: Handles real-time WebSocket connections for interactive agency-client communication.
- **Custom Tools**: A collection of tools including `SearchWeb`, `GenerateProposal`, `BuildDirectoryTree`, and more,
providing specialized functionalities tailored to the needs of different agency roles.
- **Data Persistence**: Utilizes JSON-based configurations to maintain agency states and preferences across sessions.

## Features

- **Agency Configuration**: Configure agencies with agents
- **Tool Configuration**: Configure tools with custom parameters
- **Tool Execution**: Execute tools and return results
- **Agent Configuration**: Configure agents with their knowledge and tools
- **User Management**: Manage users and their access to different agencies [TODO]

## Installation

Ensure you have Python 3.11 or higher and follow these steps to get started:

1. Install the required dependencies (from `requirements.txt` or using Poetry).
2. Set up the necessary environment variables, including `OPENAI_API_KEY`.
3. Use the provided JSON configuration files as templates to configure your own AI agencies.
4. Start the FastAPI server (`uvicorn nalgonda.main:app --reload`) to interact with the system.

Note: Refer to individual class and method docstrings for detailed instructions and usage.

## Deployment to Heroku

Follow these steps to deploy the app to Heroku:
1. `poetry export -o requirements.txt --without dev --without-hashes` - update `requirements.txt`
2. `heroku login`- log in to Heroku
3. `heroku git:remote -a ainhand` - set up Heroku remote
4. `git push heroku main` - deploy to Heroku
5. `heroku ps:scale web=1` - scale up the app
6. `heroku logs --tail` - view logs

## Usage

### API Endpoints

Send POST requests to endpoints such as `POST /v1/api/agency` and `POST /v1/api/agency/message` to perform operations
like creating new agencies and sending messages to them.

### WebSocket Communication

Connect to WebSocket endpoints (e.g., `/v1/ws/{agency_id}`, `/v1/ws/{agency_id}/{thread_id}`)
to engage in real-time communication with configured AI agencies.
