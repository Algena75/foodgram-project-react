# Generated by Django 2.2.16 on 2023-05-30 09:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_delete_blacklistedtoken'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'Подписки', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('pk',)},
        ),
    ]