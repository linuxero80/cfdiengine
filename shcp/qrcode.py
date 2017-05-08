import os
import qrcode

def qrcode_v33():
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data("hola mundo")
    qr.make(fit=True)
    x = qr.make_image()

    qr_file = os.path.join("./out" + ".jpg")
    img_file = open(qr_file, 'wb')
    x.save(img_file, 'JPEG')
    img_file.close()
