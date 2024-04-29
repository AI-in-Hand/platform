# AI in Hand Platform
[![Actions Status](https://github.com/AI-in-Hand/platform/workflows/Test/badge.svg)](https://github.com/AI-in-Hand/platform/actions)
[![codecov](https://codecov.io/gh/AI-in-Hand/platform/graph/badge.svg?token=D2ZCM1DK55)](https://codecov.io/gh/AI-in-Hand/platform)

AI in Hand Platform is an open-source API and web application for managing LLM-driven multi-agent workflows.
Building on OpenAI's Assistants API, it offers a collaborative environment for developing, testing, and deploying AI teams.
The platform is built using FastAPI and draws inspiration from two open-source projects:
[Agency-Swarm by VRSEN](https://github.com/VRSEN/agency-swarm) for useful backend abstractions,
and [AutoGen Studio UI by Microsoft](https://github.com/microsoft/autogen/tree/main/samples/apps/autogen-studio/frontend)
for UI layout and customizable components.

## Key Features

- **Configuration Management**: Centrally manage configurations for agencies, agents, and skills.
- **Custom Skills**: Extend AI agents with specialized skills.
- **Persistence and Caching**: Use Firestore for configuration persistence.
- **API and WebSocket**: Interact with the platform through API endpoints and WebSocket for real-time communication.
- **Security**: Authenticate users with Firebase Authentication and encrypt user variables.

## Deployed Version

A deployed version of the AI in Hand Platform is always available at [https://platform.ainhand.com](https://platform.ainhand.com).
Feel free to explore and interact with the platform without setting it up locally.

## Getting Started

To set up the AI in Hand Platform locally, follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/AI-in-Hand/platform.git
   ```

2. Set up the backend:
   - Go to the `backend` directory.
   - Install the required dependencies:
     ```bash
     pip install -r requirements.txt
     ```
     or, for development purposes:
     ```bash
     poetry install
     ```
   - Set up the necessary environment variables (see `.env.testing`, rename it to `.env`).
   - Run the application:
     ```bash
     uvicorn main:app --reload
     ```
   - The backend API will be accessible at `http://localhost:8000`.

3. Set up the frontend:
   - Go to the `frontend` directory.
   - Install the necessary dependencies:
     ```bash
     npm install
     ```
   - Set up the environment variables (see `.env.default`, rename it to `.env.development`).
   - Set up Firebase Authentication and Firestore and update the frontend/src/firebase/firebaseConfig.json file with your Firebase project configuration.
   - Start the development server:
     ```bash
     yarn start
     ```
   - The frontend application will be accessible at `http://localhost:3000`.

For more details on running and developing the backend and frontend, refer to their respective README files:
- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)

## Backend

The backend of the AI in Hand Platform is built using FastAPI and provides various functionalities,
including managing agencies, agents, skills, sessions, and user variables.
It integrates with Google Firestore database for persistence of agency configurations.

For detailed information on the backend, including project structure, API documentation, custom skills,
and contributing guidelines, please refer to the [Backend README](backend/README.md).

## Frontend

The frontend of the AI in Hand Platform is built using React and provides a user-friendly interface for interacting
with the platform. It leverages Gatsby for fast setup and rich configurations, TailwindCSS for styling,
and Ant Design for UI components.

For detailed information on the frontend, including running the UI in dev mode, codebase overview, design elements,
modifying the UI, adding pages, and connecting to the backend, please refer to the [Frontend README](frontend/README.md).

## Contributing

We welcome contributions from the community to improve the AI in Hand Platform. To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your forked repository.
5. Submit a pull request to the main repository.

Please ensure your code follows the project's coding standards and includes tests for any new functionality.

## License
The core AI in Hand Platform is licensed under the [Affero General Public License (AGPL)](LICENSE), promoting community-driven improvements under the same license for an open and collaborative development atmosphere.

**User-Generated Content (UGC):**
- **Python Skills**: Python code for AI agent skills will be contributed to the source code repository under the AGPL after a security review, as these skills are executed server-side.
- **AI Assistant and Team Configurations and Other User Data**: Configurations and user data remain the property of the users, unless voluntarily made public. This preserves users' proprietary rights while utilizing the platform's open-source features.

## Disclaimer

This is an open-source project under active development.
While we strive for quality, there may be bugs or issues. Use at your own risk.

If you have any questions or need assistance, feel free to reach out to our team through our website widget
or by creating an issue or discussion in this repository.
Happy coding!
