# Generated by Django 4.2.7 on 2023-12-09 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sliders', '0008_extension_is_move_on_click_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='extension',
            name='mouseover_action',
            field=models.IntegerField(default=1),
        ),
    ]