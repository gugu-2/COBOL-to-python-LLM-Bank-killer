import os
import logging
import re
from .llm_adapter import LLMAdapter
from .prompts import DEPENDENCY_RESOLUTION_PROMPT

class DependencyResolver:
    def __init__(self, adapter: LLMAdapter):
        self.adapter = adapter

    def resolve_dependencies(self, cobol_code: str, output_filepath: str):
        # Extremely basic heuristic to see if there are even any external calls
        if "CALL " not in cobol_code and "EXEC SQL" not in cobol_code:
            logging.info("No external CALLs or SQL found. Skipping dependency resolution.")
            return

        logging.info("Analyzing COBOL dependencies for modern equivalents...")
        
        prompt = DEPENDENCY_RESOLUTION_PROMPT.format(cobol_code=cobol_code)
        requirements_list = self.adapter.generate_code(prompt)
        
        # Write the supplemental requirements file
        req_file = os.path.join(os.path.dirname(output_filepath), "requirements_supplemental.txt")
        
        with open(req_file, "w") as f:
            f.write(requirements_list)
            
        logging.info(f"Supplemental dependencies resolved and saved to {req_file}")
