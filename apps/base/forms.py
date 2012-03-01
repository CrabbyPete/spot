from django import  forms
from django.forms import  ModelForm
from django.forms.extras.widgets import SelectDateWidget

from django.utils.translation import ugettext_lazy as _
from django.contrib.localflavor.us.forms import USPhoneNumberField, USZipCodeField

from base.models import *

# This was replaced in the __init__ of SignUpForm
CARRIER_CHOICES = ((" ","Unknown"))

class SignUpForm(forms.Form):

    name            = forms.RegexField  ( label = 'User Name:',
                                            required = False,
                                            max_length=45,
                                            regex=r'^((\w((\s|\@|\!){0,1})){2,})+$',
                                            error_message = _("Minimum 2 character. Numbers, underscores, and one space are allowed"),
                                            widget= forms.TextInput(attrs={'class':'supf','size':40} )
                                        )

    mobile          = USPhoneNumberField( required = False,
                                            widget = forms.TextInput(attrs={'class':'supf','size':15})
                                         )

    carrier         = forms.ChoiceField( required = False,
                                            choices=(),
                                            widget=forms.Select( attrs={'class':'supf'})
                                        )

    password        = forms.CharField   ( max_length = 45,
                                            widget = forms.PasswordInput(attrs={'class':'supf','size':35} )
                                        )

    pass_confirm    = forms.CharField   ( max_length = 45,
                                            widget = forms.PasswordInput(attrs={'class':'supf','size':35} )
                                        )

    email           = forms.EmailField  ( required = False,
                                            max_length = 60,
                                            widget= forms.TextInput(attrs={'class':'supf','size':40})
                                        )

    first_name      = forms.RegexField  ( required = False,
                                            max_length =45, regex=r'^[a-zA-Z]+$',
                                            error_message = _("Only letters are allowed; 3 letters at least"),
                                            widget = forms.TextInput(attrs={'class':'supf','size':40})
                                        )

    last_name       = forms.RegexField  ( required = False,
                                            max_length = 45,
                                            regex=r'^[a-zA-Z]+$',
                                            error_message = _("Only letters are allowed"),
                                            widget = forms.TextInput(attrs={'class':'supf','size':40})
                                        )

    address        = forms.RegexField  ( required = False,
                                            max_length = 45,
                                            regex=r"^[a-zA-Z0-9,' ']+$",
                                            error_message = _("Only letters numbers and commas"),
                                            widget = forms.TextInput(attrs={'class':'supf','size':40})
                                        )


    zip             = USZipCodeField    ( required = False,
                                            widget= forms.TextInput(attrs={'class':'supf'})
                                        )

    #Check this in the code, set required to false so it can be used by editprofile
    agree           = forms.BooleanField( initial = True,
                                            required = False,
                                            widget = forms.CheckboxInput(attrs={'class':'supf'})
                                        )
    
    #Check this in the code, set required to false so it can be used by editprofile
    facebook        = forms.BooleanField( initial = False,
                                            required = False,
                                            widget = forms.CheckboxInput(attrs={'class':'supf'})
                                        )


    newsletter      = forms.BooleanField( required = False,
                                            widget = forms.CheckboxInput(attrs={'class':'supf'})
                                        )

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.fields['carrier'].choices = [('', 'Unknown')] + [(c.domain, c.title) for c in MobileProvider.objects.all()]
        pass

class LoginForm(forms.Form):
    username        = forms.CharField   ( max_length = 45,
                                            widget = forms.TextInput(attrs={'class':'txtBox1','size':19, 'id':'user',
                                            'value':"User Name or Email Address",
                                            'onfocus':"if(this.value == 'User Name or Email Address')this.value = ''",
                                            'onblur' :"if(this.value == '') this.value = 'User Name or Email Address'"}
                                        )
                                        )
    password        = forms.CharField   ( max_length = 45,
                                            widget = forms.PasswordInput(attrs={'class':'txtBox1','size':19,
                                            'value':"Password",
                                            'onfocus':"if(this.value == 'Password')this.value = ''",
                                            'onblur' :"if(this.value == '') this.value = 'Password'"})
                                        )


