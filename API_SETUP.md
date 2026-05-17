# 🔑 API Key Configuration

QuantumForge AI Pipeline relies on advanced Google Gemini models to power its codebase translation, self-healing, and security patching mechanisms.

To use the software, you must configure your local environment with a valid Gemini API key.

## 1. Obtain an API Key
If you do not already have one, obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/). 
Ensure your Google Cloud Project has billing enabled or has sufficient free-tier quota for the `gemini-2.5-flash` or `gemini-2.5-pro` models.

## 2. Setup the `.env` file
The pipeline securely reads your API key from a `.env` file located in the root directory.

1. Create a file named `.env` in the root of the project (if it doesn't already exist).
2. Add the following line, replacing the placeholder with your actual key:
```env
GEMINI_API_KEY="your_api_key_here"
```

*Note: Make sure `.env` is listed in your `.gitignore` so you do not accidentally commit your credentials to a public repository.*

## 3. Verify Authentication
Once the `.env` file is saved, you can verify it by executing a test run of the core pipeline:
```bash
python main.py --input sample_db2.cbl --output modern_app.py
```
If the execution begins logging "HTTP Request: POST... 200 OK", your authentication was successful.
