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
from datetime import datetime

load_dotenv()
open_ai_client = OpenAIClient()

save_path = "./kt_gen3"
avatar_image_url = (
    "https://create-images-results.d-id.com/DefaultPresenters/William_m/thumbnail.jpeg"
)

logger.info("Starting the processing...")

codeparser = CodeParser()
nodes = dict()

# -------------------------------


def process_file(directory_path, file_path, output_file, global_index):
    if file_path.endswith(".py"):

        with open(file_path, "r") as f:
            content = f.read()

            # Only analyze Python files

            # Remove the root directory and '.py' extension to form the module name
            module_name = os.path.relpath(file_path, directory_path)[:-3].replace(
                os.path.sep, "."
            )
            class_info = codeparser.extract_elements(content, module_name)

            # Merge the newly found classes into the global dictionary
            global_index.update(class_info)

            output_file.write(content)
            output_file.write("\n\n")


def walk_directory(dir_path, output_file_path, global_index):
    with open(output_file_path, "w") as output_file:
        for root, dirs, files in os.walk(dir_path):
            for filename in files:
                file_path = os.path.join(root, filename)
                if os.path.isfile(file_path):
                    print(f"Processing file: {file_path}")
                    process_file(dir_path, file_path,
                                 output_file, global_index)


def get_required_nodes(node_names, for_images=False):
    if for_images:
        logger.info("get required nodes for images")
    else:
        logger.info("get required nodes for script")

    output = []
    for name in node_names:
        node = nodes[name]
        node_info = {
            "name": name,
            "body": node["body"],
        }
        if "class_name" in node:
            node_info["class_name"] = node["class_name"]

        if name == "InteractiveSpecificationTask" and for_images:
            """
            Hardcoding the handling for InteractiveSpecificationTask
            as we want a specific image being generated for it.
            """
            node_info["body"] = """
class InteractiveSpecificationTask(Task):
    class Meta:
        proxy = True

    @classmethod
    def get_task_type(cls):
        return "InteractiveSpecification"

    def kick_off(self, bot: SlackBot):
        ...

    def handle_user_response(self, bot: SlackBot, user_input: str):
        ...

    def generate_story(self, bot: SlackBot):
        ...
            """

        output.append(node_info)
    return output


# generate class script
def create_class_script(
    classes, temperature=0.8, presence_penalty=0, frequency_penalty=0
):
    scripts = []
    for i in classes:
        # open_ai_client.reset_history()
        class_prompt = CLASS_EXPLAINATION_PROMPT.format(
            context_code=i["body"], class_name=i
        )
        class_script = open_ai_client.create_chat(
            class_prompt, temperature, presence_penalty, frequency_penalty
        )
        scripts.append(class_script)
        logger.info(class_script)
    return scripts


# generate method scripts
def create_method_script(
    methods, temperature=0.8, presence_penalty=0, frequency_penalty=0
):
    scripts = []
    for i in methods:
        # open_ai_client.reset_history()
        method_prompt = METHOD_EXPLAINATION_PROMPT.format(
            context_code=i["body"], method_name=i
        )
        method_script = open_ai_client.create_chat(
            method_prompt, temperature, presence_penalty, frequency_penalty
        )
        scripts.append(method_script)
        logger.info(method_script)
    return scripts


# Need to iteratively generate scripts for classes and methods.
def gen_scripts(classes, methods, temperature=0.8, presence_penalty=0, frequency_penalty=0, iterations=1):
    for k in range(iterations):
        logger.info(f"Iteration: {k}")
        scripts = []

        logger.info("Generating class scripts...")
        class_scripts = create_class_script(
            classes, temperature=temperature, presence_penalty=presence_penalty, frequency_penalty=frequency_penalty
        )

        logger.info("Generating method scripts...")
        method_scripts = create_method_script(
            methods, temperature=temperature,  presence_penalty=presence_penalty, frequency_penalty=frequency_penalty
        )

        scripts = class_scripts + method_scripts

        now = datetime.now()
        logger.info("Writing scripts to file...")
        with open(f"./scripts/scripts_{now}_{temperature}_{frequency_penalty}_{k}.py", "w") as f:
            f.write(str(scripts))


# --------------------------------

source_code_dir_path = os.getenv("SOURCE_CODE_PATH")
assert source_code_dir_path, "SOURCE_CODE_PATH is not set!"

code_dump_filepath = "source.txt"
walk_directory(source_code_dir_path, code_dump_filepath, nodes)
logger.info("Code parsing completed...")

# with open(code_dump_filepath, "r") as f:
#     source = f.read()

with open("object.py", "w") as f:
    f.write(str(nodes))

required_nodes = [
    "InteractiveSpecificationTask",
    "InteractiveSpecificationTask.kick_off",
    "InteractiveSpecificationTask.handle_user_response",
    "InteractiveSpecificationTask.generate_story"
]

nodes_for_images = get_required_nodes(required_nodes, for_images=True)
logger.info("Selected elements extraction completed...")
# logger.info(processed_nodes)

# %%
# Generate carbon snippets
elements_for_images = [x["body"] for x in nodes_for_images]
generate_carbon_snippets(elements_for_images, save_path)

nodes_for_script = get_required_nodes(required_nodes, for_images=False)
classes = [x for x in nodes_for_script if "class_name" not in x]
# logger.info(classes)
with open("class.py", "w") as f:
    f.write(str(classes))

methods = [x for x in nodes_for_script if "class_name" in x]
with open("method.py", "w") as f:
    f.write(str(classes))


scripts = gen_scripts(classes, methods, temperature=0.8,
                      presence_penalty=0.3, frequency_penalty=0.3, iterations=1)

# # %%
# # Generate video
# video_processor = DIDVideoGeneration(source_url=avatar_image_url)

# # video_processor.process_chunk(summary, "summaries", save_path)
# for index, chunk in enumerate(video_scripts):
#     logger.info(f"Chunk {index} video generation started...")
#     video_processor.process_chunk(chunk, index, save_path)
#     logger.info(f"Chunk {index} video generation completed...")

# # %%
# # Stitch videos and images together
# video_paths = [os.path.join(save_path, f"chunk_{i}.mp4") for i in range(
#     len(elements_for_images))]
# image_paths = [os.path.join(save_path, f"image_{i}.png") for i in range(
#     len(elements_for_images))]
# stitch_video(save_path, video_paths, image_paths)
