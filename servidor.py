from flask import Flask, request, jsonify, send_file
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from PIL import Image
import io

app = Flask(__name__)

def decrypt_image(encrypted_data, key):
    print("Desencriptando imagen recibida...")
    iv = encrypted_data[:AES.block_size]
    ct = encrypted_data[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    print("Imagen desencriptada exitosamente.")
    return pt

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    image_format = file.filename.split('.')[-1] 
    print("Imagen recibida en el servidor.")
    key = b'my16-bytekey1234'
    
    try:
        decrypted_data = decrypt_image(file.read(), key)
        image = Image.open(io.BytesIO(decrypted_data))
        img_io = io.BytesIO()
        image.save(img_io, format=image_format.upper())
        img_io.seek(0)
        print("Enviando imagen desencriptada de vuelta al cliente.")
        return send_file(img_io, mimetype=f'image/{image_format.lower()}')
    except Exception as e:
        print("Error al desencriptar la imagen.")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)