from django.db import models
from django.contrib.comments.models import Comment
from django.contrib.auth.models import User, Group, Permission
from django.utils.translation import ugettext_lazy as _

#from imagekit.models import ImageModel v. 0.3
from imagekit.models import  ImageSpec
from imagekit.processors import Adjust
from imagekit.processors.resize import Crop



# Zip Code database
class ZipCodes(models.Model):
    city			= models.CharField(max_length=45)
    zip_code        = models.CharField(max_length=15)
    longitude       = models.FloatField()
    state           = models.CharField(max_length =45)
    state_abbr 		= models.CharField(max_length=3)
    latitude		= models.FloatField()

    def __unicode__(self):
	   return self.zipcode

#Mobile Provider
class MobileProvider(models.Model):
    """ MobileProvider model """
    title           = models.CharField(_('title'), max_length=25, blank = True, null = True)
    domain          = models.CharField(_('domain'), max_length=50, unique=True)
    mms				= models.BooleanField(_('mms'), default = False )

    class Meta:
	   verbose_name = _('mobile provider')
	   verbose_name_plural = _('mobile providers')

    class Admin:
	   pass

    def __unicode__(self):
	   return self.domain


class FishSpecies(models.Model):
    common_name     = models.CharField( max_length=40, blank = True)
    genus_species   = models.CharField( max_length=100, blank = True, unique = True)
    image           = models.ImageField( upload_to='fish' , blank = True, null = True)

    class Meta:
	   verbose_name = _('fish')
	   verbose_name_plural = _('fish species')


    def __unicode__(self):
	   if self.common_name != None:
            return self.common_name
	   else:
	       return self.genus_species

# This is the JSON result of a query to Google for a location
# see http://code.google.com/apis/maps/documentation/geocoding/index.html

class GoogleLocation(models.Model):
    #   "address": "1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA"
    address = models.CharField( max_length=100, blank = True)

    #    "CountryNameCode": "US"
    countrynamecode = models.CharField( max_length=100, blank = True, null = True)

    #    "CountryName": "USA"
    countryname     = models.CharField (max_length=100, blank = True, null = True)

    #    "AdministrativeAreaName": "CA",
    adminareaname   = models.CharField( max_length = 100, blank = True, null = True)

    #    "LocalityName": "Mountain View",
    localityname    = models.CharField( max_length = 100, blank = True, null = True)

    #    "ThoroughfareName": "1600 Amphitheatre Pkwy"
    thoroughfare    = models.CharField (max_length = 150, blank = True, null = True)

    #    "PostalCodeNumber": "94043"
    postalcode      = models.CharField ( max_length = 100, blank = True, null = True)

    #    "Accuracy": 8
    #    "coordinates": [ -122.0841430, 37.4219720, 0 ]
    longitude       = models.FloatField( null = True, blank = True)
    latitude        = models.FloatField( null = True, blank = True )

    def __unicode__(self):
       return self.address


#Profile for User class
class SpotUser(models.Model):
    user            = models.ForeignKey(User)
    is_temporary    = models.BooleanField(default = False)
    is_private      = models.BooleanField(default = False)

    mobile          = models.CharField(max_length=15, 	    blank = True, null = True)
    mobile_provider = models.ForeignKey('MobileProvider',   blank = True, null = True)
    phone_addr      = models.EmailField(max_length=60,      blank = True, null = True)
    proxy_email     = models.EmailField(max_length=120,     blank = True, null = True)

    address         = models.CharField(max_length=100, 	blank = True, null = True)
    zipcode         = models.CharField(max_length=15,   blank = True, null = True)

    mugshot         = models.ImageField(upload_to = "profiles", null = True, blank = True)

    birthday        = models.DateField(null = True, blank = True)
    use_email       = models.BooleanField(default = False)
    use_phone       = models.BooleanField(default = False)
    time_off        = models.TimeField(null = True,	blank = True)
    time_on         = models.TimeField(null = True,	blank = True)

    fish            = models.ManyToManyField(FishSpecies, blank = True, null = True)

    fish_method     = models.TextField(blank = True)
    is_pro          = models.BooleanField(default = False)
    web_site        = models.URLField(null = True, blank = True)

    newsletter      = models.BooleanField(default = False)

    def __unicode__(self):
        if self.user.username == u'':
            return str(self.pk)
        return self.user.username

"""
Permissions: admin, user, view
"""
class SpotGroupMembership(models.Model):
    member         = models.ForeignKey(User)
    follow         = models.CharField(max_length = 5, default = 'None')
    permission     = models.CharField(max_length = 5, default = 'user')

    def __unicode__(self):
       return str(self.pk)


class SpotGroupManager(models.Manager):
    def groups_for(self, user):
        groups = []

        qry = self.filter(members__member=user)
        for membership in qry:
            follow = membership.follows_by(user)
            groups.append({'membership':membership, 'follow':follow})

        return groups


