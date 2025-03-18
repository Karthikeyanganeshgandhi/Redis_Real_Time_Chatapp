from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from .models import ChatRoom, Message
from .forms import signform 
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import registerform  
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.http import HttpResponse
from django.template import loader


# Create your views here.


@login_required
def chat_room(request, room_name):
    room, _ = ChatRoom.objects.get_or_create(name=room_name)
    messages = Message.objects.filter(room=room).order_by("timestamp")

    return render(request, "chatroom.html", {"room_name": room_name, "messages": messages})

def signin(request):
    if request.method == 'POST':
        form = signform(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('chat_room', room_name='general') 
            else:
                messages.error(request, 'Invalid email or password')
    else:
        form = signform()

    return render(request, 'login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = registerform(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            passwd = form.cleaned_data['passwd']
            
            user = User.objects.create_user(username=email, email=email, password=passwd)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            messages.success(request, f'Account created for {first_name} {last_name}')
            return redirect('signin')
    else:
        form = registerform()
    return render(request, 'register.html', {'form':form})

def user_logout(request):
    logout(request)
    return redirect('signin')

def account(request):
    return render(request, 'Account.html', {'user':request.user})





