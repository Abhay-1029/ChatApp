from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_chatroom_members'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='is_seen',
            field=models.BooleanField(default=False),
        ),
    ]
