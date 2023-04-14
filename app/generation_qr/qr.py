import io
import qrcode
from flask import Flask, send_file,Blueprint
from PIL import Image


qr_blouprint = Blueprint('qr_blouprint', __name__)

@qr_blouprint.route('/generate_qr_code/<path:encoded_url>')
def generate_qr_code(encoded_url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(encoded_url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')
