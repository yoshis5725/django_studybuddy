from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q  # q lookups
from .models import Room, Topic, User, Message
from .forms import RoomForm, UserForm


def home(request):
    # search logic - retrieving the rooms whose topic equals the browser search requirement of 'q'
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) | Q(name__icontains=q) | Q(description__icontains=q)
    )

    topics = Topic.objects.all()
    room_messages = Message.objects.filter(Q(room__topic__name__contains=q)).order_by('-created')
    context = {'rooms': rooms, 'topics': topics, 'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    single_room = Room.objects.get(id=pk)
    comments = single_room.message_set.all().order_by('-created')
    participants = single_room.participants.all()

    # creating the message
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=single_room,
            body=request.POST.get('body')
        )
        # adding the user to the room, then reloading the page so that the message is correctly placed on the page
        single_room.participants.add(request.user)
        return redirect('room', pk=single_room.id)

    context = {'room': single_room, 'comments': comments, 'participants': participants}
    return render(request, 'base/room.html', context)


@login_required(login_url='login')
def create_room(request):
    topics = Topic.objects.all()
    form = RoomForm()

    if request.method == 'POST':

        # getting the value of the topic. If the topic already exists, it will get the name and return it to the topic
        # object and created will be false; if the topic does not exist, then it will create the topic and return it to
        # the topic object and created will be true
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        # creating the room
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description')
        )

        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def update_room(request, pk):
    topics = Topic.objects.all()
    edit_room = Room.objects.get(id=pk)
    form = RoomForm(instance=edit_room)  # pre-filling the form

    # checking if the currently logged-in user is the host of the room. If not then that user will
    # not be allowed to utilize the edit function
    if request.user != edit_room.host:
        return HttpResponse('Your are not the owner of this room, your action is not allowed!')

    if request.method == 'POST':

        # getting the value of the topic. If the topic already exists, it will get the name and return it to the topic
        # object and created will be false; if the topic does not exist, then it will create the topic and return it to
        # the topic object and created will be true
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        # saving the edited information
        edit_room.name = request.POST.get('name')
        edit_room.topic = topic
        edit_room.description = request.POST.get('description')
        edit_room.save()
        return redirect('home')

    context = {'form': form, 'topics': topics, 'room': edit_room}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def delete_room(request, pk):
    remove_room = Room.objects.get(id=pk)

    if request.method == 'POST':
        remove_room.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj': remove_room})


def login_page(request):
    page = 'login'

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # checking to see if the user exists
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request, 'User does not exist!')

        # authenticating then logging in the user if that user exists
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist!')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logout_page(request):
    logout(request)
    return redirect('login')


def register_page(request):
    page = 'register'
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)  # accessing the user's information
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error happened during registration')

    context = {'page': page, 'form': form}
    return render(request, 'base/login_register.html', context)


@login_required(login_url='login')
def delete_message(request, pk):
    remove_message = Message.objects.get(id=pk)

    if request.user.id is remove_message.user.id:
        if request.method == 'POST':
            remove_message.delete()
            return redirect('home')
    else:
        return HttpResponse('You are not allowed to perform this action!')

    return render(request, 'base/delete.html', {'obj': remove_message})


def user_profile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()  # getting all the rooms created by a user
    user_topics = Topic.objects.all()
    user_messages = user.message_set.all()
    context = {'user': user, 'rooms': rooms, 'topics': user_topics, 'room_messages': user_messages}
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def update_user(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'base/update_user.html', context)


def topics_page(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)


def activity_page(request):
    room_messages = Message.objects.all()
    context = {'room_messages': room_messages}
    return render(request, 'base/activity.html', context)



