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