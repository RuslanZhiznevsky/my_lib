# Generated by Django 4.2.6 on 2024-04-20 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0002_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='bookcategory',
            constraint=models.UniqueConstraint(fields=('user', 'position'), name='library_bookcategory_user_and_postion_unique'),
        ),
    ]
