# Generated by Django 5.1.5 on 2025-02-03 14:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0007_customuser_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='user_type',
            field=models.CharField(blank=True, default='sales', max_length=20, null=True),
        ),
    ]
