from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("applications", "0005_partner"),
    ]

    operations = [
        migrations.CreateModel(
            name="PartnerAppointment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("organization_name", models.CharField(max_length=180)),
                ("contact_name", models.CharField(max_length=120)),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(blank=True, max_length=40)),
                ("preferred_date", models.DateField(blank=True, null=True)),
                ("preferred_time", models.CharField(blank=True, max_length=60)),
                ("topic", models.CharField(blank=True, max_length=200)),
                ("message", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("responded", "Responded"), ("closed", "Closed")],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("admin_response", models.TextField(blank=True)),
                ("response_sent_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
