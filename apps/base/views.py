
from os.path    import                      abspath, dirname, join, split, exists

from django.contrib.auth.models import      User

from django.template import                 Context
from django.template.loader import          get_template
from django.http import                     HttpResponse, HttpResponseRedirect
from django.db.models import                Q
from django.forms.util import               ErrorList

from django.contrib import                  auth
from django.shortcuts import                render_to_response
from django.views.generic.simple import     direct_to_template
from django.template import                 RequestContext

from django.core.mail import                EmailMessage

from django.contrib.sessions.backends.base    import SessionBase
# Used for the django Comment framework
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import     Site

# Python Imaging Library 
from PIL            import                  Image
from PIL.ExifTags   import                  TAGS


from base.forms import                      *
from base.models import                     *
from base.geo import                        *

from friends.models import                  *
from notification.models import             *

import settings
import simplejson

# Return Message for display default = 0-20f
def message_list( user = None, start = 0, end = None, friends =[] ):
    m = []
    
    # If this user is anonymous get the messages, don't show private or group messages
    if user == None:
        messages,prev,next  = SpotMessage.objects.get_all(start,end)
        for message in messages:
            if message.user.get_profile().is_private:
                continue;
            if message.group == None:
                m.append(message)
    else:
        m,prev,next = SpotMessage.objects.for_user(user,start,end, friends)

    return m,prev,next


MESSAGE_SPAN = 15
# Get the previous messages
def next_messages(request):
    end = int(request.GET['message'])
    end += MESSAGE_SPAN
    start = end - MESSAGE_SPAN
    if request.GET.has_key('show' ):
        show = request.GET['show']
        if show == 'on':
            show = True
        else:
            show = False
    else:
        show = False
    return homepage(request, start, end, show)

# Get the next messages
def prev_messages(request):
    start = int(request.GET['message'])
    start = start - MESSAGE_SPAN
    if start < 0:
        start = 0
    end = start + MESSAGE_SPAN
    if request.GET.has_key('show' ):
        show = request.GET['show']
        if show == 'on':
            show = True
        else:
            show = False
    else:
        show = False
    return homepage(request, start, end, show)

from django.contrib.sessions.models import Session

# The default home page.
def homepage(request, start = 0, end = MESSAGE_SPAN, showfriends = False ):
    profile = None
    if request.user.is_authenticated():
        try:
            profile = request.user.get_profile()
        except:
            pass
    
    login = LoginForm()
    mess,prv,nxt = message_list(None, start, end)

    c = Context({'messages':mess, 'nxt':nxt, 'prv':prv, 'lform':login, 'profile':profile})
    # t = get_template('index.html')
    # html = t.render(c)
    # return HttpResponse(html)
    
    return render_to_response('index.html', c, context_instance=RequestContext(request))

  

def my_page(request, start = 0, end = MESSAGE_SPAN, showfriends = False ):
    
    # If the user is already logged in default to their page
    user = request.user
    if user.is_authenticated():
        try:
            profile = request.user.get_profile()

        # This should only happen for the admin, but who knows
        except SpotUser.DoesNotExist:
            profile = SpotUser(user = user)
            profile.save()

        # Display my page
 #       friends = friend_set_for(user)
        friends = Friendship.objects.friends_for_user(user)
        groups = SpotGroup.objects.groups_for(user)
        notices = Notice.objects.notices_for(user)

        if showfriends:
            mess,prv,nxt = message_list(user, start, end, friends )
        else:
            mess,prv,nxt = message_list(user, start, end )

        c = Context(    {'profile':profile,
                        'friends':friends,
                        'groups':groups,
                        'notices':notices,
                        'messages':mess,
                        'nxt':nxt,
                        'prv':prv,
                        'showfriends':showfriends,
                        }
                    )

#      t = get_template('mypage.html')
#       html = t.render(c)
        return render_to_response('mypage.html', c, context_instance=RequestContext(request))

    

def view_all( response ):
    show = response.GET['show']
    if show == 'on':
        show = False
    else:
        show = True
    return homepage(response, 0, 15, show)



def submit_signup_form( request, signup = None, login = LoginForm()):

    if signup == None:
        signup = SignUpForm()
        
    c = Context({'form':signup,'lform':login})
    return render_to_response('signup.html', c, context_instance=RequestContext(request))

def login(request):
    return submit_signup_form(request)

