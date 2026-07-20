# Migration pour le nouveau système de notifications (alerte tous les membres)

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('equipments', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type_notification', models.CharField(choices=[('echographe', 'Nouvel équipement'), ('panne', 'Nouvelle panne'), ('maintenance', 'Nouvelle maintenance'), ('planification', 'Nouvelle planification'), ('piece', 'Nouvelle pièce de rechange'), ('stock', 'Mouvement de stock'), ('info', 'Information')], default='info', max_length=30)),
                ('titre', models.CharField(max_length=200)),
                ('message', models.TextField()),
                ('lien', models.CharField(blank=True, help_text="URL relative liée à l'objet concerné", max_length=200)),
                ('date_creation', models.DateTimeField(auto_now_add=True)),
                ('auteur', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications_envoyees', to=settings.AUTH_USER_MODEL)),
                ('lu_par', models.ManyToManyField(blank=True, related_name='notifications_lues', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Notification',
                'verbose_name_plural': 'Notifications',
                'ordering': ['-date_creation'],
            },
        ),
    ]
