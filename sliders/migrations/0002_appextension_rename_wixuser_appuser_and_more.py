# Generated by Django 4.2.7 on 2023-12-03 00:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sliders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AppExtension',
            fields=[
                ('extension_id', models.CharField(max_length=200, primary_key=True, serialize=False)),
                ('before_image', models.CharField(max_length=1000)),
                ('before_label_text', models.CharField(max_length=1000)),
                ('before_alt_text', models.CharField(max_length=1000)),
                ('after_image', models.CharField(max_length=1000)),
                ('after_label_text', models.CharField(max_length=1000)),
                ('after_alt_text', models.CharField(max_length=1000)),
                ('offset', models.IntegerField()),
                ('offset_float', models.FloatField()),
                ('is_vertical', models.BooleanField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.RenameModel(
            old_name='WixUser',
            new_name='AppUser',
        ),
        migrations.DeleteModel(
            name='ComponentSlider',
        ),
        migrations.AddField(
            model_name='appextension',
            name='instance_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sliders.appuser'),
        ),
    ]
