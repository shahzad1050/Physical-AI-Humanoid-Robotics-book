# Create a mock backend server that mimics the expected API and also serves simple documentation
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from urllib.parse import urlparse

print("Starting mock backend server with API documentation...")

class MockRAGHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"status": "healthy", "api": "RAG Chatbot API", "version": "1.0.0"}
            self.wfile.write(json.dumps(response).encode())
        elif path == '/test_json':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"hello": "world", "status": "ok"}
            self.wfile.write(json.dumps(response).encode())
        elif path == '/docs' or path == '/redoc':
            # Serve simple API documentation
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            doc_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Physical AI & Humanoid Robotics RAG API Documentation</title>
            </head>
            <body>
                <h1>Physical AI & Humanoid Robotics RAG API</h1>
                <h2>Available Endpoints:</h2>
                <ul>
                    <li><strong>GET /health</strong> - Health check</li>
                    <li><strong>GET /test_json</strong> - Test endpoint</li>
                    <li><strong>POST /chat</strong> - Chat endpoint (message: str, top_k: int)</li>
                </ul>
                <h3>Example request to /chat:</h3>
                <pre>
POST /chat
Content-Type: application/json

{
    "message": "What is Physical AI?",
    "top_k": 3
}
                </pre>
            </body>
            </html>
            """
            self.wfile.write(doc_html.encode())
        elif path == '/':
            # Serve a simple API root response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {"message": "Physical AI & Humanoid Robotics RAG API", "version": "1.0.0", "endpoints": ["/health", "/chat", "/docs"]}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/chat':
            # Read the request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            # Parse the request
            try:
                request_data = json.loads(post_data.decode('utf-8'))
                message = request_data.get('message', 'No message provided')
            except:
                message = 'Invalid request'

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            response = {
                "response": f"Mock response to: {message}",
                "context_used": [{"id": 1, "content": "mock context for testing", "score": 0.9}]
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

def start_mock_server():
    print("Starting mock RAG backend server on port 8002...")
    print("API documentation available at: http://localhost:8002/docs")
    server = HTTPServer(('0.0.0.0', 8002), MockRAGHandler)
    server.serve_forever()

if __name__ == "__main__":
    print("Starting mock RAG backend server...")
    print("This is a temporary mock server due to dependency compatibility issues.")
    print("Endpoints available:")
    print("  GET  /           - API root")
    print("  GET  /health     - Health check")
    print("  GET  /docs       - API documentation")
    print("  GET  /test_json  - Test endpoint")
    print("  POST /chat       - Chat endpoint")
    start_mock_server()