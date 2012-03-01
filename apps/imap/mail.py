import django_header
import settings

import pdb
import os, sys, time, re

from os.path                    import join
from PIL                        import Image


EMAIL  = 'fish@coastalflyrodders.com'
PHOTOS = join(settings.MEDIA_ROOT, 'photos/')

from django.db.models           import Q
from django.core.mail           import send_mail,EmailMessage,EmailMultiAlternatives
from django.contrib             import auth
from django.contrib.auth.models import User,Message,Group
from django.template            import loader, Context

# Import local stuff
from imap                       import *
from base.models                import *
from friends.models             import *
from notification.models        import *
from pycron                     import pycron

# Pre-compiled regular expressions
re_mobile = re.compile('[0-9]{10}')
re_email  = re.compile('^[\w\.=-]+@[\w\.-]+\.[\w]{2,3}$')

import password

# This is essentially send_mail, but adds attachments.
def mail_to(subject, message, from_email, recipient_list, attachments ):

    mail = EmailMessage(subject, message, from_email, recipient_list )
    for attach in attachments:
        mail.attach_file(attach)
    mail.send()

def cronjob(job):
    if len(job) == 0:
        return
    
    print 'Mailing @' + time.strftime("%I:%M:%S %p", time.localtime()) 
    
    qry = User.objects.filter(username = 'Pete_Douma')# make this ()
    spam = []
 
    # Send email to every user
    for user in qry:
        if user.first_name != u'':
            name  = user.first_name
        else:
            name = user.username
            
        profile = user.get_profile()
        
        #Old Facebook users only have proxy emails
        if user.email != u'':
            spam.append(user.email)
        elif profile.proxy_email != u'':
            spam.append(profile.proxy_email)

        # Personalize text and html version with first name
        c = Context({'name':name})
        text = loader.get_template('anyfish.txt').render(c)
        html = loader.get_template('anyfish.html').render(c)
  
        msg = EmailMultiAlternatives("How's the fishing?", text, EMAIL, spam )
        msg.attach_alternative(html, "text/html")
        msg.send(fail_silently = True)

    return
        
        
def main():
    # Get the mail
    mailbox = MailBox()
    mailbox.login('douma','fishf00l')
    
    # Set the cron job to send mail every week Mon at 12:00AM
    cron = pycron(latency = 30)
    cron.add_job('0 0 0 * * *', 'anyfish')
    

    # Continually poll
    while True:

        # Gets the mail list: If nothing there quit in order to clean up
        mail_msgs = mailbox.new_messages()
        if len(mail_msgs) == 0:
            mailbox.kill()
            time.sleep(30)
            cronjob( cron.get_matched_jobs())
            continue

        # Get each message
        for msg in mail_msgs:
            msg_num = mailbox.fetch(msg)
            em, sentby, group = mailbox.header(msg_num)

            # Check to see if you got an Undeliverable messages from the mail server
            if  em == "" or sentby == EMAIL:
                # Done with this email delete it
                mailbox.mark_deleted(msg)
                continue

            # See if this is a phone number
            pn = re_mobile.search(em)
            if pn != None:
                pn = pn.group(0)

            # Get the messages and pictures
            text,html  = mailbox.get_text(msg_num)
            tag,domain = em.split('@')

            media = mailbox.get_media(msg_num,prefix = tag+'-', path = PHOTOS )

            # Now look up sender in the database and add the message
            if pn != None:
                try:
                    profile = SpotUser.objects.get( mobile = pn )
                except Exception:
                    usr = None
                else:
                    usr = profile.user
                
            elif em != None:
                try:
                    usr = User.objects.get( email = em )
                except Exception:
                    usr = None
                else:
                    profile = usr.get_profile()
            
            # Make sure you have a user or dump the message
            if not usr:
                mailbox.mark_deleted(msg)
                continue


            # Save the text part of the message Decode quoted printable characters
            message = SpotMessage( user = usr )
            message.save()
            
            if text:
                if isinstance(text, list):
                    text = ' '.join(text)
 
                # Dump the reply part of the message
                if '----- Original Message -----' in text:
                    text,dmp = text.split('----- Original Message -----')
 
                message.text = text
            message.save()

            # Save each image, with this message.
            if media != None:
                for m in media:
                    
                    # Just get the file name and the relative url
                    path, title = split(m)
                    path = join('photos//',title)
                    photo = SpotPhoto( image = path, title = title )
                    photo.set_exif()

                    # Resize the image and convert to jpeg
                    ms = Image.open(m)
                    size = 400,400
                    ms.thumbnail(size, Image.ANTIALIAS)
                    ms.save(m, "JPEG")

                    try:
                        photo.save()
                    except Exception, e:
                        print 'Photo %s failed to save because %s'%(title,e)
                    else:
                        message.photos.add(photo)
                        try:
                            message.save()
                        except Exception,e:
                            print 'Photo %s failed to save to message because %s'%(title,e)
					
    
            # Check if this is a group message
            send_to = []

            if group and SpotGroup.objects.filter(name = group):
                group = SpotGroup.objects.get(name = group)

                # If this is a member of the group save the message
                if group.is_member(usr):
                    message.group = group
                    message.save()
                    members = group.get_members()
                    for member in members:
                        if member == usr:
                            continue
                        follow = group.follows_by(member)
                        if follow == 'email':
                            send_to.append(member.email)
                        elif follow == 'phone':
                            m_profile = member.get_profile()
                            send_to.append(m_profile.phone_addr)
                        notice_send(usr, member, "message_for_group",{'group':group})

            # Find my friends and send them a notice and email, or MMS
            else:
                friends = Friendship.objects.friends_who_follow(usr)
                for person in friends:
                    friend = person['friend']
                    notice_send(usr, friend, "message_from_friend",{'user':friend})
                    f_profile = friend.get_profile()
                    if person['follow'] == 'email':
                        if friend.email != '':
                            send_to.append(friend.email)
                    if person['follow'] == 'phone':
                        f_profile = friend.get_profile()
                        if f_profile.phone_addr != '':
                            send_to.append(f_profile.phone_addr)

            # Send email to everyone who is following this one
            if len(send_to) > 0:
                mail_to('SpotBurn Alert',text, EMAIL ,send_to, media)

            # Done with this email delete it
            mailbox.mark_deleted(msg)

if __name__ == "__main__":
    main()