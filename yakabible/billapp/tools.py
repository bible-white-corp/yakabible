import re
import qrcode
import os

from django.conf import settings

from PIL import Image

from io import BytesIO, StringIO
import datetime
from django.http import HttpResponse
from reportlab.pdfgen import canvas

from django.template.loader import render_to_string

from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage

from billapp.forms import Event_Form, Staff_Form_Set, EventStaffCapacity

from icalendar import Calendar, Event


def make_qrcode(ticket):
    """
    Generates the QRCode.
    :param ticket: ticket of the current user
    :return: image object of the QRCode
    """
    q = qrcode.QRCode()
    q.add_data(ticket.user.username + '\n')
    q.add_data(str(ticket.event.pk) + '\n')
    q.add_data(str(ticket.pk) + '\n')
    q.add_data(ticket.user.email + '\n')
    return q.make_image()


def make_ics(ticket):
    """
    Generate an ics object following RFC5455
    :param ticket: the ticket that correspond to the future ics
    :return: the calendar object
    """
    cal = Calendar()
    cal.add('version', '2.0')
    cal.add('prodid', '//BWC//BILLETERIE EPITA//FR')
    event = Event()
    event.add('summary', ticket.event.title)
    event.add('uid', datetime.datetime.now())
    event.add('dtstart', ticket.event.begin)
    event.add('dtstamp', datetime.datetime.now())
    event.add('dtend', ticket.event.end)
    event.add('description', ticket.event.description)
    event.add('location', ticket.event.place)
    cal.add_component(event)

    return cal


def get_ticket_type(ticket):
    if ticket.category:
        return "Staff"
    elif ticket.ionis:
        return "Interne"
    return "Externe"


def make_pdf(ticket):
    """
    Generates the pdf ticket of the current user.
    :param ticket: ticket object of the current user.
    :return: a pdf object
    """
    association = ticket.event.association
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
    p.drawString(100, 500, 'Type de ticket: ' + get_ticket_type(ticket))
    p.drawString(100, 480, 'ID: ' + str(ticket.pk))
    p.drawInlineImage(img, 100, 60)

    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def send_mail(obj, text_bd, html_bd, targets):
    """
    Generic function to send informational mail
    :param obj: the subject of the mail
    :param text_bd: the .txt alternative file
    :param html_bd: the html main view file
    :param targets: a list of mail address
    :return: true if sending succeeded
    """
    email = EmailMultiAlternatives(
        subject=obj, from_email='yakabible@gmail.com', to=targets,
        body=text_bd
    )
    email.attach_alternative(html_bd, "text/html")
    email.mixed_subtype = 'related'
    fp = open(os.path.join(settings.BASE_DIR, 'billapp/static/billapp/img/logo-epita.png'), 'rb')
    epita_logo = MIMEImage(fp.read())
    fp.close()
    epita_logo.add_header('Content-ID', '<{}>'.format('logo-epita.png'))
    email.attach(epita_logo)
    return email.send() == 1


def send_pdf_mail(ticket, pdf=None):
    """
    Send the ticket mail to the tuser
    :param ticket: the ticket in the BDD
    :param pdf: the pdf to attach if exists
    :return: boolean with true if the sending succeeded
    """
    if pdf is None:
        pdf = make_pdf(ticket)

    qr = make_qrcode(ticket)
    pdf_name = "{}_{}.pdf".format(ticket.user, ticket.event.title.replace(' ', '-'))

    context = {'title': 'Votre ticket pour ' + ticket.event.title,
               'ticket': ticket,
               'event': ticket.event
               }

    obj = ticket.user.username + ', vos billets pour l\'événement ' + ticket.event.title
    text_bd = render_to_string("emails/email-ticket-template.txt", context)
    html_bd = render_to_string("emails/email-ticket-template.html", context)

    email = EmailMultiAlternatives(
        subject=obj, from_email='yakabible@gmail.com', to=[ticket.user.email],
        body=text_bd
    )
    email.attach_alternative(html_bd, "text/html")
    email.mixed_subtype = 'related'

    # Converting the EPITA img as an embedded image for the mail html
    fp = open(os.path.join(settings.BASE_DIR, 'billapp/static/billapp/img/logo-epita.png'), 'rb')
    epita_logo = MIMEImage(fp.read())
    fp.close()
    epita_logo.add_header('Content-ID', '<{}>'.format('logo-epita.png'))

    # Creation of the QRCode as an embedded image in the mail
    qr_tmp = BytesIO()
    qr.save(qr_tmp, "PNG")
    qrcode = MIMEImage(qr_tmp.getvalue())
    qrcode.add_header('Content-ID', '<{}>'.format('qr-code.png'))

    # Generating the .ics attcach file
    cal = make_ics(ticket).to_ical()

    email.attach(epita_logo)
    email.attach(qrcode)
    email.attach(pdf_name, pdf)
    email.attach('event.ics', cal, 'text/calendar')

    return email.send() == 1


