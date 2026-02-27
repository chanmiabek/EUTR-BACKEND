from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("donations", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="donation",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="donation",
            name="external_reference",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="donation",
            name="failed_reason",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="donation",
            name="gateway_event_id",
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name="donation",
            name="provider",
            field=models.CharField(blank=True, max_length=20),
        ),
    ]
