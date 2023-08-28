# %%
from pathlib import Path
from CarbonSnippets import *
from CodeParser import *
from CreateVideo import *
from DIDVideoGenerator import *
from ResponseGenerator import *
import ast
from open_ai_client import (
    OpenAIClient,
    METHOD_EXPLAINATION_PROMPT,
    CLASS_EXPLAINATION_PROMPT,
)

from loguru import logger

import os
from dotenv import load_dotenv


load_dotenv()  # take environment variables from .env.

open_ai_client = OpenAIClient()

# UTIL Methods Start


def get_method_name(method_declaration):
    # Parse the method declaration using the ast module
    parsed_ast = ast.parse(method_declaration)

    # Find the first function definition node in the parsed AST
    for node in ast.walk(parsed_ast):
        if isinstance(node, ast.FunctionDef):
            return node.name

    return None


# UTIL Methods End


save_path = "./kt_gen3"
avatar_image_url = (
    "https://create-images-results.d-id.com/DefaultPresenters/William_m/thumbnail.jpeg"
)
test_directory = "./test"
source_file = "source.txt"

logger.info("Starting the processing...")

codeparser = code_parser()

all_classes = {}


def process_file(directory_path, file_path, output_file):
    with open(file_path, "r") as f:
        content = f.read()

        # Only analyze Python files
        if file_path.endswith(".py"):
            # Remove the root directory and '.py' extension to form the module name
            module_name = os.path.relpath(file_path, directory_path)[:-3].replace(
                os.path.sep, "."
            )
            class_info = codeparser.extract_elements(content, module_name)

            # Merge the newly found classes into the global dictionary
            all_classes.update(class_info)

        output_file.write(content)
        output_file.write("\n\n")


def walk_directory(dir_path, output_file_path):
    with open(output_file_path, "w") as output_file:
        for root, dirs, files in os.walk(dir_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                if os.path.isfile(file_path):
                    print(f"Processing file: {file_path}")
                    process_file(dir_path, file_path, output_file)


walk_directory(test_directory, source_file)

with open(source_file, "r") as f:
    source = f.read()

# codeparser = code_parser()
# extracted_elements = codeparser.extract_elements(source)

logger.info("Code parsing completed...")

with open("object.py", "w") as f:
    f.write(str(all_classes))

selected_elements = ["DIDVideoGeneration" , "DIDVideoGeneration.download_video"]
method_elements = []
for i in selected_elements:
    method_elements.append(all_classes[i]["body"])

# %%
# Generate carbon snippets
elements_for_images = method_elements
generate_carbon_snippets(elements_for_images, save_path)

video_scripts = []

# generate class script
class_prompt = CLASS_EXPLAINATION_PROMPT.format(
    context_code=source, class_name="InteractiveSpecificationTask"
)
class_script = open_ai_client.create_chat(class_prompt)
video_scripts.append(class_script)
logger.info(class_script)

# generate method scripts
for element in method_elements:
    open_ai_client.reset_history()
    method_name = get_method_name(element)
    logger.info(method_name)
    method_prompt = METHOD_EXPLAINATION_PROMPT.format(
        context_code=source, method_name=method_name
    )
    method_script = open_ai_client.create_chat(method_prompt)
    video_scripts.append(method_script)
    logger.info(method_script)

# %%
# Generate video
video_processor = DIDVideoGeneration(source_url=avatar_image_url)

# video_processor.process_chunk(summary, "summaries", save_path)
for index, chunk in enumerate(video_scripts):
    logger.info(f"Chunk {index} video generation started...")
    video_processor.process_chunk(chunk, index, save_path)
    logger.info(f"Chunk {index} video generation completed...")

# %%
# Stitch videos and images together
video_paths = [os.path.join(save_path, f"chunk_{i}.mp4") for i in range(
    len(elements_for_images))]
image_paths = [os.path.join(save_path, f"image_{i}.png") for i in range(
    len(elements_for_images))]
stitch_video(save_path, video_paths, image_paths)
