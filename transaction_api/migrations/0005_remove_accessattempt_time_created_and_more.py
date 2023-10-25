# Generated by Django 4.2.3 on 2023-10-24 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction_api', '0004_remove_accessattempt_expiration_date_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accessattempt',
            name='time_created',
        ),
        migrations.AddField(
            model_name='accessattempt',
            name='time_last_unsuccessful_login',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
