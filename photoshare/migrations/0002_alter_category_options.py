# Generated by Django 4.2.2 on 2023-06-11 06:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('photoshare', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('name',), 'verbose_name_plural': 'categories'},
        ),
    ]
