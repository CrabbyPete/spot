import django_header
import settings

import time, re

import logging
LOGGER = logging.getLogger('django.request')

from os.path                    import join, split
from PIL                        import Image

EMAIL  = 'fish@coastalflyrodders.com'
PHOTOS = join(settings.MEDIA_ROOT, 'photos/')

from django.core.mail           import EmailMessage, EmailMultiAlternatives
from django.contrib             import auth
from django.contrib.auth.models import User
from django.template            import loader, Context

# Import local stuff
from imap                       import MailBox
from base.models                import SpotUser, SpotPhoto, SpotMessage, SpotGroup
from friends.models             import Friendship
from notification.models        import notice_send
from pycron                     import pycron

# Pre-compiled regular expressions
re_mobile = re.compile('[0-9]{10}')
re_email  = re.compile('^[\w\.=-]+@[\w\.-]+\.[\w]{2,3}$')


def mail_to(subject, message, from_email, recipient_list, attachments ):
    """ This is send_mail, but adds attachments
    """
    mail = EmailMessage(subject, message, from_email, recipient_list )
    for attach in attachments:
        mail.attach_file(attach)
    mail.send()

def cronjob(job):
    """ Check if the cron timer went off
        job is the string of the job name
    """
    if len(job) == 0 or job[0] != 'fish':
        return

    print 'Mailing @' + time.strftime("%I:%M:%S %p", time.localtime()) 
    
    # For now only send to me
    qry = User.objects.filter(username = 'CrabbyPete')# make this ()
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
        c = Context({'name':name, 'url':settings.SITE_BASE})
        text = loader.get_template('anyfish.txt').render(c)
        html = loader.get_template('anyfish.html').render(c)
  
        msg = EmailMultiAlternatives("How's the fishing?", text, EMAIL, spam )
        msg.attach_alternative(html, "text/html")
        try:
            msg.send(fail_silently = False)
        except Exception, error:
            err_msg =  'Email error: %s'% str(error)
            print err_msg
            LOGGER.error(err_msg)
    return
        

def email_parts( mailbox, msg_num, em ):
    """ Get the message, text, html,and media parts
    """
    text, html  = mailbox.get_text(msg_num)
    
    tag, domain = em.split('@')
    media = mailbox.get_media( msg_num, prefix = tag+'-',  path = PHOTOS )
    
    if text:
        if isinstance(text, list):
            if isinstance(text[0], list):
                text = text[0]
                        
            text = ' '.join(text)
 
            # Dump the reply part of the message
            if '----- Original Message -----' in text:
                text, dmp = text.split('----- Original Message -----')
 
    return text, html, media

PHOTO_TYPES = ['jpg', 'png', 'gif']      
def main():
    """ Checks mailbox and sends valid messages to the database
    """
    mailbox = MailBox()
    mailbox.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    
    # Set the cron job to send mail every week Mon at 12:00AM
    cron = pycron(latency = 240)
    jobs = cron.add_job(' 0 0 0 * * * ', 'fish','fish')
#    jobs = cron.add_job(' 0 * * * * * ', 'fish','anyfish')
    if not jobs:
        print "Cron job not added"
    else:
        print "Cron jobs"
        cron.print_jobs()
    # When this goes off string 'fish' will be passed to cron goes off @ 12:00AM
 
    
    # Continually poll
    while True:

        # Gets the mail list: If nothing there quit in order to clean up
        mail_msgs = mailbox.new_messages()
        if not mail_msgs or len(mail_msgs) == 0:
            mailbox.kill()
            time.sleep(30)
            jobs = cron.get_matched_jobs()
            cronjob( jobs )
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
            
                # Now look up sender in the database and add the message
                try:
                    profile = SpotUser.objects.get( mobile = pn )
                except Exception:
                    usr = None
                else:
                    usr = profile.user
                
            # No its just a regular email address
            elif em != None:
                print "Message from: "+em
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
    
            # Get the message parts
            text, html, media = email_parts( mailbox, msg_num, em )
            if text:
                message.text = text
            message.save()

            # Save each image, with this message.
            if media:
                for img in media:
                    
                    # Just get the file name and the relative url
                    path, title = split(img)
                    path = join('photos//', title)
                    photo = SpotPhoto( image = path, title = title )
                    
                    # Get the exif data before you adjust the photo
                    rotate = photo.set_exif()

                    # Resize the image and convert to jpeg
                    name = title.split('.')
                    img_type = name[-1].lower()
                    if img_type in PHOTO_TYPES:
                        ms = Image.open(img)
                        """ Check Orientation
                        1: 'Horizontal (normal)',
                        2: 'Mirrored horizontal',
                        3: 'Rotated 180',
                        4: 'Mirrored vertical',
                        5: 'Mirrored horizontal then rotated 90 CCW',
                        6: 'Rotated 90 CW',
                        7: 'Mirrored horizontal then rotated 90 CW',
                        8: 'Rotated 90 CCW'}),
                        """
                        if rotate != 0:
                            if '90' in rotate:
                                if 'CW' in rotate:
                                    ms = ms.rotate(270)
                                elif 'CCW' in rotate:
                                    ms = ms.rotate(90)
                            elif '180' in rotate:
                                ms = ms.rotate(180) 
                        
                        size = 400, 400
                        ms.thumbnail(size, Image.ANTIALIAS)
                        ms.save(img)

                    try:
                        photo.save()
                    except Exception, error:
                        err_msg = 'Photo %s failed to save because %s'% ( title, str(error) )
                        print err_msg
                        LOGGER.error(err_msg)
                    else:
                        message.photos.add(photo)
                        try:
                            message.save()
                        except Exception, error:
                            err_msg = 'Photo %s failed to save to message because %s'% (title, str(error)) 
                            print err_msg
                            LOGGER.error(err_msg)
    
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
                        
                        notice_send(usr, member, "message_for_group", {'group':group})

            # Find my friends and send them a notice and email, or MMS
            else:
                friends = Friendship.objects.friends_who_follow(usr)
                for person in friends:
                    friend = person['friend']
                    notice_send(usr, friend, "message_from_friend", {'user':friend})
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
                subject = 'SpotBurn Message From %s %s'% ( usr.first_name, usr.last_name )
                mail_to( subject, text, EMAIL, send_to, media )

            # Done with this email delete it
            mailbox.mark_deleted(msg)

if __name__ == "__main__":
    main()
