# Biblioteca para renderização web
from flask import  Flask, render_template, request, send_file
import os

# Bibliotecas para criação de QRcode
import qrcode
from wifi_qrcode_generator.generator import wifi_qrcode


app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")

def index ():
    return render_template("index.html")

@app.route("/gerar", methods=["POST"])
# Função para gerar QRcode
def gerar():
    # Coletar a informação do tipo escolhido no frontend
    tipo = request.form.get("tipo")

    # Gerar QrCode do WiFi
    if tipo == "wifi":     
        ssid = request.form.get("ssid")
        password = request.form.get("password")
        auth = request.form.get("auth")

        qr = wifi_qrcode(ssid, False, auth, password)
        img = qr.make_image()

        file_path = os.path.join(BASE_DIR,"Wifi_QrCode.png")
        img.save(file_path)
        return send_file(file_path, as_attachment=True)
    
    # Gerar QrCode para Url
    if tipo == "url":
            url = request.form.get("url")
            img = qrcode.make(url)

            file_path = os.path.join(BASE_DIR,"url_dinamico.png")
            img.save(file_path)
            return send_file(file_path, as_attachment=True)
    
    if tipo == "vcard":

            nome = request.form.get("nome")
            sobrenome = request.form.get("sobrenome")
            telefone = request.form.get("telefone")
            email = request.form.get("email")

            vcard_text =( 
                "BEGIN:VCARD\n"
                "VERSION:3.0"
                f"N:{sobrenome};{nome};;;\n"
                f"FN:{nome} {sobrenome}\n"
                f"TEL;TYPE=CELL:{telefone}\n"
                f"EMAIL;TYPE=INTERNET:{email}\n"
                "END:VCARD"
            )

            img = qrcode.make(vcard_text)

            file_path = os.path.join(BASE_DIR,"contato_vcard.png")
            img.save(file_path)
            return send_file(file_path, as_attachment=True)
    
    return "Tipo Inválido"

if __name__ == "__main__":
    app.run(debug=True)