def signup(request):
    form = SignUpForm(request.POST)
    if not form.is_valid():
        return submit_signup_form(request, signup = form)

    # Create a user, make sure its long enough
    name = form.cleaned_data['name']

    # Check password input
    password = form.cleaned_data['password']
    pass_confirm = form.cleaned_data['pass_confirm']
    if password != pass_confirm:
        form._errors['password'] = ErrorList(['The passwords do not match'])
        return submit_signup_form(request, signup = form)

    # Get the email address and double check it to make sure its unique
    email = form.cleaned_data['email']
    if email != u'':
        qry = User.objects.filter(email = email)
        if qry.count() >= 1: 
            form.errors['email'] = "This email is in use"
            return submit_signup_form(request, signup = form)

    # Get the phone number and remove the dashes
    mobile = form.cleaned_data['mobile']
    if mobile != u'':
        number = mobile.split('-')
        mobile = number[0]+number[1]+number[2]
        if SpotUser.objects.filter(mobile = mobile):
            form.errors['mobile'] = "This phone number is in use"
            return submit_signup_form(request, signup = form)

    # Add the carrier
    domain = form.cleaned_data['carrier']

    # Make sure you have one of the following
    if (name is u'') and ( email is u'') and (mobile is u''):
        form._errors['name']   =  ErrorList(["At least a username, email, or phone is required"])
        form._errors['email']  =  ErrorList(["At least a username, email, or phone is required"])
        form._errors['mobile'] = ErrorList(["At least a username, email, or phone is required"])
        return submit_signup_form(request, signup = form)

    # Set the user name to the one thing and if not username set to temporary
    if name is u'':
        is_temporary = True
        if email != u'':
            name = email
        else:
            name = mobile
    else:
        is_temporary = False

    # Check if  email is unique
    qry = User.objects.filter(email = email)
    
    
    # Create the user
    try:
        user  = User.objects.create_user(username=name, email = email, password=password)
    except:
        form._errors['name'] = ErrorList(['This name has already been used'])
        return submit_signup_form(request, signup = form)

    user.first_name = form.cleaned_data['first_name']
    user.last_name = form.cleaned_data['last_name']
    user.save()

    # Create profile
    profile = SpotUser(user = user)
    profile.is_temporary = is_temporary
    zip = form.cleaned_data['zip']
    address = form.cleaned_data['address']

    if zip != u'' and address == u'':
        profile.zipcode = zip
        try:
            addr = ZipCodes.objects.get(Q(zip_code = zip))
            profile.address = addr.city +', '+ addr.state_abbr
        except:
            pass
    elif address != u'':
        local = geocode(address)
        if local != None:
            if 'address' in local:
                profile.address = local['address']
        else:
            profile.address = address

    profile.newsletter = form.cleaned_data['newsletter']
    profile.phone_addr = ' '
    # Get the mobile number
    if mobile != u'':
        profile.mobile = mobile
        if domain != u'':
            profile.phone_addr = mobile +'@'+domain

    profile.save()

    # Login the new user
    user = auth.authenticate(username=user.username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)

    # Check for invitations to join
    contacts = Contact.objects.filter ( email = email )
    for contact in contacts:
        for invite in contact.joininvitation_set.all():
            invite.accept(user)

    if form.cleaned_data['facebook']:
        fb = request.facebook
        url = fb.get_login_url()
        return HttpResponseRedirect(url)
   
    return homepage(request)

