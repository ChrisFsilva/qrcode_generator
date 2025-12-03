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

def calcula_crc16(data: str):
    polinomio = 0x1021
    resultado = 0xFFFF

    for char in data:
        resultado ^= (ord(char) << 8)
        for _ in range(8):
            if resultado & 0x8000:
                resultado = ((resultado << 1) ^ polinomio) & 0xFFFF
            else:
                resultado = (resultado << 1) & 0xFFFF

    return f"{resultado:04X}"


def campo(id, valor):
    return f"{id}{len(valor):02}{valor}"

def gerar_payload_pix(chave, nome, cidade, valor):
    nome = nome.strip() if nome else "DESCONHECIDO"
    cidade = cidade.strip() if cidade else "BR"
    chave = chave.strip()

    # Normaliza valor
    if valor and valor.strip() != "":
        valor = valor.replace(",", ".")
    else:
        valor = None

    payload = "000201"

    # Merchant Account Information
    gui = "BR.GOV.BCB.PIX"
    merchant_info = campo("00", gui) + campo("01", chave)
    payload += campo("26", merchant_info)

    payload += "52040000"
    payload += "5303986"

    if valor:
        payload += campo("54", valor)

    payload += "5802BR"
    payload += campo("59", nome)
    payload += campo("60", cidade)

    # TXID válido (8 caracteres alfa-numéricos)
    txid = "ABCD1234"
    adf = campo("05", txid)
    payload += campo("62", adf) 

    payload_sem_crc = payload + "6304"
    crc = calcula_crc16(payload_sem_crc)
    print(payload)
    return payload_sem_crc + crc

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
    
    if tipo == "whatsapp":
            numero = request.form.get("wa_number")
            mensagem = request.form.get("wa_msg")

            # Mantendo somente digitos no telefone
            numero = ''.join(filter(str.isdigit,numero))

            # Retirar o 0
            if numero.startswith("0"):
                numero=numero[1:]

            # ADICIONAR DDI DO BRASIL
            if not numero.startswith("55"):
                numero="55"+numero

            # CODIFICAR A MENSAGEM
            from urllib.parse import quote
            mensagem_enconded = quote(mensagem)

            url = f"https://wa.me/{numero}?text={mensagem_enconded}"

            img = qrcode.make(url)
            file_path = os.path.join(BASE_DIR,"wp_qrcode.png")
            img.save(file_path)
            return send_file(file_path, as_attachment=True)
    
    # CODIGO DO GERADOR DO PIX
    
    if tipo == "pix":
        chave = request.form.get("pixKey")
        nome = request.form.get("pixName")
        cidade = request.form.get("pixCity")
        valor = request.form.get("pixValor")

        payload = gerar_payload_pix(chave, nome, cidade, valor)

        img = qrcode.make(payload)

        file_path = os.path.join(BASE_DIR, "pix_qrcode.png")
        img.save(file_path)

        return send_file(file_path, as_attachment=True)

         
    return "Tipo Inválido"

if __name__ == "__main__":
    app.run(debug=True)