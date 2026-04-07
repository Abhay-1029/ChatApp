from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .forms import RoomCreateForm, RoomJoinForm, StyledAuthenticationForm, StyledUserCreationForm
from .models import ChatRoom, ChatMessage

DEFAULT_ROOM_SLUGS = ['work', 'tech']


# Create your views here.
def landing(request):
    if request.user.is_authenticated:
        return redirect('index')
    return redirect('login')


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = StyledUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully.')
            return redirect('index')
    else:
        form = StyledUserCreationForm()

    return render(request, 'myapp/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')

    form = StyledAuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, 'Welcome back.')
        return redirect('index')

    return render(request, 'myapp/login.html', {'form': form})


@login_required
def index(request):
    if request.method == 'POST':
        if request.POST.get('action') == 'join_room':
            join_form = RoomJoinForm(request.POST)
            form = RoomCreateForm()
            if join_form.is_valid():
                share_link = join_form.cleaned_data['share_link'].strip().rstrip('/')
                slug = share_link.split('/')[-1]
                chatroom = ChatRoom.objects.filter(slug=slug).first()
                if chatroom:
                    messages.success(request, 'Room opened successfully.')
                    return redirect('chatroom', slug=chatroom.slug)
                messages.error(request, 'No room found for that shared link.')
        else:
            form = RoomCreateForm(request.POST)
            join_form = RoomJoinForm()
            if form.is_valid():
                room_name = form.cleaned_data['name'].strip()
                base_slug = slugify(room_name)
                slug = base_slug or 'room'
                counter = 1

                while ChatRoom.objects.filter(slug=slug).exists():
                    counter += 1
                    slug = f'{base_slug or "room"}-{counter}'

                chatroom = ChatRoom.objects.create(name=room_name, slug=slug, owner=request.user)
                chatroom.members.add(request.user)
                messages.success(request, 'Room created successfully.')
                return redirect('chatroom', slug=chatroom.slug)
    else:
        form = RoomCreateForm()
        join_form = RoomJoinForm()

    chatrooms = ChatRoom.objects.filter(
        Q(slug__in=DEFAULT_ROOM_SLUGS) | Q(owner=request.user) | Q(members=request.user)
    ).distinct()
    return render(request, 'myapp/index.html',{'chatrooms':chatrooms, 'form': form, 'join_form': join_form})

@login_required
def chatroom(request, slug):
    chatroom = get_object_or_404(ChatRoom, slug=slug)
    chatroom.members.add(request.user)
    ChatMessage.objects.filter(room=chatroom, is_seen=False).exclude(user=request.user).update(is_seen=True)
    room_messages = ChatMessage.objects.filter(room=chatroom)[0:25]
    share_url = request.build_absolute_uri()
    return render(request,'myapp/room.html',{'chatroom':chatroom, 'room_messages':room_messages, 'share_url': share_url}) 


@login_required
def delete_room(request, slug):
    chatroom = get_object_or_404(ChatRoom, slug=slug)

    if request.method != 'POST':
        return redirect('chatroom', slug=chatroom.slug)

    if chatroom.slug in DEFAULT_ROOM_SLUGS:
        messages.error(request, 'Default rooms cannot be deleted.')
        return redirect('chatroom', slug=chatroom.slug)

    if chatroom.owner_id != request.user.id:
        messages.error(request, 'Only the room creator can delete this room.')
        return redirect('chatroom', slug=chatroom.slug)

    chatroom.delete()
    messages.success(request, 'Room deleted successfully.')
    return redirect('index')


@login_required
def leave_room(request, slug):
    chatroom = get_object_or_404(ChatRoom, slug=slug)

    if request.method != 'POST':
        return redirect('chatroom', slug=chatroom.slug)

    if chatroom.slug in DEFAULT_ROOM_SLUGS:
        messages.error(request, 'Default rooms stay available for every user.')
        return redirect('chatroom', slug=chatroom.slug)

    if chatroom.owner_id == request.user.id:
        messages.error(request, 'Room creator cannot leave the room. You can delete it instead.')
        return redirect('chatroom', slug=chatroom.slug)

    chatroom.members.remove(request.user)
    messages.success(request, 'You left the room.')
    return redirect('index')


@login_required
def upload_attachment(request, slug):
    chatroom = get_object_or_404(ChatRoom, slug=slug)
    chatroom.members.add(request.user)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method.'}, status=405)

    attachment = request.FILES.get('attachment')
    if not attachment:
        return JsonResponse({'error': 'No file selected.'}, status=400)

    chat_message = ChatMessage.objects.create(
        user=request.user,
        room=chatroom,
        message_content='',
        attachment=attachment,
    )

    attachment_url = chat_message.attachment.url
    attachment_name = attachment.name.split('/')[-1].split('\\')[-1]
    is_image = bool(getattr(attachment, 'content_type', '') and attachment.content_type.startswith('image/'))

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'chat_{chatroom.slug}',
        {
            'type': 'chat_message',
            'message_id': chat_message.id,
            'message': '',
            'username': request.user.username,
            'room': chatroom.slug,
            'is_seen': False,
            'attachment_url': attachment_url,
            'attachment_name': attachment_name,
            'is_image': is_image,
        }
    )

    return JsonResponse({
        'success': True,
        'message_id': chat_message.id,
        'attachment_url': attachment_url,
        'attachment_name': attachment_name,
        'is_image': is_image,
    })
