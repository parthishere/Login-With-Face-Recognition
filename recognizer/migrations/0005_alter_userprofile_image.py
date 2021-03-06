# Generated by Django 3.2.3 on 2021-05-29 16:38

from django.db import migrations, models
import recognizer.models


class Migration(migrations.Migration):

    dependencies = [
        ('recognizer', '0004_alter_userprofile_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=recognizer.models.user_image_path),
        ),
    ]
