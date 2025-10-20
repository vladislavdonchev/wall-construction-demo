# Generated migration for wall simulation support

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="wallsection",
            name="initial_height",
            field=models.IntegerField(
                blank=True,
                null=True,
                help_text="Initial height in feet (0-30) for simulation",
            ),
        ),
        migrations.AddField(
            model_name="wallsection",
            name="current_height",
            field=models.IntegerField(
                blank=True,
                null=True,
                help_text="Current height in feet during simulation",
            ),
        ),
    ]