class SpotGroup(models.Model):
    name            = models.CharField(max_length=80, unique = True)
    description     = models.TextField(max_length=120, blank=True, null=True)

    members         = models.ManyToManyField( SpotGroupMembership, blank = True, null = True )

    date_created    = models.DateTimeField( auto_now = True )
    profile_pic     = models.ImageField(upload_to = "photos",null = True, blank = True)
    web_site        = models.URLField(unique =True, null = True, blank = True)

    is_private      = models.BooleanField(default = True)

    objects         = SpotGroupManager()

    def __unicode__(self):
	   return self.name

    def __str__(self):
	   return self.__unicode__()

    # Who is the admin
    def admin(self):
        for m in self.members.all():
            if m.permission == 'admin':
                return m.member
        return None

    # Is this user a member of this group
    def is_member(self, user):
        for m in self.members.all():
            if m.member == user:
                return True
        return False

    # How does a user follow this group, set changes the way
    def follows_by(self,user, set = None):
        for m in self.members.all():
            if m.member == user:
                if set != None:
                    m.follow = set
                    m.save()
                return m.follow

        return None

    # Return the list of members
    def get_members(self):
        membership = []
        for m in self.members.all():
            membership.append(m.member)
        return membership

    def new_member(self,user, permission):
        member = SpotGroupMembership(member = user, permission = permission)
        member.save()
        self.members.add(member)
        self.save()
        return self

    def remove_member(self, user):
        for m in self.members.all():
            if m.member == user:
                m.delete()
        return self

# Class for each photo, uses ImageKit

from EXIF   import  process_file
from coord  import  get_GPS


class SpotPhoto(models.Model):
    image           = models.ImageField( upload_to='photos/' )
    thumbnail       = ImageSpec( [ Adjust(contrast=1.2, sharpness=1.1),
                                   Crop(74,53)
                                 ],
                                 image_field='image', format='JPEG',
                                )
    title           = models.CharField( max_length=100, unique = True )
    caption         = models.TextField( blank=True )

    date_taken      = models.DateTimeField( blank = True , null = True )

    longitude       = models.FloatField( null = True, blank = True )
    latitude        = models.FloatField( null = True, blank = True )

    is_public       = models.BooleanField( default=True )
    views           = models.PositiveIntegerField( default=0, editable=False )


    def __unicode__(self):
	   return self.title

    def __str__(self):
	   return self.__unicode__()

    def set_exif(self):
        data = process_file(self.image, details = True, debug = False )
        if not data:
            return False

        # See if the date the image was taken is available
        if data.has_key('Image DateTime'):
            datetime = data['Image DateTime']
            self.date_taken = datetime.values.replace(':','-',2)

        # See if GPS data is available and if so convert to decimal for Google Map
        self. longitude, self.latitude = get_GPS(data)
        
        # Check orientation
        if data.has_key( 'Image Orientation' ):
            orient = data['Image Orientation']
            if orient.printable:
                return orient.__str__()
            
        return 0


class SpotMessageManager(models.Manager):

    # Get all messages for a user, latest one first
    def for_user(self, user, start = 0, end = None, friends = [] ):
        if isinstance(user, SpotGroup):
            m = self.filter(group = user).order_by('date_added').reverse()
        else:
            m = self.filter(user = user).order_by('date_added').reverse()
            for friend in friends:
                f = friend['friend']
                m = m | self.filter(user = f).order_by('date_added').reverse()

        if end == None:
            end == m.count()
        more = m.count()
        m = m[start:end]

        if end >= more:
            end = False
        if start <= 0:
            start = False

        return m,start,end

    # Get all messages within a given range, return if next or previous
    def get_all(self, start = 0, end = None):
        m = self.order_by('date_added').reverse()
        if end == None:
           end == m.count()

        more = m.count()
        m = m[start:end]

        if end >= more:
            end = False
        if start <= 0:
            start = False

        return m,start,end


# Class for every message
class SpotMessage(models.Model):
    user            = models.ForeignKey(User)
    group           = models.ForeignKey(SpotGroup, null = True, blank = True)

    text            = models.TextField(blank = True)
    date_added      = models.DateTimeField( auto_now = True )
    is_public       = models.BooleanField( default=True )
    views           = models.PositiveIntegerField( default=0, editable=False)

    longitude       = models.CharField( max_length=100, blank = True)
    latitude        = models.CharField( max_length=100, blank = True)

    photos          = models.ManyToManyField(SpotPhoto)

    objects = SpotMessageManager()

    class Meta:
	   ordering = ['-date_added']
	   get_latest_by = 'date_added'

    def __unicode__(self):
	   return str(self.id)

    def __str__(self):
	   return self.__unicode__()


class SpotComment( Comment ):
    photos          = models.ManyToManyField(SpotPhoto)
    
    longitude       = models.CharField( max_length=100, blank = True)
    latitude        = models.CharField( max_length=100, blank = True)

