import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
from jinja2 import Template

# Conectar o crear la base de datos
conn = sqlite3.connect('database.db')
c = conn.cursor()

# Crear la tabla si no existe
c.execute('''CREATE TABLE IF NOT EXISTS purchase_form (
                product_ID TEXT,
                product TEXT,
                amount INTEGER
            )''')
conn.commit()

# Clase para manejar las peticiones HTTP
class MyHandler(BaseHTTPRequestHandler):
    
    # Método para manejar GET (enviar la página HTML con los datos de la tabla)
    def do_GET(self):
        if self.path == "/":
            # Recuperar los datos de la base de datos
            c.execute("SELECT * FROM purchase_form")
            rows = c.fetchall()

            # Cargar el formulario HTML y reemplazar las filas de la tabla
            with open("index.html", "r") as f:
                html = f.read()
            
            template = Template(html)
            rendered_html = template.render(rows=rows)
            
            # Enviar respuesta HTTP
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(rendered_html.encode("utf-8"))

    # Método para manejar POST (guardar datos en la base de datos y recargar la tabla)
    def do_POST(self):
        if self.path == "/submit":
            # Leer el contenido enviado en el formulario
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            form_data = urllib.parse.parse_qs(post_data)

            # Obtener los valores de los inputs
            product_ID = form_data.get('product_ID')[0]
            product = form_data.get('product')[0]
            amount = form_data.get('amount')[0]

            # Insertar datos en la base de datos
            c.execute("INSERT INTO purchase_form (product_ID, product, amount) VALUES (?, ?, ?)", 
                      (product_ID, product, amount))
            conn.commit()

            # Redirigir de nuevo a la página principal (para mostrar los nuevos datos)
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()

# Iniciar el servidor HTTP
def run(server_class=HTTPServer, handler_class=MyHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server running on port {port}...")
    httpd.serve_forever()

if __name__ == "__main__":
    run()

