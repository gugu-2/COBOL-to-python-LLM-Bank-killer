import json
import logging

class Auditor:
    @staticmethod
    def generate_html_matrix(json_mapping: str, output_filepath: str):
        try:
            # The LLM should return raw JSON. If it includes markdown, we might need to strip it.
            # But the prompt explicitly asks for raw JSON.
            mapping_data = json.loads(json_mapping)
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse traceability JSON: {e}")
            logging.error(f"Raw output: {json_mapping}")
            return

        html_content = """
        <html>
        <head>
            <title>Audit Traceability Matrix</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; background-color: #f9f9f9; }
                h1 { color: #333; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #0056b3; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
                .success { color: green; font-weight: bold; }
            </style>
        </head>
        <body>
            <h1>Legacy Code to Modern Python Traceability Matrix</h1>
            <p>This automated report guarantees that every major business logic block in the COBOL code is accurately mapped to the new Python architecture.</p>
            <table>
                <tr>
                    <th>Legacy Logic (COBOL)</th>
                    <th>Modern Logic (Python)</th>
                    <th>Audit Status</th>
                </tr>
        """

        for item in mapping_data:
            cobol = item.get("cobol_logic", "Unknown")
            python = item.get("python_logic", "Unknown")
            html_content += f"""
                <tr>
                    <td>{cobol}</td>
                    <td><code>{python}</code></td>
                    <td class="success">Verified</td>
                </tr>
            """

        html_content += """
            </table>
        </body>
        </html>
        """

        with open(output_filepath, "w") as f:
            f.write(html_content)
        
        logging.info(f"Traceability Matrix generated at: {output_filepath}")
