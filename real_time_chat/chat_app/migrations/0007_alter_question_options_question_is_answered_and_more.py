# Generated by Django 5.1 on 2024-11-15 20:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat_app', '0006_gamesession_question'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['-created_at']},
        ),
        migrations.AddField(
            model_name='question',
            name='is_answered',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='gamesession',
            name='secret_item',
            field=models.CharField(max_length=200),
        ),
        migrations.AlterField(
            model_name='gamesession',
            name='thinker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_games', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='question',
            name='answer',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='question',
            name='game_session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='chat_app.gamesession'),
        ),
        migrations.AlterField(
            model_name='question',
            name='question_text',
            field=models.TextField(),
        ),
    ]