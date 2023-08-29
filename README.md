# KT_Generator

Repository of the code base for KT Generation process that we worked at LifeSight, Google Cloud and Searce GenAI Hackathon.

## Repo structure

- Code
- Presentation
- Readme.md

## Prereqs
1. ffmpeg
2. poetry

## Setup

1. Copy `Code/KT Generator/.env.sample` to `Code/KT Generator/.env` and fill in the values.
2. create a file `kt_gen3` in the root directory.
3. Create a folder called `test` in the root directory and add the codebase you wish to test in it.
4. Edit the `required_nodes` with the required functions/classes. 
    a. Class format = `class_name`
    b. Function format = `class_name.function_name`
5. Install deps with `$ poetry install`
6. Add poe as a poetry plugin `$ poetry self add 'poethepoet[poetry_plugin]'`
7. Run tests with `$ poetry poe test`
8. Lint with `$ poetry poe lint`
9. Run a local build with `$ poetry poe all`

*Note: This is a happy path, so if any errors, report*

## Run

1. `$ poetry poe run`

## Notes
1. Default model is `gpt-4`. Pass the required model to service configuration to change.

### Code

This folder contains the code base for the KT Generation process.

- KT Generator
    - `CodeParser.py`: This file contains the code to parse the code base and chunk it into logical code blocks (chunks).
    - `CarbonSnippets.py`: This file generates the `carbon.now` snippets for the code blocks.
    - `ResponseGenerator.py`: This file generates the explaination and the code summary using Llamaindex and PaLM LLM.
    - `DIDVideoGenerator.py`: This file generates the DID video avatar using the code explainations for all the chunks.
    - `CreateVideo.py`: This file stitches the final video using the videos and the code snippets and the summary.
    - `main.py`: This file is the main file that runs the entire process.
