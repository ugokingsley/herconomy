# Generated by Django 4.2.3 on 2023-10-24 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('transaction_api', '0003_accessattempt_delete_accessattemptaddons'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accessattempt',
            name='expiration_date',
        ),
        migrations.AddField(
            model_name='accessattempt',
            name='time_created',
            field=models.DateTimeField(null=True),
        ),
        migrations.AlterField(
            model_name='accessattempt',
            name='attempt_count',
            field=models.IntegerField(default=0),
        ),
    ]