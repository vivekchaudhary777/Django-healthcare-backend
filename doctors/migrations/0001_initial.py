import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("accounts", "0001_initial")]
    operations = [migrations.CreateModel(name="Doctor", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("name", models.CharField(max_length=150)), ("specialization", models.CharField(max_length=120)),
        ("email", models.EmailField(blank=True, max_length=254)), ("phone", models.CharField(blank=True, max_length=32)),
        ("clinic_address", models.CharField(blank=True, max_length=255)), ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("created_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="created_doctors", to=settings.AUTH_USER_MODEL)),
    ], options={"ordering": ["id"]})]
