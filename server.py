from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from engine import calculate_level # Импортируем нашу логику

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Получаем данные от HTML
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        grammar = float(data.get('grammar', 0))
        vocab = float(data.get('vocab', 0))
        listen = float(data.get('listen', 0))

        result = calculate_level(grammar, vocab, listen)
        
        # Отправляем ответ обратно в HTML
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

    def do_GET(self):
        # Просто отдаем index.html
        if self.path == '/' or self.path == '/index.html':
            with open('index.html', 'rb') as f:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f.read())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), Handler)
    print("Сервер запущен! Откройте в браузере: http://localhost:8080")
    server.serve_forever()