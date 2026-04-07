from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0005_chatmessage_is_seen'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='attachment',
            field=models.FileField(blank=True, null=True, upload_to='chat_attachments/'),
        ),
    ]
