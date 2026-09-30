import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('exams', '0005_speakingrecording')]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='audio_file',
            field=models.FileField(
                blank=True,
                upload_to='exam_audio/',
                validators=[django.core.validators.FileExtensionValidator(['mp3', 'wav', 'ogg', 'm4a', 'webm'])],
            ),
        ),
    ]
