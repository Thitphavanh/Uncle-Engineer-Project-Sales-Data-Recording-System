# Generated by Django 5.1.5 on 2025-02-03 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0008_alter_customuser_user_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='salerecord',
            name='status',
            field=models.CharField(choices=[('pending', 'รอคอนเฟิร์ม'), ('confirmed', 'คอนเฟิร์มยอดแล้ว')], default='pending', max_length=10),
        ),
    ]
