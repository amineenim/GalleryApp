# Generated by Django 4.2.2 on 2023-07-10 21:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photoshare', '0004_passwordresettoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='created_at',
            field=models.DateTimeField(),
        ),
    ]
