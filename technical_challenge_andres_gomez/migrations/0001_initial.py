# Generated by Django 5.1.3 on 2024-11-25 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Registro',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_archivo', models.CharField(max_length=255)),
                ('url_archivo', models.URLField()),
                ('peso_archivo', models.CharField(max_length=50)),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
