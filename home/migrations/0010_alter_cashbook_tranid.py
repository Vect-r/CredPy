# Generated by Django 4.0.5 on 2022-06-30 15:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_alter_cashbook_tranid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cashbook',
            name='TranID',
            field=models.IntegerField(primary_key=True, serialize=False),
        ),
    ]
