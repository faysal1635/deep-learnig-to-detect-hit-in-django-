# Generated by Django 3.2.5 on 2022-05-21 19:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('firing', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='firer',
            name='status',
            field=models.CharField(blank=True, choices=[('Passed', 'Passed'), ('Failed', 'Failed'), ('Not appeared', 'Not appeared')], max_length=200, null=True),
        ),
    ]
