# Generated by Django 4.2.7 on 2023-12-09 09:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sliders', '0007_extension_is_move_on_hover_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='extension',
            name='is_move_on_click_enabled',
            field=models.BooleanField(default=False),
        ),
    ]