# Generated by Django 4.1.7 on 2023-06-27 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login_details', '0002_initial'),
        ('recognizer', '0008_alter_lectruemodel_semester'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionattendancemodel',
            name='requested_users',
            field=models.ManyToManyField(blank=True, related_name='requested_sessions', to='login_details.logindetails'),
        ),
    ]
