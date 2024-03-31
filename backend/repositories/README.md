# Repositories Directory

This directory is responsible for all persistent storage interactions within the AI in Hand Platform,
particularly with Firestore. It contains implementations for storing, retrieving, and managing configurations
and data for agencies, agents, skills, etc.

## Files and Descriptions

- **AgencyConfigFirestoreStorage.py**: Manages the persistence of agency configurations in Firestore,
providing methods to load and save these configurations based on owner or agency IDs.

- **AgentFlowSpecFirestoreStorage.py**: Similar to its agency counterpart, this file handles the persistence
of agent configurations, offering functionalities to load and save agent data.

- **SkillConfigFirestoreStorage.py**: Facilitates storing and retrieving skill configurations in Firestore.
This includes handling skill data validation and manipulation.

- **UserRepository.py**: Manages user data within Firestore, including functions to retrieve and update user records.
This setup reinforces the project's data integrity and provides a seamless integration with Firebase's Firestore
for its storage needs.
