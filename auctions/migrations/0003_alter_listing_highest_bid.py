# Generated by Django 3.2.3 on 2021-05-30 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_alter_listing_highest_bid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='highest_bid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
    ]