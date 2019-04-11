import qrcode
from django.http import HttpResponse
from reportlab.pdfgen import canvas

def make_qrcode(ticket):
    q = qrcode.QRCode()
    q.add_data(ticket.user.username + '\n')
    q.add_data(str(ticket.event.pk) + '\n')
    q.add_data(str(ticket.pk) + '\n')
    q.add_data(ticket.user.email + '\n')
    return q.make_image()

def make_pdf_response(ticket):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="{}_{}.pdf"' \
        .format(ticket.user, ticket.event.title.replace(' ', '-'))

    img = make_qrcode(ticket)
    p = canvas.Canvas(response)
    p.drawString(100, 700, 'Nom d\'utilisateur: ' + ticket.user.username)
    full_name = ticket.user.first_name + ' ' + ticket.user.last_name
    p.drawString(100, 680, 'Nom: ' + full_name)
    p.drawString(100, 660, 'Nom de l\'événement: ' + ticket.event.title)
    p.drawString(100, 640, 'ID: ' + str(ticket.pk))
    p.drawInlineImage(img, 100, 160)
    p.showPage()
    p.save()

    return response
