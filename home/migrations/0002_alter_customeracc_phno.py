# Generated by Django 3.2.9 on 2022-05-09 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customeracc',
            name='phno',
            field=models.IntegerField(),
        ),
    ]