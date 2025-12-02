# Biblioteca para renderização web
from flask import  Flask, render_template, request, send_file
import io
# Bibliotecas para criação de QRcode
from wifi_qrcode_generator.generator import wifi_qrcode
from PIL import Image


app = Flask(__name__)
@app.route("/")

def index ():
    return render_template("index.html")

@app.route("/gerar", methods=["POST"])
# Função para gerar QRcode
def gerar():
    
    ssid = request.form["ssid"].strip()
    password = request.form["password"].strip()
    auth = request.form["auth"]

    qr = wifi_qrcode(ssid, False, auth, password)
    img = qr.make_image()

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)

    return send_file(
        buf,
        mimetype="image/png",
        as_attachment=True,
        download_name="WiFi_QRcode.png"
    )

if __name__ == "__main__":
    app.run(debug=True)