def send_approval_mail(ev, adm, path):
    """
    Send mail to resp and president (if found) asking them to approve the event
    """
    prez = ev.association.associationuser_set.filter(role=2)
    if not prez:
        return False
    prez = prez[0].user.email

    context = {'title': 'Requete d\'approbation: ' + ev.title,
               'link': path,
               'event': ev
               }

    obj = '[APPROBATION][' + ev.association.name + '] Requete d\'approbation: ' + ev.title
    text_bd = render_to_string("emails/email-approval-template.txt", context)
    html_bd = render_to_string("emails/email-approval-template.html", context)

    targets = []
    if prez == ev.manager.email:
        targets = [adm.email]
    elif adm.email == ev.manager.email:
        targets = [prez]
    else:
        targets = [adm.email, prez, ev.manager.email]

    return send_mail(obj, text_bd, html_bd, targets)


def send_registration(username, email, link):
    """
    Send mail to resp and president (if found) asking them to approve the event
    """

    context = {'title': 'Bienvenue !',
               'fullname': username,
               'link': link
               }

    obj = '[BILLETERIE][EPITA] Bienvenue!'
    text_bd = render_to_string("emails/email-registration.txt", context)
    html_bd = render_to_string("emails/email-registration.html", context)

    return send_mail(obj, text_bd, html_bd, [email])


def send_validation_mail(ev, adm, path):
    """
    Send mail to resp and president (if found) asking them to approve the event
    """
    prez = ev.association.associationuser_set.filter(role=2)
    if not prez or not adm:
        return False
    prez = prez[0].user.email
    adm = adm[0].email

    context = {'title': 'Événement approuvé: ' + ev.title,
               'link': path,
               'event': ev
               }

    obj = '[VALIDATION][' + ev.association.name + '] Événement approuvé: ' + ev.title
    text_bd = render_to_string("emails/email-validation-template.txt", context)
    html_bd = render_to_string("emails/email-validation-template.html", context)

    return send_mail(obj, text_bd, html_bd, [adm, prez, ev.manager.email])


def send_refusing_mail(ev, adm, is_prez, description, path):
    """
    Send mail to resp and president (if found) asking them to approve the event
    """
    prez = ev.association.associationuser_set.filter(role=2)
    if not prez or not adm:
        return False
    prez = prez[0].user.email
    adm = adm[0].email

    context = {'title': 'Événement refusé: ' + ev.title,
               'link': path,
               'event': ev,
               'has_description': len(description) != 0,
               'description': description,
               'is_prez': is_prez
               }
    text_bd = render_to_string("emails/email-refusing-template.txt", context)
    html_bd = render_to_string("emails/email-refusing-template.html", context)
    obj = '[VALIDATION][' + ev.association.name + '] Événement refusé: ' + ev.title

    return send_mail(obj, text_bd, html_bd, [adm, prez, ev.manager.email])


def make_pdf_response(ticket, pdf=None):
    """
    Prepare pdf for browser download.
    :param ticket: ticket of the user/event.
    :param pdf: pdf object generated from the ticket
    :return: the http response for download.
    """
    if pdf is None:
        pdf = make_pdf(ticket)

    pdf_name = "{}_{}.pdf".format(ticket.user, ticket.event.title.replace(' ', '-'))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=' + pdf_name

    response.write(pdf)
    return response


def transform_date(date_field):
    return date_field.strftime("%d/%m/%Y %H:%M")


def get_form_from_event(event):
    """
    Re-create form creation event.
    :param event: the event object
    :return: the form created
    """
    form = Event_Form(initial={
        "title": event.title,
        "description": event.description,
        "begin": transform_date(event.begin),
        "end": transform_date(event.end),
        "begin_register": transform_date(event.begin_register),
        "end_register": transform_date(event.end_register),
        "place": event.place,
        "price_ionis": event.price_ionis,
        "price": event.price,
        "ext_capacity": event.ext_capacity,
        "int_capacity": event.int_capacity,
        "promotion_image_path": event.promotion_image_path,
        "show_capacity": event.show_capacity
    })
    return form


def get_staff_form_from_event(event):
    """
    Re-create form for the staff of an event
    :param event: concerned events.
    :return: the form created.
    """
    staffs = EventStaffCapacity.objects.filter(event=event)

    list_form = []
    for staff in staffs:
        list_form.append({'association_name': staff.association.pk,
                          'capacity': staff.capacity})

    staff_form = Staff_Form_Set(initial=list_form)
    return staff_form


def send_modification_mail(ev, president, adm, link):
    """
    Informs ADM and/or president if an event has changed and need to be approved.
    """
    dest = []
    if president:
        dest.append(president)
    if adm:
        dest.append(adm)
    dest.append(ev.manager.email)

    context = {'title': 'Événement modifié: ' + ev.title,
               'link': link,
               'event': ev,
               }
    text_bd = render_to_string("emails/email-modified-template.txt", context)
    html_bd = render_to_string("emails/email-modified-template.html", context)
    obj = '[VALIDATION][' + ev.association.name + '] Événement modifié: ' + ev.title

    return send_mail(obj, text_bd, html_bd, dest)


def send_modification_notification_mail(ev, user, link):
    context = {'title': 'Événement modifié: ' + ev.title,
               'link': link,
               'event': ev,
               }
    text_bd = render_to_string("emails/email-modified-notif-template.txt", context)
    html_bd = render_to_string("emails/email-modified-notif-template.html", context)
    obj = '[MODIFICATION][' + ev.association.name + '] Événement modifié: ' + ev.title

    return send_mail(obj, text_bd, html_bd, [user])
