import os
import logging
from .llm_adapter import LLMAdapter
from .prompts import JCL_TO_AIRFLOW_PROMPT
from .validator import CodeValidator

class JCLEngine:
    def __init__(self, adapter: LLMAdapter):
        self.adapter = adapter

    def translate_jcl(self, input_filepath: str, output_filepath: str):
        if not os.path.exists(input_filepath):
            raise FileNotFoundError(f"Input file not found: {input_filepath}")

        with open(input_filepath, "r") as f:
            jcl_code = f.read()

        logging.info(f"Read JCL file: {input_filepath}")

        prompt = JCL_TO_AIRFLOW_PROMPT.format(jcl_code=jcl_code)
        
        logging.info("Generating Apache Airflow DAG...")
        airflow_code = self.adapter.generate_code(prompt)
        
        is_valid, error_msg = CodeValidator.is_valid_python(airflow_code)
        if not is_valid:
            logging.warning(f"Validation error in generated Airflow DAG: {error_msg}")

        with open(output_filepath, "w") as f:
            f.write(airflow_code)
        
        logging.info(f"Generated Airflow DAG saved to {output_filepath}")
