#!/usr/bin/env python3
import http.server
import socketserver
import os

# Force change to frontend directory
os.chdir('/Users/kartika/Documents/GitHub/paper-generator/frontend')
print(f"Serving from: {os.getcwd()}")
print(f"Files: {os.listdir('.')}")

PORT = 3000
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Server running at http://localhost:{PORT}/")
    httpd.serve_forever()