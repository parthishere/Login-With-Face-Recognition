# Generated by Django 4.1.7 on 2023-03-26 12:49

from django.db import migrations, models
import recognizer.models


class Migration(migrations.Migration):

    dependencies = [
        ('recognizer', '0005_sessionattendancemodel_end_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='image',
            field=models.ImageField(blank=True, max_length=500, null=True, upload_to=recognizer.models.user_image_path),
        ),
    ]