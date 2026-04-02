from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [('registrations', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='AdmissionToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=255, unique=True)),
                ('checked_in_at', models.DateTimeField(blank=True, null=True)),
                ('registration', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='registrations.registration')),
            ],
        ),
    ]
