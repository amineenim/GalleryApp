# Generated by Django 4.2.2 on 2023-07-10 22:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('photoshare', '0005_alter_passwordresettoken_created_at'),
    ]

    operations = [
        migrations.AlterField(
            model_name='passwordresettoken',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
