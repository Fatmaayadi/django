import qrcode
from io import BytesIO
from django.core.files.base import ContentFile

def generate_qr_for_ticket(ticket):
    data = f"ticket:{ticket.reference}"
    img = qrcode.make(data)
    buf = BytesIO()
    img.save(buf, format='PNG')
    filename = f"qr_{ticket.reference}.png"
    filebuf = ContentFile(buf.getvalue())
    ticket.qr_code.save(filename, filebuf)
    ticket.save()
    return ticket.qr_code.url
