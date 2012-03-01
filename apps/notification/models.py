# For now I have stubbed out django-notices to keep it simple and fit in our HTML/CSS

from django.db import models

from django.template import Context
from django.template.loader import render_to_string

from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _


class NoticeManager(models.Manager):
    def notices_for(self, user):
        return self.filter(user=user)

    def notices_by(self, user):
        return self.filter(sent_by=user)

    def unseen_for(self, user):
        return self.filter(user=user).filter(unseen=True)

class Notice(models.Model):
    user        = models.ForeignKey(User, verbose_name=_('user'))
    sent_by     = models.ForeignKey(User, related_name =_('sent_by'))
    message     = models.TextField(_('message'))
    notice_type = models.CharField(_('notice_type'),max_length = 30)
    added       = models.DateTimeField(_('added'), auto_now = True )
    unseen      = models.BooleanField(_('unseen'), default=True)

    objects = NoticeManager()

    def __unicode__(self):
        return self.message

    def is_unseen(self):
        """
        returns value of self.unseen but also changes it to false.

        Use this in a template to mark an unseen notice differently the first
        time it is shown.
        """
        unseen = self.unseen
        if unseen:
            self.unseen = False
            self.save()
        return unseen

    class Meta:
        ordering = ["-added"]
        verbose_name = _("notice")
        verbose_name_plural = _("notices")

def notice_send( sent_by, sent_to, label, extra_context=None, email = None):
    file = 'notification/%s.txt' % label
    context = Context(extra_context)
    context.autoescape = False
    message  = render_to_string( file, dictionary=context)

    # Strip newlines from subject
    subject = 'SpotBurn Notice'

    notice = Notice.objects.create( user=sent_to,
                                    sent_by = sent_by,
									message=message,
									notice_type = label
								   )


    if email != None:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, email )
