from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('severity', models.CharField(choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='medium', max_length=20)),
                ('category', models.CharField(choices=[('phishing', 'Phishing'), ('romance', 'Romance Scam'), ('financial', 'Financial Fraud'), ('identity', 'Identity Theft'), ('malware', 'Malware'), ('vishing', 'Vishing/Smishing'), ('general', 'General')], default='general', max_length=30)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('related_entities', models.ManyToManyField(blank=True, related_name='alerts', to='entities.entity')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
