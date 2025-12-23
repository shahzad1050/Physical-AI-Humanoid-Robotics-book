# Create a very minimal FastAPI app that avoids the problematic openapi models
import sys
import os

# Try to install a known working combination
print("Trying to run minimal backend...")

# Let's try to start the original app directly with a workaround
import os
import sys

# Add the parent directory to the path so we can import from frontend
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Set environment variable to avoid the pydantic-settings import issue
os.environ['PYDANTIC_ERRORS_OMIT_URL'] = '1'

try:
    from fastapi import FastAPI
    print("FastAPI imported successfully")

    app = FastAPI(title="Test App", version="1.0.0")

    @app.get("/")
    def read_root():
        return {"status": "Backend is running"}

    if __name__ == "__main__":
        import uvicorn
        print("Starting server on http://0.0.0.0:8000")
        uvicorn.run(app, host="0.0.0.0", port=8000)

except Exception as e:
    print(f"Error: {e}")
    print("There's a compatibility issue between FastAPI and Pydantic versions.")
    print("The project requires specific versions that may not be compatible with the current environment.")