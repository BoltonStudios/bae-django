# Generated by Django 4.2.7 on 2023-12-10 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sliders', '0010_remove_extension_is_move_on_hover_enabled_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='extension',
            name='handle_animation',
            field=models.IntegerField(default=0),
        ),
    ]
