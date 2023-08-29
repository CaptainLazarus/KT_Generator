import ast
from loguru import logger


class CodeParser:
    def extract_elements(self, source: str, module_name: str) -> str:
        node = ast.parse(source)
        imports_block = []
        output = {}

        # AST helper method to get the source code for a given node
        def get_source_lines(start, end):
            return "".join(source.splitlines(True)[start - 1 : end])

        # Iterate through each node in the AST
        for n in ast.walk(node):
            # Check if the node represents an import statement
            if isinstance(n, (ast.Import, ast.ImportFrom)):
                logger.info("found import")
                # Extract the start and end line numbers
                start_line = n.lineno - 1
                end_line = n.lineno

                # Append the import statement to the imports_block string
                imports_block.append(source.splitlines(True)[start_line:end_line])
            if isinstance(n, ast.ClassDef):
                logger.info("Found Class")
                class_name = n.name
                class_start_line = n.lineno
                class_end_line = n.end_lineno

                # Get the code block for the entire class
                class_body = get_source_lines(class_start_line, class_end_line)

                # Look for method definitions within the class
                for sub_node in ast.iter_child_nodes(n):
                    if isinstance(sub_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_name = sub_node.name
                        method_start_line = sub_node.lineno
                        method_end_line = sub_node.end_lineno

                        # Get the code block for the method
                        method_body = get_source_lines(
                            method_start_line, method_end_line
                        )

                        output[class_name + "." + method_name] = {
                            "body" : method_body,
                            "class_name" : class_name
                        }
                output[class_name] = {
                    "body": class_body
                }

        return output

        # Prepend the imports block if there were any imports
        if imports_block:
            elements.insert(0, imports_block)

        return elements
