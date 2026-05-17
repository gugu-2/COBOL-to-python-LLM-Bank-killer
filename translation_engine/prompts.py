COBOL_TO_OOP_PYTHON_PROMPT = """You are an expert software engineer specializing in autonomous legacy codebase migration.
Your task is to translate the provided COBOL source code into modern, clean, Object-Oriented Python.

Follow these strict guidelines:
1. **Object-Oriented Architecture:** Refactor the procedural COBOL logic into a well-structured Object-Oriented Python script.
2. **Data Division to Dataclasses:** Convert COBOL records into Python `dataclasses`.
3. **Database Modernization (DB2/VSAM):** If the COBOL code contains `EXEC SQL` (DB2) or VSAM file reads, convert them to modern `SQLAlchemy` ORM queries. Assume a generic PostgreSQL database.
4. **Procedure Division to Methods:** Convert COBOL paragraphs into methods within a main orchestrator class.
5. **Main Execution:** Provide an `if __name__ == "__main__":` block.
6. **No Markdown or Explanations:** Output ONLY valid Python code.

Here is the COBOL code to translate:
{cobol_code}
"""

TEST_GENERATION_PROMPT = """You are an expert QA Engineer. 
I have translated a legacy COBOL program into the following Python code.
Your task is to write a comprehensive `pytest` test suite.

Guidelines:
1. Write tests using the `pytest` framework.
2. Mock any external file I/O or system calls (e.g. SQLAlchemy sessions).
3. Ensure you test the core business logic calculation.
4. Output ONLY valid Python code for the test file. No markdown, no explanations. 
5. Assume the translated Python code will be saved in a file named `{python_module_name}.py`. You should import the classes/functions from it.

Original COBOL logic for context:
{cobol_code}

Translated Python Code:
{python_code}
"""

SELF_HEALING_PROMPT = """You are an expert Python debugger. 
You previously generated the following Python code and tests, but the tests failed during execution.

Analyze the pytest traceback and fix the code. You must output the ENTIRE fixed Python code.
Output ONLY valid Python code. No markdown, no explanations.

Context:
Which file needs fixing based on the error?: {target_file}

Original Code ({target_file}):
{original_code}

Pytest Traceback Error:
{traceback}
"""

TRACEABILITY_PROMPT = """You are an expert legacy code auditor.
I have a COBOL file and its newly translated Python equivalent.
Your task is to generate a JSON array mapping the major sections/logic of the COBOL code to the Python code.

The JSON should be an array of objects:
- "cobol_logic": A string describing the COBOL section.
- "python_logic": A string describing the corresponding Python section.

Output ONLY valid JSON. Do not include markdown blocks like ```json. Just raw JSON.

COBOL Code:
{cobol_code}

Python Code:
{python_code}
"""

JCL_TO_AIRFLOW_PROMPT = """You are an expert Cloud Data Engineer.
I have an IBM Mainframe JCL script. Translate it into a modern Apache Airflow DAG in Python.

Guidelines:
1. Map JCL Steps to Airflow Operators.
2. Output ONLY valid Python code. No markdown blocks.

JCL Script:
{jcl_code}
"""

SECURITY_UPGRADE_PROMPT = """You are an elite Cybersecurity Engineer.
Review the following translated Python code. 
Your task is to identify legacy anti-patterns (e.g. hardcoded passwords, insecure database strings) and rewrite them to use modern security best practices (e.g., pulling from `os.environ.get()` or AWS Secrets Manager).

Rewrite the entire file and output ONLY valid Python code. No markdown.

Original Python Code:
{python_code}
"""

DEPENDENCY_RESOLUTION_PROMPT = """You are an expert Python Dependency Manager.
Review the following COBOL code. It may contain external `CALL` statements to proprietary mainframe modules or `EXEC SQL` calls.
List the modern Python `pip` packages that should be installed to support the translated logic (e.g., `requests`, `SQLAlchemy`, `psycopg2`).

Output ONLY a plain text file suitable for `requirements.txt`. Do not output explanations or markdown.

COBOL Code:
{cobol_code}
"""
