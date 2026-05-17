import os
import logging
import re
from .llm_adapter import LLMAdapter
from .prompts import (
    COBOL_TO_OOP_PYTHON_PROMPT, TEST_GENERATION_PROMPT, 
    SELF_HEALING_PROMPT, TRACEABILITY_PROMPT, SECURITY_UPGRADE_PROMPT
)
from .validator import CodeValidator
from .sandbox import Sandbox
from .auditor import Auditor
from .chunking_engine import ChunkingEngine
from .cost_estimator import CostEstimator
from .dependency_resolver import DependencyResolver

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

class TranslationEngine:
    def __init__(self, adapter: LLMAdapter, max_retries: int = 3):
        self.adapter = adapter
        self.max_retries = max_retries

    def translate_file(self, input_filepath: str, output_filepath: str):
        if not os.path.exists(input_filepath):
            raise FileNotFoundError(f"Input file not found: {input_filepath}")

        with open(input_filepath, "r") as f:
            cobol_code = f.read()

        logging.info(f"Read COBOL file: {input_filepath} ({len(cobol_code)} chars)")

        # Feature: Generate ROI Dashboard
        dashboard_filepath = os.path.join(os.path.dirname(output_filepath), "roi_dashboard.html")
        CostEstimator.generate_roi_dashboard(cobol_code, dashboard_filepath)

        # Feature: Dependency Resolution
        resolver = DependencyResolver(self.adapter)
        resolver.resolve_dependencies(cobol_code, output_filepath)

        # Feature: AST Chunking
        # We chunk the file. For simplicity in this prototype, if it's multiple chunks, 
        # we would loop over them. Here we just take the first chunk for demonstration 
        # or process it all if it's small.
        chunks = ChunkingEngine.chunk_cobol_file(cobol_code)
        target_cobol = chunks[0] # Assume processing chunk 1 for prototype

        # Step 1: Generate Python Code (with DB2 to SQLAlchemy handling baked into prompt)
        logging.info("Generating Python code...")
        prompt = COBOL_TO_OOP_PYTHON_PROMPT.format(cobol_code=target_cobol)
        python_code = self.adapter.generate_code(prompt)
        
        # Feature: Security Posture Upgrading
        logging.info("Running Security Posture Upgrade scan...")
        security_prompt = SECURITY_UPGRADE_PROMPT.format(python_code=python_code)
        secured_python_code = self.adapter.generate_code(security_prompt)
        
        self._save_code(output_filepath, secured_python_code)

        # Step 2: Generate Tests
        logging.info("Generating Pytest suite...")
        module_name = os.path.splitext(os.path.basename(output_filepath))[0]
        test_filepath = os.path.join(os.path.dirname(output_filepath), f"test_{os.path.basename(output_filepath)}")
        
        test_prompt = TEST_GENERATION_PROMPT.format(
            python_module_name=module_name,
            cobol_code=target_cobol,
            python_code=secured_python_code
        )
        test_code = self.adapter.generate_code(test_prompt)
        self._save_code(test_filepath, test_code)

        # Step 3: The Self-Healing Execution Loop
        success = False
        for attempt in range(1, self.max_retries + 1):
            logging.info(f"Execution loop attempt {attempt}/{self.max_retries}...")
            
            loop_success, output = Sandbox.run_tests(test_filepath)
            
            if loop_success:
                logging.info("SUCCESS! All tests passed. The code is functionally verified.")
                success = True
                break
            else:
                logging.warning(f"Tests failed. Capturing traceback for self-healing...\n{output}")
                
                logging.info("Requesting LLM to self-heal the Python business logic...")
                heal_prompt = SELF_HEALING_PROMPT.format(
                    target_file=os.path.basename(output_filepath),
                    original_code=secured_python_code,
                    traceback=output
                )
                secured_python_code = self.adapter.generate_code(heal_prompt)
                self._save_code(output_filepath, secured_python_code)

        if not success:
            logging.warning(f"Failed to achieve a passing test suite after {self.max_retries} attempts.")

        # Step 4: Traceability Audit
        logging.info("Generating Audit Traceability Matrix...")
        audit_prompt = TRACEABILITY_PROMPT.format(
            cobol_code=target_cobol,
            python_code=secured_python_code
        )
        
        try:
            json_mapping_response = self.adapter.client.models.generate_content(
                model=self.adapter.model_name,
                contents=audit_prompt
            ).text
            
            # Strip markdown json blocks if present
            match = re.search(r"```json\n(.*?)\n```", json_mapping_response, re.DOTALL)
            json_mapping = match.group(1).strip() if match else json_mapping_response.strip()
                
            audit_filepath = os.path.join(os.path.dirname(output_filepath), "traceability_matrix.html")
            Auditor.generate_html_matrix(json_mapping, audit_filepath)
        except Exception as e:
            logging.error(f"Traceability audit failed to generate properly: {e}")

    def _save_code(self, filepath: str, code: str):
        is_valid, error_msg = CodeValidator.is_valid_python(code)
        if not is_valid:
            logging.warning(f"Code validation warning before saving {filepath}: {error_msg}")
        
        with open(filepath, "w") as f:
            f.write(code)
        logging.info(f"Saved: {filepath}")
