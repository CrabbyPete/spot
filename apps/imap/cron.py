#-------------------------------------------------------------------------------
# Name:        Cron Mail Send an email reminder to user to ask about fishing
# Purpose:
#
# Author:      pdouma
#
# Created:     13/01/2011
# Copyright:   (c) pdouma 2011
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#!/usr/bin/env python

#mail_to(subject, message, from_email, recipient_list, attachments )
from mail import mail_to

def crontab( ):
    # Check if its cron time
    
    # Look up users in the database and add the message
    qry = User.objects.filter()
    spam = []
    for user in qry:
        name = user.get_full_name()
        if user.email != u'':
            spam.append(user.email)
"""
    mail_to ( "Fishing Report",
              "How is the fishing?",
              "fish@spotburn.com",
              spam
             )
"""
i