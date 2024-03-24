# Custom Skills Directory

This directory contains a collection of custom skills developed to extend the functionalities of the AI in Hand Platform.
Each skill performs a specific task and can be called upon when needed.

## Skills and Descriptions

- **Build Directory Tree**: Prints the structure of directories and files within a specified directory
while preventing directory traversal.

- **Generate Proposal**: Generates a proposal for a project based on a project brief.
Uses a GPT model to generate text based on input.

- **Print File Contents**: Prints the contents of a specific file, preventing directory traversal.

- **Save Lead to Airtable**: Saves new lead information to Airtable, including name, email, and lead details.

- **Search Web**: Performs a web search and returns the results. It uses the `duckduckgo_search` library.

- **Summarize Code**: Summarizes the code of a specified file using GPT-3.
It relies on the `PrintFileContents` skill to access the code text.

- **Utils**: Contains utility functions including directory traversal checks.

- **Write and Save Program**: Writes and saves files that represent a program/application
to the disk based on specified parameters.
