import qrcode


def qrcode_generator(code: int):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )

    qr.add_data(code)
    qr.make(fit=True)

    return qr.make_image(fill_color="black", back_color="white")
