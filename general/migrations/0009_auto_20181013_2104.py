# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-13 21:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0008_auto_20181006_1134'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='data_source',
            field=models.CharField(choices=[('FanDuel', 'FanDuel'), ('DraftKings', 'DraftKings'), ('Yahoo', 'Yahoo'), ('Fanball', 'Fanball'), ('FantasyDraft', 'FantasyDraft')], default='FanDuel', max_length=30),
        ),
    ]
