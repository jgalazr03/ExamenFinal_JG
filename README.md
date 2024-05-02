# Examen final
Estas son las instrucciones de instalación.

## Instalación de librerias

```bash
pip3 install Pillow pycryptodome requests Flask
```

## Código (Python)- Lado del cliente

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import requests
from PIL import Image
import io

def encrypt_image(image_path, key):
    print("Cargando imagen...")
    image = Image.open(image_path)
    image_bytes = io.BytesIO()
    image.save(image_bytes, format=image.format)
    data = image_bytes.getvalue()
    
    print("Encriptando imagen...")
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    iv = cipher.iv
    
    print("Imagen encriptada.")
    return iv + ct_bytes, image.format  # Prepend iv to ciphertext

def send_image_to_server(encrypted_data, image_format):
    print("Enviando imagen encriptada al servidor...")
    url = 'http://127.0.0.1:5000/upload'
    files = {'file': (f'encrypted_image.{image_format.lower()}', encrypted_data)}
    response = requests.post(url, files=files)
    print("Imagen enviada al servidor.")

    if response.status_code == 200:
        print("Imagen recibida de vuelta del servidor. Guardando...")
        image_path = 'received_decrypted_image.' + image_format.lower()
        with open(image_path, 'wb') as f:
            f.write(response.content)
        print("Imagen guardada como:", image_path)
    else:
        print("No se pudo recuperar la imagen del servidor, código de estado:", response.status_code)
    return response.text

# Clave de encriptación
key = b'my16-bytekey1234'

# Encriptando la imagen y enviando al servidor
encrypted_image, format = encrypt_image('chairImage.jpg', key)
response = send_image_to_server(encrypted_image, format)
print(response)
```

## Código (Python) - Lado del servidor

```python
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
```

### Notas:
1. Hay que agregar la imagen y, en el código del cliente, hay que cambiar el path de la imagen por el de tu imagen.
2. La clave de 16 bytes debe coincidir para que funcione la encriptación y desencriptación correctamente (ya hay una predeterminada que debe funcionarte). 
3. Ya agregué una imagen para que puedas hacer la prueba.

## Proceso de ejecución
1. Ejecutar el código del servidor con: **.../python3 servidor.py**
2. Ejecutar el código del cliente con: **.../python3 cliente.py**