# Sign up or Login
def signin(request):

    # If this was a GET, its the first time the form is called
    if request.method == 'GET':
        submit_signup_form(request)
    
    # POST the form was submitted
    lform = LoginForm(request.POST)
    if not lform.is_valid():
        return submit_signup_form(request,login = lform)
    
    # Get the name and password and login
    name     = lform.cleaned_data['username']
    password = lform.cleaned_data['password']
    try:
        user = User.objects.get(Q(username = name)|Q(email = name))
    except User.DoesNotExist:
        # Check if they used a phone number
        try:
            spotuser = SpotUser.objects.get(mobile = name)
            user = spotuser.user
        except SpotUser.DoesNotExist:
            lform._errors['username']  = ErrorList(["User does not exist or wrong password"])

            return submit_signup_form(request,login = lform)
        
    user = auth.authenticate(username=user.username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
        return my_page(request)
    else:
        lform._errors['username']  = ErrorList(["User does not exist or wrong password"])
        return submit_signup_form(request, login = lform)

def editprofile(request):

    # Resubmit the form if errors, or just the first time
    def submit_form():
        c = Context( {'form':form,
                      'profile':profile,
                      'friends':friends,
                      'messages':m
                      }
                    )
        return render_to_response('mypage_edit.html', c, context_instance=RequestContext(request))


    # Need to know what user this is
    user = request.user
    profile = user.get_profile()
    friends = friend_set_for(user)
    m,p,n = message_list(user)

    # Set up a default password, to see if the user tried to change passwords
    default_password ='3dhl4df6ajhhd9ir'

    # Here for the first time, show the currents values
    if not request.POST:
        data = {'name':user.username,
                'password':default_password,
                'pass_confirm':default_password,
                'mobile':profile.mobile,
                'carrier':profile.mobile_provider,
                'email':user.email,
                'first_name':user.first_name,
                'last_name':user.last_name,
                'address':profile.address,
                'zip':profile.zipcode,
                'newsletter':profile.newsletter,
                'mugshot':profile.mugshot,
                'birthday':profile.birthday,
                'use_email':profile.use_email,
                'use_phone':profile.use_phone,
                'time_off':profile.time_off,
                'time_on':profile.time_on,
                'fish_method':profile.fish_method,
                'is_pro':profile.is_pro,
                'web_site':profile.web_site
                }
        form = ProfileForm(data)
        return submit_form()

    #POST: Get the form data and change the values
    form = ProfileForm(request.POST)
    if not form.is_valid():
        return submit_form()

    # Check for file uploads
    if 'mugshot' in request.FILES:
        file = request.FILES['mugshot']
        # Other data on the request.FILES dictionary:
        #   filesize = len(file['content'])
        #   filetype = file['content-type']
        file_to_open = settings.MEDIA_ROOT+'//profiles//'+ user.username+'-'+file.name
        fd = open(file_to_open, 'wb+')
        if file.multiple_chunks():
            for chunk in file.chunks():
                fd.write(chunk)
        else:
            fd.write(file.read())
        fd.close()
        # Resize the image
        ms = Image.open(file_to_open)
        size = 145,132
        ms.thumbnail(size, Image.ANTIALIAS)
        ms.save(file_to_open, "JPEG")
        profile.mugshot = settings.MEDIA_URL + '//profiles//'+ user.username+'-'+file.name
        
    # Check password input
    password = form.cleaned_data['password']
    pass_confirm = form.cleaned_data['pass_confirm']
    if password != default_password:
        if password != pass_confirm:
            form._errors['password'] = ErrorList(["The passwords do not match"])
            return submit_form(form)
        else:
            user.set_password(password)

    # Have to check if user name is valid
    name = form.cleaned_data['name']
    if name is '':
        is_temporary = True
        if email != '':
            name = email
        else:
            name = mobile

        profile.is_temporary = True
    else:
        user.username = name
        profile.is_temporary = False

    mobile  = form.cleaned_data['mobile']
    profile.mobile = mobile.replace('-','')
    mobile_provider = form.cleaned_data['carrier']
    if mobile_provider != u'' and mobile != u'':
        try:
            profile.mobile_provider = MobileProvider.objects.get(domain=mobile_provider)
            profile.phone_addr = profile.mobile+'@'+profile.mobile_provider.domain
        except:
            pass

    # Confirm email
    user.email      = form.cleaned_data['email']
    user.first_name = form.cleaned_data['first_name']
    user.last_name  = form.cleaned_data['last_name']

    # Check location and zip code match
    zip     = form.cleaned_data['zip']
    address = form.cleaned_data['address']
    if zip != '' and address == '':
        profile.zipcode = zip
        try:
            addr = ZipCodes.objects.get(Q(zip_code = zip))
            profile.address = addr.city +', '+ addr.state_abbr
        except:
            pass
    elif address != '':
        local = geocode(address)
        if 'address' in local:
            profile.address = local['address']
        else:
            profile.address = address

    profile.birthday    = form.cleaned_data['birthday']
    profile.time_off    = form.cleaned_data['time_off']
    profile.time_on     = form.cleaned_data['time_on']
    profile.fish_method = form.cleaned_data['fish_method']
    profile.is_pro      = form.cleaned_data['is_pro']
    profile.web_site    = form.cleaned_data['web_site']

    try:
        user.save()
        profile.save()
    except:
        pass

    return homepage(request)

# Show the main page for a group
def showgroup(request, group=None):
    if request.GET:
        u = request.GET['group']
        group = SpotGroup.objects.get(pk=u)

    user = request.user
    profile = user.get_profile()
    if not group.is_member(user):
        alert('Only group members can view group messages')
        return homepage(request)

    m,p,n = message_list(group,0,20)
    c = Context({'profile':profile, 'group':group, 'messages':m})
    # t = get_template('mygroup.html')
    return render_to_response('mygroup.html', c, context_instance=RequestContext(request))
    

# Create and edit a group
def editgroup(request):

    def submit_form():
        if group != None:
            membership = group.get_members()
        else:
            membership = None

        c = Context( {'form':gform,'friends':friends, 'group':group, 'membership':membership} )
        t = get_template('groups.html')
        html = t.render(c)
        return HttpResponse(html)

    # Display my page
    friends = friend_set_for(request.user)
    group = None
    membership = None

    # Request to see and existing group
    if request.GET:
        g = request.GET['group']
        if g != '':
            group = SpotGroup.objects.get(pk=g)
            data = {'group_name': group.name,
                    'upload': group.profile_pic,
                    'description': group.description,
                    'web_site': group.web_site,
                    }
            gform = GroupEditForm(data)
        else:

        # First time here put up a blank form
            group = None
            gform = GroupEditForm()

        return submit_form()

    # POST Get the filled out form and check validity
    gform = GroupEditForm(request.POST)
    if not gform.is_valid():
        return submit_form()

    # Name is required
    g_name  = gform.cleaned_data['group_name']
    if g_name == '':
        gform['name']._errors = ErrorList(["A group name is required"])
        return submit_form()

    g_description = gform.cleaned_data['description']
    g_web_site    = gform.cleaned_data['web_site']

    # Get the group we are editing or create a new group
    group, created  = SpotGroup.objects.get_or_create( name = g_name )
    group.description = g_description
    group.web_site = g_web_site

    # Upload a logo
    if 'upload' in request.FILES:
        file = request.FILES['upload']
        file_to_open = settings.MEDIA_ROOT+'//profiles//'+ group.name+'-'+file.name
        fd = open(file_to_open, 'wb+')
        if file.multiple_chunks():
            for chunk in file.chunks():
                fd.write(chunk)
        else:
            fd.write(file.read())
        fd.close()
        group.profile_pic = 'profiles//'+ group.name+'-'+file.name

    group.save()

    # If this was just created add the admin
    if created:
        group.new_member(request.user,'admin')


    #Add members ( this should be temporary fix it in the template )
    members = []
    for member in request.POST.getlist('friends_add'):
        members.append(User.objects.get(pk=member))

    for friend in friends:
        if friend in members:
            if not group.is_member(friend):
                group.new_member(friend,'user')
        else:
            if group.is_member(friend):
                group.remove_member(friend)

    return showgroup(request,group)

# Delete a message: From editprofile
def message_delete(request):
    if request.POST:
        for message in request.POST.getlist('message_delete'):
            m = SpotMessage.objects.get(pk=message)
            m.delete()

        return editprofile(request)

def message(request):
    edit = False
    def submit_form():
        c = Context( {'profile':profile, 'form':form, 'message':message, 'comment_list':comment_list, 'edit':edit} )
        return render_to_response('message.html', c, context_instance=RequestContext(request))
       

    user = request.user
    if user.is_authenticated():
        profile = user.get_profile()
    else:
        profile = None

    # A POST indicates data was changed  to update the details
    if  request.POST:
        form = MessageEditForm(request.POST)
        if form.is_valid():
            m = request.POST['pk']
            message = SpotMessage.objects.get(pk=m)
            message.text = form.cleaned_data['text']
            message.date_added = form.cleaned_data['date_added']
            if form.data['lati'] and form.data['lngi']:
                latitude = form.data['lati']
                longitude = form.data['lngi']
                message.latitude = latitude
                message.longitude = longitude
                
                """ Save for photos
                for photo in message.photos.all():
                    photo.latitude = latitude
                    photo.longitude = longitude
                    photo.save()
                """
            # Delete checked photos
            if "photo_delete" in request.POST:
                for photo in request.POST.getlist('photo_delete'):
                    p = SpotPhoto.objects.get(pk=photo)
            
            # Save the new message
            message.save()
            return homepage(request)

    # Show message details from the list first time displaying form.
    if request.GET:
        if 'edit' in request.GET:
            edit = True
        
        m = request.GET['message']
        message = SpotMessage.objects.get(pk=m)
 
        type = content_type = ContentType.objects.get_for_model(SpotMessage)
        comment_list = list(SpotComment.objects.filter(content_type = type).filter(object_pk=m))
        user = request.user

        data = {'text': message.text,
                'date_added': message.date_added
               }
        form = MessageEditForm(data)
        return submit_form()
    

# Add photo in comments and new posts
def add_photo(request, photo, caption):
    # Get the file and make sure you have a unique title
    file = request.FILES[photo]
    i=1
    title = request.user.username+'-'+file.name
    while SpotPhoto.objects.filter(title = title):
        title, ext = title.split('.')
        title = title +'_' + str(i) +  '.' +ext
        i=i+1
    path = settings.MEDIA_ROOT+'//photos//'
    file_to_open = join(path,title)
    
    # Open the new file
    fd = open(file_to_open, 'wb+')
    
    #Check if its big
    if file.multiple_chunks():
        for chunk in file.chunks():
            fd.write(chunk)
    else:
        fd.write(file.read())
    fd.close()
    
    # Django only wants the relative path
    path = join('photos/',title)
    photo = SpotPhoto( image = path, title = title, caption=caption )
    photo.set_exif()
    
    # Resize the image
    ms = Image.open(file_to_open)
    size = 400,400
    ms.thumbnail(size, Image.ANTIALIAS)
    ms.save(file_to_open, "JPEG")
    
    try:
        photo.save()
        return photo
    except:
        return None

# Add a comment to an existing message
def add_comment(request):
    user = request.user
    if user.is_authenticated():
        profile = user.get_profile()
    else:
        #Alert that they can not post.
        profile = None

    # If this was a GET, its the first time the form is called
    if request.method == 'GET':
        m = request.GET['message']
        message = SpotMessage.objects.get(pk=m)
        
        form = CommentForm()
        c = Context( {'form':form, 'message':message} )
        t = get_template('comment.html')
        html = t.render(c)
        return HttpResponse(html)

    elif (request.POST):
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = SpotComment()

            # Use the GET to know what message to comment on
            m = request.POST['message']
            message = SpotMessage.objects.get(pk=m)
            
            comment.comment = form.cleaned_data['text']
            if profile != None:
                    comment.user = user

            comment.content_type = ContentType.objects.get_for_model(SpotMessage)
            comment.object_pk = m
            comment.site = Site.objects.get_current()
            
            # Save any location data 
            local = form.cleaned_data['location']
            if local != u'' and local != 'Address or Longitude and Latitude':
                # Get Longitude and Latitude 
                local = geocode(local)
                if 'latitude' in local and 'longitude' in local:
                    comment.latitude  = local['latitude']
                    comment.longitude = local['longitude']
                
            comment.save()
               
            # Pictures are many to many save comment first
            if 'picture' in request.FILES:
                photo = add_photo(request, 'picture', None )
                if photo != None:
                    # data = process_file(file, details = True, debug = False )
                    comment.photos.add(photo)
                    comment.save()

    return homepage(request)

def delete_comment(request):
    if "comment_delete" in request.GET:
        for comment in request.GET.getlist('comment_delete'):
            c = SpotComment.objects.get(pk=comment)
            c.delete()
    return message(request)

# This supports the pop up icon for a map on comments being viewed   
def map_comment(request):
    if 'latitude' in request.GET and 'longitude' in request.GET:
        latitude = request.GET['latitude']
        longitude = request.GET['longitude']
        c = Context({'longitude':longitude, 'latitude':latitude})
        t = get_template('map.html')
        html = t.render(c)
        return HttpResponse(html)

# User added message

def add_post(request):
    user = request.user
    if user.is_authenticated():
        profile = user.get_profile()
    
    def submit_form():
        c = Context({'profile':profile, 'form':form})
        return render_to_response('addpost.html', c, context_instance=RequestContext(request))
    
    # Got the form back, validate and post
    if request.method == 'GET':
        # Check if this came from a group page
        if 'group' in request.GET:
            data = {'for_group': True,
                    'group_name': request.GET['group'],
                   }
            form = PostAddForm(data)
        else:
            form = PostAddForm()
        return submit_form()
        
    # Request.POST handler
    form = PostAddForm(request.POST)
    if not form.is_valid():
        return submit_form()
    else:
        message = SpotMessage(user=user)
        message.text = form.cleaned_data['text']
    
    # Check if this message is for a group        
    group = None
    if form.cleaned_data['for_group']:
        group = form.cleaned_data['group_name']
        if SpotGroup.objects.filter(name = group):
            group = SpotGroup.objects.get(name = group)
            if not group.is_member(request.user):
                form._errors['group_name'] = ErrorList(['You must be a member of this group to post reports'])
                return submit_form(request,form)
        else:
            form._errors['group_name'] = ErrorList(['This group does not exist'])
            return submit_form()
    
    # Get the Google Map data
    if form.data['lati'] and form.data['lngi']:
        latitude = form.data['lati']
        longitude = form.data['lngi']
        message.latitude = latitude
        message.longitude = longitude
            
    # You have to save the message to add more
    message.save()
    if 'picture_1' in request.FILES:
        caption = form.cleaned_data['caption_1']
        photo = add_photo(request, 'picture_1', caption)
        if photo != None:
            message.photos.add(photo)
            message.save()
 
    if 'picture_2' in request.FILES:
        caption = form.cleaned_data['caption_2']
        photo = add_photo(request, 'picture_2', caption)
        if photo != None:
            message.photos.add(photo)
            message.save()
  
    if 'picture_3' in request.FILES:
        caption = form.cleaned_data['caption_3']
        photo = add_photo(request, 'picture_3', caption)
        if photo != None:
            message.photos.add(photo)
            message.save()
 
    if 'picture_4' in request.FILES:
        caption = form.cleaned_data['caption_4']
        photo = add_photo(request, 'picture_4', caption)
        if photo != None:
            message.photos.add(photo)
            message.save()

    
    # Send a notice to all followers.
    send_to = []
    
    # If this is a groum message send to members
    if group != None:
        message.group = group
        message.save()
        members = group.get_members()
        for member in members:
            # Don't send it to the sender
            if member == request.user:
                continue
            follow = group.follows_by(member)
            if follow == 'email':
                send_to.append(member.email)
            elif follow == 'phone':
                m_profile = member.get_profile()
                send_to.append(m_profile.phone_addr)
            
            notice_send(user, member, "message_for_group",{'group':group})

    # Find my friends and send them a notice and email, or MMS
    else:
        friends = Friendship.objects.friends_who_follow(request.user)
        for person in friends:
            friend = person['friend']
            notice_send(user, friend, "message_from_friend",{'user':friend})
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
        mail = EmailMessage('SpotBurn Alert', message.text, 'fish@spotburn.com', send_to )
        for p in message.photos.all():
            mail.attach_file(p.image)
        mail.send()
    
    return my_page(request)       
 
def rotate(request):
    pass
    
    
 # This is the logout for a user   
from django.contrib.auth import logout
def goodbye(request):
    logout(request)
    return HttpResponseRedirect('/')

# This is the ajax interfaces
from django.core import serializers
def ajax(request):
    photos = SpotPhoto.objects.all()
    n = photos.count()
    photos = photos[n-1:n]
    data = serializers.serialize("json", photos)
    return HttpResponse(data, mimetype="application/javascript")

def ajaxradio(request):
    user = request.user
    if request.POST:
        button = request.POST['button']

        #Was this a response to change the way to follow a friend?
        if 'friend' in request.POST:
            pk = request.POST['friend']

            friend = User.objects.get(pk=pk)
            friendship = Friendship.objects.follows(user,friend)
            
            # We are not friends yet
            if friendship == None:
                invite = FriendshipInvitation( from_user = request.user, to_user = friend )
                invite.request()
            else:
                # Figure out if the user is following the friend or visa versa
                if user == friendship.to_user and friend == friendship.from_user:
                    friendship.to_follow = button;
                elif user == friendship.from_user and friend == friendship.to_user:
                    friendship.from_follow = button;
                friendship.save()

        elif 'group' in request.POST:
            pk = request.POST['group']
            group = SpotGroup.objects.get(pk=pk)
            group.follows_by(user,button)
            group.save()

    data = 'OK'
    return HttpResponse(data, mimetype="application/javascript")

