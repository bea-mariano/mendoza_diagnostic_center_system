# Generated by Django 5.2 on 2025-04-16 03:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='company_peme_rate',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
