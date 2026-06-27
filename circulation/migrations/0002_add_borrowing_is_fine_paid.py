from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circulation', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='borrowing',
            name='is_fine_paid',
            field=models.BooleanField(default=False),
        ),
    ]
