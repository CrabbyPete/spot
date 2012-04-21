import quopri
import imaplib
import email

import os.path

from password       import gen
from decodeh        import decode_heuristically
from types          import *

# Regular expression to test for valid file name and acceptable extensions
import re
re_file = re.compile ('^[^\\\./:\*\?\"<>\|]{1}[^\\/:\*\?\"<>\|]{0,254}$')
re_extn = re.compile('^.*\.(jpg|JPG|gif|GIF|png|PNG|bmp|BMP|mov|MOV|avi|AVI|mp4|MP4)$')


class MailBox(imaplib.IMAP4):
    mailbox = None

    def __init__(self):
        self.mailbox = imaplib.IMAP4('mail.webfaction.com')

    def login(self, user='', password=''):
        return self.mailbox.login(user, password)

    def new_messages(self):
        try:
            self.mailbox.select("INBOX")
        except:
            return None
        
        try:
            ok, mess = self.mailbox.search(None, "UNDELETED")
        except IMAP4.error:
            return None
        
        if ok == 'OK':
            mess = mess[0].split()
            return mess
        else:
            return None

    def fetch(self, number):
        try:
            ok, data = self.mailbox.fetch(number,'(RFC822)')
        except IMAP4.error,e:
            print str(e)
            return None
        
        if ok =='OK':
            mess = data[0][1]
            mess = email.message_from_string(mess)
            return mess
        else:
            return None

    # Return the file header
    def header(self, mess):
        hed = mess.keys()
        for i in hed:
            print i, mess[i]
        print '**************'
        if mess.has_key("Return-Path"):
            head = mess["Return-Path"]
            head = (head.lstrip('<')).rstrip('>')
        else:
            head = None

        if mess.has_key("Subject"):
            subj = mess["Subject"]
        else:
            subj = None

        if mess.has_key("From"):
            sender = mess["From"]
        else:
            sender = None

        return head, sender, subj

    def mark_deleted(self,number):
        try:
            ok, data  = self.mailbox.store(number, 'FLAGS', '(\Deleted)')
        except IMAP4.error, e:
            print str(e)
            return None
        
        if ok != 'OK':
            return False
        else:
            return True

    def kill(self):
        try:
            ok, data = self.mailbox.expunge()
        except IMAP4.error,e:
            print str(e)
            return False
        
        if ok != 'OK':
            return False
        return True


    def get_text(self, mess):
        text =[]
        html =[]
        char_set = mess.get_charsets()

        for part in mess.walk():
            type    = part.get_content_type()
            charset = part.get_content_charset()
            if type == 'text/plain':
                body = part.get_payload()

                # Determine what character set they use and convert to utf8
                body = quopri.decodestring(body)
                body = decode_heuristically(body, enc = charset, denc = "utf-8")
                if body != None:
                    text.append(body[0])
   
            elif type == 'multipart/alternative':
                body = part.get_payload()
                if isinstance(body,ListType):
                    for b in body:
                        tx,ht = self.get_text(b)
                        text.append(tx)
                        html.append(ht)
                        
                else:
                    body = quopri.decodestring(body)
                    body = quopri.decodestring(body)
                    body = decode_heuristically(body, enc = charset, denc = "utf-8")
                    if body != None:
                        htlm.append(body[0])
                
        return text,html

    def get_media(self, mess, prefix = '', path = os.path.abspath('') ):
        media = []

        # Check path
        """
        if os.path.exists(path) == False:
            return None
        """
        
        # Get each part of the message
        for part in mess.walk():
            d_type = part.get_params(None, 'Content-Disposition')
            if d_type != None:
                attachment = False
                for key,value in d_type:
                    key = key.lower()
                    if key == 'attachment' or key == 'inline':
                        attachment = True;
                    if key == 'filename':
                        image_file,ext = value.split('.');

                if not attachment:
                    continue;
            else:
                c_type = part.get_content_maintype()
                if c_type != 'image':
                    continue

                # Get the subtype
                ext = part.get_content_subtype()
                if ext == 'jpeg':
                    ext = 'jpg'

            # Create a new name to avoid duplicate file names
            image_file = gen(alpha = 8, numeric = 0)
            image_file = path + prefix + image_file + '.' + ext

            # Create a uniqe name
            num_of_trys = 1
            while num_of_trys < 10:
                if os.path.isfile(image_file) == False:
                    break
                else:
                    image_file = image_file.split('.')
                    image_file[0] = image_file[0]+'(' + str(num_of_trys) + ')'
                    image_file = '.'.join(image_file)
                    num_of_trys  = num_of_trys + 1

            # Is this a new name
            if num_of_trys >= 10:
                print "Error: Could not generate a unique name"
                continue

            # Create each file
            try:
                fp = open(image_file, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()

            except IOError:
                print 'File Error: %s' % IOError

            else:
                media.append(image_file)

        return media

    def logout(self):
        self.mailbox.logout()


