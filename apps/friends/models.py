import datetime
from random import random

from django.db import models

from django.template.loader import render_to_string
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User, AnonymousUser
from django.contrib.sites.models import Site
from django.utils.hashcompat import sha_constructor

from django.db.models import signals
from django.core.mail import send_mail

from notification.models import *


from django.conf import settings


class Contact(models.Model):
    """
    A contact is a person known by a user who may or may not themselves
    be a user.
    """

    # the user who created the contact
    user = models.ForeignKey(User, related_name="contacts")

    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()
    added = models.DateField(default=datetime.date.today)

    # the user(s) this contact correspond to
    users = models.ManyToManyField(User)

    def __unicode__(self):
        return "%s (%s's contact)" % (self.email, self.user)


class FriendshipManager(models.Manager):

    # My friends and how I follow them
    def friends_for_user(self, user):
        friends = []
        for friendship in self.filter(from_user=user):
            friends.append({"friend": friendship.to_user, "follow": friendship.from_follow})
        for friendship in self.filter(to_user=user):
            friends.append({"friend": friendship.from_user, "follow": friendship.to_follow})
        return friends

    # Used to see who are my friends and how they follow me 
    def friends_who_follow(self, user):
        friends = []
        for friendship in self.filter(from_user=user):
            friends.append({"friend": friendship.to_user, "follow": friendship.to_follow})
        for friendship in self.filter(to_user=user):
            friends.append({"friend": friendship.from_user, "follow": friendship.from_follow})
        return friends


    def are_friends(self, user1, user2):
        if isinstance(user1, AnonymousUser) or isinstance(user2, AnonymousUser):
            return False
        if self.filter(from_user=user1, to_user=user2).count() > 0:
            return True
        if self.filter(from_user=user2, to_user=user1).count() > 0:
            return True
        return False

    def follows( self, user1, user2):
        qry = self.filter(from_user=user1, to_user=user2)

        # if no match flip users
        if qry.count() <= 0:
            qry = self.filter(from_user=user2, to_user=user1)
            if qry.count() <= 0:
                return None

        friendship = qry.get()
        return friendship

FOLLOW_STATUS = (
    ("None"),
    ("email"),
    ("phone"),
    ("web only"),
)


class Friendship(models.Model):
    """
    A friendship is a bi-directional association between two users who
    have both agreed to the association.
    """

    to_user      = models.ForeignKey(User, related_name="friends")
    to_follow    = models.CharField(max_length = 5, default = 'None')

    from_user    = models.ForeignKey(User, related_name="_unused_")
    from_follow  = models.CharField(max_length = 5, default = 'None')

    # @@@ relationship types
    added = models.DateField(default=datetime.date.today)

    objects = FriendshipManager()

    class Meta:
        unique_together = (('to_user', 'from_user'),)



def friend_set_for(user):
    return set([obj["friend"] for obj in Friendship.objects.friends_for_user(user)])


INVITE_STATUS = (
    ("1", "Created"),
    ("2", "Sent"),
    ("3", "Failed"),
    ("4", "Expired"),
    ("5", "Accepted"),
    ("6", "Declined"),
    ("7", "Joined Independently")
)

class JoinInvitationManager(models.Manager):

    def send_invitation(self, from_user, to_email, message):
        contact, created = Contact.objects.get_or_create(email=to_email, user=from_user)

        salt = sha_constructor(str(random())).hexdigest()[:5]
        confirmation_key = sha_constructor(salt + to_email).hexdigest()
        url = reverse("base_signup")
        accept_url = settings.SITE_BASE + url

        subject = "An Invitation To Join SpotBurn.com"

        email_message = render_to_string("friends/join_invite_message.txt", {
            "user": from_user,
            "message": message,
            "accept_url": accept_url,
        })

        send_mail(subject, email_message, settings.DEFAULT_FROM_EMAIL, [to_email])
        invite = self.create(from_user=from_user, contact=contact, message=message, status="2", confirmation_key=confirmation_key)

        notice_send(from_user, from_user, "join_request", {"to": to_email})

        return invite

class JoinInvitation(models.Model):
    """
    A join invite is an invitation to join the site from a user to a
    contact who is not known to be a user.
    """

    from_user = models.ForeignKey(User, related_name="join_from")
    contact = models.ForeignKey(Contact)
    message = models.TextField()
    sent = models.DateField(default=datetime.date.today)
    status = models.CharField(max_length=1, choices=INVITE_STATUS)
    confirmation_key = models.CharField(max_length=40)

    objects = JoinInvitationManager()

    def accept(self, new_user):
        # mark invitation accepted
        self.status = 5
        self.save()
        # auto-create friendship
        friendship = Friendship(to_user=new_user, from_user=self.from_user)
        friendship.save()

        notice_send(new_user, self.from_user, "join_accept", {"invitation": self, "new_user": new_user})
        """
            friends = []
            for user in friend_set_for(new_user) | friend_set_for(self.from_user):
                if user != new_user and user != self.from_user:
                    friends.append(user)
            notice_send(friends, "friends_otherconnect", {"invitation": self, "to_user": new_user})
        """

class FriendshipInvitation(models.Model):
    """
    A frienship invite is an invitation from one user to another to be
    associated as friends.
    """

    from_user = models.ForeignKey(User, related_name="invitations_from")
    to_user = models.ForeignKey(User, related_name="invitations_to")
    message = models.TextField()
    sent = models.DateField(default=datetime.date.today)
    status = models.CharField(max_length=1, choices=INVITE_STATUS)

    def request(self):
        self.status = 2
        self.save()

        notice_send(self.from_user, self.to_user, "friends_invite", {"invitation": self})

    def accept(self):
        if not Friendship.objects.are_friends(self.to_user, self.from_user):
            friendship = Friendship(to_user=self.to_user, from_user=self.from_user)
            friendship.save()
            self.status = 5
            self.save()

            notice_send(self.to_user,self.from_user, "friends_accept", {"invitation": self})

            """
                for user in friend_set_for(self.to_user) | friend_set_for(self.from_user):
                    if user != self.to_user and user != self.from_user:
                        notice_send([user], "friends_otherconnect", {"invitation": self, "to_user": self.to_user})
            """
