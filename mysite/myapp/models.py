from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ChatRoom(models.Model):
    name = models.CharField(max_length = 100)
    slug = models.SlugField(unique = True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_chatrooms')
    members = models.ManyToManyField(User, blank=True, related_name='joined_chatrooms')
    
class ChatMessage(models.Model):
    user  = models.ForeignKey(User, on_delete = models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete = models.CASCADE)
    message_content = models.TextField()
    is_seen = models.BooleanField(default=False)
    attachment = models.FileField(upload_to='chat_attachments/', null=True, blank=True)
    date = models.DateTimeField(auto_now_add = True)

    class Meta:
        ordering = ('date',)        
