# Project Nalgonda

## Overview

... Project description ...

## Features

- **Agency Configuration**: Configure agencies with agents
- **Tool Configuration**: Configure tools with custom parameters
- **Tool Execution**: Execute tools and returns results
- **Agent Configuration**: Configure agents with their knowledge and tools
- **User Management**: Manage users and their access to different agencies [TODO]

## Getting Started

### Prerequisites

- Python 3.11 or higher
- FastAPI
- Uvicorn (for running the server)
- Additional Python packages as listed in `pyproject.toml`

### Installation

1. **Clone the Repository**

   ```sh
   git clone https://github.com/bonk1t/nalgonda.git
   cd nalgonda
   ```

2. **Install Dependencies**

   Using poetry:

   ```sh
   poetry install
   ```

   Or using pip:

   ```sh
   pip install -r requirements.txt
   ```

3. **Set up Environment Variables**

   Ensure to set up the necessary environment variables such as `OPENAI_API_KEY`.

### Running the Application

1. **Start the FastAPI Server**

   ```sh
   uvicorn backend.main:app --reload
   ```

   The API will be available at `http://localhost:8000`.

2. **Accessing the Endpoints**

   Use a tool like Postman or Swagger UI to interact with the API endpoints.

## Usage

### API Endpoints
Send a POST request to the /create_agency endpoint to create an agency. The request body should contain the following fields:
- agency_id: The ID of the agency

### WebSocket Endpoints
After creating an agency, you can connect to the WebSocket endpoint at /ws/{agency_id} to communicate with the agency.
