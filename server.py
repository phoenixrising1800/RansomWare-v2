"""server.py

Host server listening for POST data upload of a generated encryption key
"""

import http.server # Our HTTP Server Handler for requests
import socketserver # Establish the TCP Socket connections

PORT = 9000

class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        length = int(self.headers["Content-Length"])
        print('Data: ' + str(self.rfile.read(length), 'utf-8'))
        
        response = bytes('Received POST data', 'utf-8')
        self.send_response(200)
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()

        self.wfile.write(response)

Handler = MyHttpRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("HTTP Server Serving at Port: ", PORT)
    try:
        httpd.serve_forever()
    except:
        print("Server stopped")
