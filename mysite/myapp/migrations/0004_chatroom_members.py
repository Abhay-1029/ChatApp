from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_chatroom_owner'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='chatroom',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='joined_chatrooms', to=settings.AUTH_USER_MODEL),
        ),
    ]
