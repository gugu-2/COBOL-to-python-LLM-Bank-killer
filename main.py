import argparse
from dotenv import load_dotenv
from translation_engine.llm_adapter import GeminiAdapter
from translation_engine.core import TranslationEngine

def main():
    parser = argparse.ArgumentParser(description="Autonomous COBOL to Python Translation Engine")
    parser.add_argument("--input", required=True, help="Path to the input COBOL file")
    parser.add_argument("--output", required=True, help="Path to save the generated Python file")
    
    args = parser.parse_args()

    # Load environment variables (e.g., GEMINI_API_KEY from .env)
    load_dotenv()

    try:
        print("Initializing LLM Adapter...")
        adapter = GeminiAdapter()
        
        print("Initializing Translation Engine...")
        engine = TranslationEngine(adapter=adapter)
        
        print(f"Translating {args.input} -> {args.output}...")
        engine.translate_file(args.input, args.output)
        
        print("Migration complete!")
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    main()
