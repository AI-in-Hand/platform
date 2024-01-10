#!/bin/bash

# Build Frontend
cd frontend
npm install -g gatsby-cli
npm install --global yarn
yarn install
yarn build
cd ..

# Install Python dependencies
pip install -r requirements.txt
