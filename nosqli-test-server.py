# coding: utf-8

import http.server as serv
from urllib.parse import urlparse
from urllib.parse import parse_qs
import json
import redis

pool = redis.ConnectionPool(host='WSL(Redis)_IP', port=6379, db=0)
r = redis.StrictRedis(connection_pool=pool)

class MyHandler(serv.BaseHTTPRequestHandler):
    def do_GET(self):

        parsed_path = urlparse(self.path)
        with open('./html/index.html' , encoding='utf-8') as f:
            html = f.read()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(html.encode('UTF-8'))
    
    def do_POST(self):
        if self.path == "/test/":
            param = self.rfile.read(int(self.headers['content-length'])).decode()
            q = parse_qs(param, keep_blank_values=1).get('q')[0]
            
            # Lua Script
            # Register parameter values with the key "test".
            lua = "return redis.call('SET', 'test', '%s')" % q
            multiply = r.register_script(lua)

            try:
                with open('./html/nosqli.html' , encoding='utf-8') as f:
                    html = f.read() % (q, multiply(), r.get('test'))
            except redis.exceptions.ResponseError as e:
                with open('./html/index.html' , encoding='utf-8') as f:
                    html = f.read() % e
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(html.encode('UTF-8'))

httpd = serv.HTTPServer(('127.0.0.1', 8000), MyHandler)
httpd.serve_forever()
