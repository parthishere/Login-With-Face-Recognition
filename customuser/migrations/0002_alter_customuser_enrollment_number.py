# Generated by Django 4.1.7 on 2023-04-03 05:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customuser', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='enrollment_number',
            field=models.BigIntegerField(default=100),
        ),
    ]
