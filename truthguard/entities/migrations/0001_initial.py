from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('entity_type', models.CharField(choices=[('phone', 'Phone Number'), ('email', 'Email Address'), ('website', 'Website URL')], max_length=20)),
                ('entity_value', models.CharField(db_index=True, max_length=500, unique=True)),
                ('risk_score', models.PositiveIntegerField(default=0)),
                ('threat_level', models.CharField(choices=[('safe', 'Safe'), ('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')], default='safe', max_length=20)),
                ('status', models.CharField(choices=[('active', 'Active'), ('monitoring', 'Under Monitoring'), ('blocked', 'Blocked'), ('cleared', 'Cleared')], default='active', max_length=20)),
                ('report_count', models.PositiveIntegerField(default=0)),
                ('risk_explanation', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'entities',
                'ordering': ['-risk_score', '-updated_at'],
            },
        ),
    ]
