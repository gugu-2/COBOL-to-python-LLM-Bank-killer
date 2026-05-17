import subprocess
import os
import logging

class Sandbox:
    @staticmethod
    def run_tests(test_filepath: str) -> tuple[bool, str]:
        """
        Executes pytest on the given test file.
        Returns a tuple of (success: bool, output/traceback: str)
        """
        if not os.path.exists(test_filepath):
            return False, f"Test file not found: {test_filepath}"

        try:
            logging.info(f"Running tests via pytest for: {test_filepath}")
            result = subprocess.run(
                ["python", "-m", "pytest", test_filepath, "-v"],
                capture_output=True,
                text=True,
                timeout=30 # 30 second timeout to prevent infinite loops in generated code
            )
            
            # pytest returns 0 if all tests pass
            if result.returncode == 0:
                return True, result.stdout
            else:
                return False, result.stdout + "\n" + result.stderr

        except subprocess.TimeoutExpired:
            return False, "Execution timed out. The generated code might contain an infinite loop."
        except Exception as e:
            return False, f"Sandbox execution error: {str(e)}"
