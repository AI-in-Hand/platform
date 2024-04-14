# AI in Hand Platform

## Overview

AI in Hand Platform is an open-source web application designed for the orchestration and operational management of AI-driven swarm agencies. Leveraging [OpenAI Assistants API](https://platform.openai.com/docs/assistants/overview), it enriches the capabilities of the AI agents with specialized skills and a robust management system. Built on a FastAPI framework and employing Firebase Firestore along with OpenAI's GPT models, it enables dynamic agency and agent management at scale.

## Key Components

- **Configuration Managers**: Centralized management of configurations for agencies, agents, and individual skills.
- **WebSocket Connection Manager**: Ensures real-time interactive communication between agencies and clients through WebSocket connections.
- **Custom Skills**: A suite of specialized skills including `SearchWeb`, `GenerateProposal`, `BuildDirectoryTree`, among others, designed to augment the functionalities of the AI agents.
- **FastAPI Web Server**: Manages API routing, initializes CORS middleware, sets up Firebase, and facilitates WebSocket communication.
- **Data Models**: Utilizes Pydantic models for defining and validating configurations of agencies, agents, skills, as well as the structure of request data.
- **Repositories**: Utilizes Firestore for robust storage and querying capabilities for skill, agent, and agency configurations -- ensuring a seamless persistence layer.
- **Caching**: Employs Redis for efficient and scalable caching of agency states (sessions) for optimized performance.

## Features

- **Skill Configuration**: Offers extensive flexibility in managing skills with specific codes and parameters for varied tasks.
- **Agent Configuration**: Allows detailed setup of agents with specialized knowledge areas and skillsets.
- **Agency Configuration**: Facilitates the creation and management of agencies composed of configured agents.
- **Skill Execution**: Executes skills within an established framework for accomplishing a wide range of tasks.
- **User Management**: User access management features for interaction with different agencies.
- **API and WebSocket Routers**: Lays down a comprehensive set of API endpoints and WebSocket routes for external interactions and real-time communications.
- **Security**: Basic implementation of Firebase Auth for user authentication with plans for further enhancements.

## Installation

Follow these steps for setting up the environment and running the AI in Hand Platform locally:

1. Ensure Python 3.11+ and Node.js 20.10+ are installed.
2. Install Python dependencies either from `requirements.txt` or using Poetry.
3. Configure environment variables in ".env", taking ".env.testing" as a reference point (used only for local development).
4. To set up the frontend:
   - For local development: `npm install && npm run start`
   - For production: `npm install -g gatsby-cli && npm install --global yarn && yarn install && yarn build` (builds to backend/ui/ directory to be served by FastAPI)

### Running the Application

Start the FastAPI server with: `uvicorn backend.main:app --reload`

## Deployment to Heroku

1. Update `requirements.txt` with `poetry export --without dev --without-hashes > requirements.txt`.
All further steps are unnecessary if you are using GitHub Actions for deployment.
2. Log in to Heroku with `heroku login`.
3. Set up Heroku remote: `heroku git:remote -a ainhand`.
4. Deploy: `git push heroku main`.
5. Scale up: `heroku ps:scale web=1`.
6. View logs: `heroku logs --tail`.

## Usage

### API Endpoints

The provided Postman collection encompasses all the necessary routes and variables, facilitating extensive testing and interaction with the platform.

### WebSocket Communication

Outlines the process for establishing WebSocket connections (`/ws/{user_id}/{agency_id}/{session_id}`) for real-time interactions.

## Contributing

We welcome contributions from the open-source community! If you'd like to contribute to the AI in Hand Platform, please follow these steps:

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes and commit them with descriptive commit messages
4. Push your changes to your forked repository
5. Submit a pull request to the main repository

Please ensure that your code adheres to the project's coding standards and includes appropriate tests.

## Areas for Improvement

Enhance exception handling, security measures, documentation quality (e.g. docstrings), testing robustness.

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

Please note that this is an open-source project and is currently in active development. While we strive to maintain a high level of quality, there may be bugs or issues present. Use at your own risk.
