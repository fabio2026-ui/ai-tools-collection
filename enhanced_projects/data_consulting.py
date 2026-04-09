#!/usr/bin/env python3
import http.server, json
from datetime import datetime

class DataConsulting:
    def consult(self):
        return {
            "consultants": ["AI专家1", "AI专家2", "AI专家3"],
            "availability": "立即可用",
            "timestamp": datetime.now().isoformat()
        }

handler = type('Handler', (http.server.BaseHTTPRequestHandler,), {
    'consulting': DataConsulting(),
    'do_GET': lambda self: self._send_json(self.consulting.consult()),
    '_send_json': lambda self, data: (
        self.send_response(200),
        self.send_header('Content-type', 'application/json'),
        self.end_headers(),
        self.wfile.write(json.dumps(data).encode())
    )[3]
})
# exec("import socketserver; socketserver.TCPServer((\"\", 5008), handler).serve_forever()")
