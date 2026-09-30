from django.db import migrations


def normalize_demo_audio(apps, schema_editor):
    Exam = apps.get_model('exams', 'Exam')
    Attempt = apps.get_model('exams', 'Attempt')
    legacy = 'browser-tts://passage'
    Exam.objects.filter(audio_url=legacy).update(audio_url='')
    for attempt in Attempt.objects.filter(snapshot__audio_url=legacy).iterator():
        snapshot = attempt.snapshot.copy()
        snapshot['audio_url'] = ''
        attempt.snapshot = snapshot
        attempt.save(update_fields=['snapshot'])


class Migration(migrations.Migration):
    dependencies = [('exams', '0006_exam_audio_file')]

    operations = [migrations.RunPython(normalize_demo_audio, migrations.RunPython.noop)]
