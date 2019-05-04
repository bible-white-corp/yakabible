import qrcode

from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas

from django.core.mail import EmailMessage


def make_qrcode(ticket):
    q = qrcode.QRCode()
    q.add_data(ticket.user.username + '\n')
    q.add_data(str(ticket.event.pk) + '\n')
    q.add_data(str(ticket.pk) + '\n')
    q.add_data(ticket.user.email + '\n')
    return q.make_image()


def make_pdf(ticket):
    buffer = BytesIO()
    img = make_qrcode(ticket)

    p = canvas.Canvas(buffer)

    p.drawString(100, 700, 'Nom d\'utilisateur: ' + ticket.user.username)
    full_name = ticket.user.first_name + ' ' + ticket.user.last_name
    p.drawString(100, 680, 'Nom: ' + full_name)
    p.drawString(100, 660, 'Nom de l\'événement: ' + ticket.event.title)
    p.drawString(100, 640, 'ID: ' + str(ticket.pk))
    p.drawInlineImage(img, 100, 160)

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def send_pdf_mail(pdf, ticket):
    pdf_name = "{}_{}.pdf".format(ticket.user, ticket.event.title.replace(' ', '-'))

# TODO plus joli mail
    email = EmailMessage(
        'Billetterie EPITA: ' + ticket.event.title,
        ticket.user.username + ', voici votre place pour l\'événement ' + ticket.event.title,
        'yakabible@gmail.com',
        [ticket.user.email]
    )
    email.attach(pdf_name, pdf)
    # TODO à la fin email.send(True) pour enlever le debug (indépendant de DEBUG=True)
    email.send()


def make_pdf_response(ticket):
    pdf_name = "{}_{}.pdf".format(ticket.user, ticket.event.title.replace(' ', '-'))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + pdf_name

    pdf = make_pdf(ticket)

    send_pdf_mail(pdf, ticket)

    response.write(pdf)
    return response