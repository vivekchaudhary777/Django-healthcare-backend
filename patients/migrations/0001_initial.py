import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [("accounts", "0001_initial")]
    operations = [migrations.CreateModel(name="Patient", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("name", models.CharField(max_length=150)), ("date_of_birth", models.DateField(blank=True, null=True)),
        ("gender", models.CharField(choices=[("female", "Female"), ("male", "Male"), ("other", "Other"), ("unspecified", "Unspecified")], default="unspecified", max_length=20)),
        ("email", models.EmailField(blank=True, max_length=254)), ("phone", models.CharField(blank=True, max_length=32)),
        ("address", models.CharField(blank=True, max_length=255)), ("created_at", models.DateTimeField(auto_now_add=True)),
        ("updated_at", models.DateTimeField(auto_now=True)),
        ("owner", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="patients", to=settings.AUTH_USER_MODEL)),
    ], options={"ordering": ["id"]})]
