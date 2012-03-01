from django import  forms
from django.forms import  ModelForm

from django.utils.translation import ugettext_lazy as _
from django.contrib.localflavor.us.forms import USPhoneNumberField, USZipCodeField

from friends.models import *

class FindFriendsForm(forms.Form):

    user       = forms.CharField( required = False,
                                    max_length = 45,
                                    widget = forms.TextInput(attrs={'class':'myrp','size':28})
                                )


    interest   = forms.RegexField( required = False,
                                    max_length =45, regex=r'^[a-zA-Z]+$',
                                    error_message = _("Only letters are allowed; 3 letters at least"),
                                    widget = forms.TextInput(attrs={'class':'myrp','size':28})
                                 )

    location    = forms.CharField( required = False,
                                    max_length = 45,
                                    widget = forms.TextInput(attrs={'class':'myrp','size':28})
                                 )


class InviteFriendsForm(forms.Form):

    email       = forms.EmailField( required = False,
                                        max_length = 60,
                                        widget= forms.TextInput(attrs={'class':'myrp','size':33})
                                  )

    phone       = USPhoneNumberField( required = False,
                                        widget = forms.TextInput(attrs={'class':'myrp','size':16})
                                    )

    message     = forms.CharField( required = False,
                                    max_length = 100,
                                    widget = forms.Textarea(attrs={'class':'myrp','cols':34,'rows':5})
                                 )
