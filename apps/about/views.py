
from django.template import                 Context
from django.template.loader import          get_template
from django.http import                     HttpResponse
from django.core.mail import                send_mail,EmailMessage

from about.forms import                     ContactForm
  
def contact_us(request):
    if request.POST:
        form = ContactForm(request.POST)
        if form.is_valid():
            name    = form.cleaned_data['name']  
            name    = 'Info Request:' + name
            email   = form.cleaned_data['email']
            message = form.cleaned_data['text']
 
            send_mail(name, message, email,['info@spotburn.com'], fail_silently=False)

            mail = EmailMessage(name, message, email,'info@spotburn.com' )
            mail.send()

    form = ContactForm()
    c = Context({'form':form})
    t = get_template('about/contact_us.html')
    html = t.render(c)
    return HttpResponse(html)