class ProfileForm(SignUpForm):

    mugshot         = forms.ImageField      (required = False)

    birthday        = forms.DateField       (required = False,
                                                widget=SelectDateWidget(years=range(1920, 2008))
                                            )

    use_email       = forms.BooleanField    ( required = False,
                                                widget = forms.CheckboxInput( attrs={'id':"CheckboxGroup1_0"})
                                            )
    use_phone       = forms.BooleanField    (required = False,
                                                widget = forms.CheckboxInput( attrs={'id':"CheckboxGroup1_0"})
                                            )
    time_off        = forms.TimeField       (required = False)
    time_on         = forms.TimeField       (required = False)

#    fish            = forms.ModelMultipleChoiceField(queryset=FishSpecies.objects.all())

    fish_method     = forms.CharField       ( required = False,
                                                widget = forms.Textarea(attrs={'cols':40, 'rows':10, 'id':'fish_method'})
                                            )
    is_private      = forms.BooleanField    (required = False,
                                                widget = forms.CheckboxInput( attrs={'id':'CheckboxGroup1_0'})
                                            )
    is_pro          = forms.BooleanField    ( required = False,
                                                widget = forms.CheckboxInput( attrs={'id':'CheckboxGroup1_0'})
                                            )
    web_site        = forms.URLField        (required = False,
                                                widget = forms.TextInput (attrs ={'id':"web_site"})
                                            )

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)

class GroupEditForm(forms.Form):
    upload          = forms.ImageField      ( required = False
                                            )
    group_name      = forms.CharField       ( required = True,
                                                max_length = 45,
                                                widget = forms.TextInput( attrs = {'size':40})
                                            )
    description     = forms.CharField       ( required = False,
                                                max_length = 120,
                                                widget = forms.Textarea ( attrs = {'cols':40, 'rows':3 })
                                            )
    web_site        = forms.URLField        ( required = False,
                                                widget = forms.TextInput (attrs ={'size':40,'id':"web_site"})
                                            )

class MessageEditForm(forms.Form):
    text       = forms.CharField            ( required = False,
                                                widget = forms.Textarea(attrs={'cols':70, 'rows':4})
                                             )

    date_added = forms.DateField            ( required = False,
                                                widget=SelectDateWidget()
                                            )

class CommentForm(forms.Form):
    text       = forms.CharField            ( required = False,
                                                widget = forms.Textarea(attrs={'cols':'','rows':'','class':'msg'})
                                            )

    picture    = forms.ImageField           ( required = False )

    location   = forms.RegexField           ( required = False,
                                                max_length = 45,
                                                regex=r"^[a-zA-Z0-9,' ']+$",
                                                error_message = _("Only letters numbers and commas"),
                                                widget = forms.TextInput(attrs={'class':'supf','size':50,
                                                'value':'Address or Longitude and Latitude',
                                                'onfocus':"if(this.value == 'Address or Longitude and Latitude')this.value = ''",
                                                'onblur' :"if(this.value == '') this.value = 'User Name or Email Address'"})
                                            )

class PostAddForm (forms.Form):
    for_group   = forms.BooleanField       ( initial = False,
                                                required = False,
                                                widget = forms.CheckboxInput(attrs={'class':'supf'})
                                            )
    group_name      = forms.CharField       ( required = False,
                                                max_length = 45,
                                                widget = forms.TextInput( attrs = {'size':40})
                                            )
    
    text        = forms.CharField          ( required = True,
                                                widget = forms.Textarea(attrs={'cols':'70','rows':'8','class':'msg'})
                                            )
    picture_1    = forms.ImageField        ( required = False )
    
    caption_1    = forms.CharField         ( required = False,
                                                widget = forms.Textarea(attrs={'cols':'70','rows':'2','class':''})
                                           )
   
    picture_2    = forms.ImageField        ( required = False )
    
    caption_2    = forms.CharField         ( required = False,
                                                widget = forms.Textarea(attrs={'cols':'70','rows':'2','class':''})
                                           )
    picture_3    = forms.ImageField        ( required = False )
    
    caption_3    = forms.CharField         ( required = False,
                                                widget = forms.Textarea(attrs={'cols':'70','rows':'2','class':''})
                                           )
    picture_4    = forms.ImageField        ( required = False )
    
    caption_4    = forms.CharField         ( required = False,
                                                widget = forms.Textarea(attrs={'cols':'70','rows':'2','class':''})
                                           )
 

    