from django import  forms

class ContactForm(forms.Form):
    name    = forms.CharField   ( required = True, 
                                  max_length = 45,
                                  widget = forms.TextInput( attrs = {'size':45} )                          
                                 )
    
    email   = forms.EmailField  ( required = False,
                                  max_length = 60,
                                  widget= forms.TextInput(attrs={'class':'supf','size':45})
                                 )
    
    text    = forms.CharField   ( required = False,
                                  widget = forms.Textarea(attrs={'cols':40, 'rows':7})
                                 )

    