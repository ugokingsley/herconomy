# Generated by Django 4.2.3 on 2023-10-24 09:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('transaction_api', '0002_accessattemptaddons'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessAttempt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('attempt_count', models.IntegerField(blank=True, null=True)),
                ('expiration_date', models.DateTimeField(verbose_name='Expiration Time')),
                ('userattempt', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='AccessAttemptAddons',
        ),
    ]