import qrcode
from io import BytesIO


def calculate_qr_settings(text):
    text_length = len(text)

    if text_length <= 25:
        version = 1
        box_size = 12
    elif text_length <= 47:
        version = 2
        box_size = 10
    elif text_length <= 77:
        version = 3
        box_size = 8
    elif text_length <= 114:
        version = 4
        box_size = 7
    elif text_length <= 154:
        version = 5
        box_size = 6
    elif text_length <= 195:
        version = 6
        box_size = 5
    elif text_length <= 224:
        version = 7
        box_size = 5
    elif text_length <= 279:
        version = 8
        box_size = 4
    elif text_length <= 335:
        version = 9
        box_size = 4
    elif text_length <= 395:
        version = 10
        box_size = 3
    else:
        version = None
        box_size = 3

    return version, box_size


async def generate_qr(text):
    version, box_size = calculate_qr_settings(text)

    qr = qrcode.QRCode(
        version=version,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=box_size,
        border=4,
    )

    qr.add_data(text)
    qr.make(fit=True)

    qr_image = qr.make_image(fill_color="black", back_color="white")

    img_buffer = BytesIO()
    qr_image.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    return img_buffer
