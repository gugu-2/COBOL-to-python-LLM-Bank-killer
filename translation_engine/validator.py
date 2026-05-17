import ast

class CodeValidator:
    @staticmethod
    def is_valid_python(code: str) -> tuple[bool, str]:
        """
        Validates if the provided string is valid Python code.
        Returns a tuple: (is_valid: bool, error_message: str)
        """
        try:
            ast.parse(code)
            return True, ""
        except SyntaxError as e:
            return False, f"Syntax Error: {e.msg} at line {e.lineno}"
        except Exception as e:
            return False, f"Validation Error: {str(e)}"
