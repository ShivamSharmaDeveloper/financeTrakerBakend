# Generated by Django 5.0.2 on 2025-05-20 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='type',
            field=models.CharField(choices=[('income', 'Income'), ('expense', 'Expense')], default='expense', max_length=7),
        ),
    ]
