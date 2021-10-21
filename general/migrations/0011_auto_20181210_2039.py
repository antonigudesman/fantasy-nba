# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-10 20:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0010_auto_20181103_0003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='ou',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='minutes',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='money_line',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='over_under',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='point_spread',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='proj_ceiling',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='proj_custom',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='proj_floor',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='proj_original',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='proj_points',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='proj_rotowire',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='proj_site',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='proj_third_party_one',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='proj_third_party_two',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='salary',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='salary_custom',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='salary_original',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='team_points',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='player',
            name='value',
            field=models.FloatField(default=0),
        ),
    ]