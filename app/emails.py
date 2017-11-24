from flask_mail import Message
from app import mail

from flask import render_template
from config import ADMINS

from threading import Thread
from app import app

from .decorators import async

@async
def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body): #receipents has to be in the form of a list
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    thr = Thread(target=send_async_email, args=[app, msg])
    if thr.isAlive():
        thr.join()
    thr.start()

def follower_notification(followed, follower):
    send_email("[Voitheia] %s is now following you!" % follower.username,
               ADMINS[0],
               [followed.email],
               render_template("email/follower_email.txt",
                               user=followed, follower=follower),
               render_template("email/follower_email.html",
                               user=followed, follower=follower))


def confirmation_mail(email_to_send_to, confirm_url):
    send_email("[Voitheia] - Confirm Account",
               ADMINS[0],
               [email_to_send_to],
               render_template("email/confirm.txt", confirm_url = confirm_url),
               render_template("email/confirm.html", confirm_url = confirm_url))

def recover_password(email_to_send_to, recover_url):
    send_email("[Voitheia] - Reset Password",
               ADMINS[0],
               [email_to_send_to],
               render_template("email/forgot_password.txt", recover_url = recover_url),
               render_template("email/forgot_password.html", recover_url = recover_url))


def spam(spam_receiver):
    i = 0
    while i < 100:
        send_email("This is spam from Aryan! Yay!",
        ADMINS[0],
        [spam_receiver],
        render_template("email/spam.txt"),
        render_template("email/spam.html"))
        i = i + 1