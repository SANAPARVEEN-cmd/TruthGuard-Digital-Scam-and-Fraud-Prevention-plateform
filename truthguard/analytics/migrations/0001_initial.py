from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pattern',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pattern_name', models.CharField(max_length=255)),
                ('signature', models.CharField(help_text='Regex or keyword signature', max_length=500)),
                ('description', models.TextField(blank=True)),
                ('risk_weight', models.PositiveIntegerField(default=10)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('related_entities', models.ManyToManyField(blank=True, related_name='patterns', to='entities.entity')),
            ],
            options={
                'ordering': ['-risk_weight', 'pattern_name'],
            },
        ),
    ]
