import qrcode
import os
from django.conf import settings

from PIL import Image

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


def make_pdf(ticket, association):
    buffer = BytesIO()
    img = make_qrcode(ticket)
    logo_epita_tmp = Image.open(os.path.join(settings.BASE_DIR, 'billapp/static/billapp/img/logo-epita.png'));
    logo_asso_tmp = Image.open(association.logo_path);

    logo_epita = Image.new("RGB", logo_epita_tmp.size, (255, 255, 255))
    if (len(logo_epita_tmp.getbands()) == 4):
        logo_epita.paste(logo_epita_tmp, mask=logo_epita_tmp.split()[3])
    else:
        logo_epita.paste(logo_epita_tmp)

    logo_asso = Image.new("RGB", logo_asso_tmp.size, (255, 255, 255))
    if (len(logo_asso_tmp.getbands()) == 4):
        logo_asso.paste(logo_asso_tmp, mask=logo_asso_tmp.split()[3])
    else:
        logo_asso.paste(logo_asso_tmp)

    logo_epita = logo_epita.resize((100, 100), Image.NEAREST)
    logo_asso = logo_asso.resize((100, 100), Image.NEAREST)

    p = canvas.Canvas(buffer)

    print(logo_asso_tmp)

    p.drawInlineImage(logo_epita, 100, 700)
    p.drawInlineImage(logo_asso, 400, 700)
    p.drawString(100, 600, 'Nom d\'utilisateur: ' + ticket.user.username)
    full_name = ticket.user.first_name + ' ' + ticket.user.last_name
    p.drawString(100, 580, 'Nom: ' + full_name)
    p.drawString(100, 560, 'Nom de l\'événement: ' + ticket.event.title)
    p.drawString(100, 540, 'Date: ' +
                 ticket.event.begin.strftime('%m/%d/%Y, %H:%M:%S'))
    p.drawString(100, 520, 'Lieu: ' + ticket.event.place)
    p.drawString(100, 500, 'ID: ' + str(ticket.pk))
    p.drawInlineImage(img, 100, 60)

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


def make_pdf_response(ticket, association):
    pdf_name = "{}_{}.pdf".format(ticket.user, ticket.event.title.replace(' ', '-'))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + pdf_name

    pdf = make_pdf(ticket, association)

    send_pdf_mail(pdf, ticket)

    response.write(pdf)
    return response
