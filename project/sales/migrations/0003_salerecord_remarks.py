# Generated by Django 5.1.5 on 2025-02-01 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sales", "0002_customer_rename_role_customuser_user_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="salerecord",
            name="remarks",
            field=models.TextField(blank=True, null=True),
        ),
    ]
