from django.contrib import admin,messages
from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Exam,Question,Attempt,Profile,Entitlement,AssessmentJob
from .services import validate_exam

class ExamForm(forms.ModelForm):
    class Meta:
        model=Exam
        fields='__all__'
        labels={'audio_file':'Audio fayl', 'audio_url':'HTTPS audio havola', 'listening_transcript':'Yashirin audio transkripti (AI uchun)'}
        help_texts={'audio_file':'MP3, WAV, OGG, M4A yoki WebM; ko‘pi bilan 20 MB. Yuklangan fayl havoladan ustun.', 'audio_url':'Ixtiyoriy: login talab qilmaydigan bevosita HTTPS audio fayl manzili.', 'listening_transcript':'Audio matnini aynan yozing. Topshiruvchiga ko‘rsatilmaydi; AI xatolarga dalil topishda ishlatadi.'}
    def clean_audio_file(self):
        audio=self.cleaned_data.get('audio_file')
        if audio and audio.size>20*1024*1024:
            raise forms.ValidationError('Audio fayl 20 MB dan oshmasin.')
        return audio

class AnswerLinesField(forms.Field):
    widget = forms.Textarea(attrs={'rows': 4})

    def prepare_value(self, value):
        return '\n'.join(value) if isinstance(value, list) else value

    def to_python(self, value):
        return [line.strip() for line in (value or '').splitlines() if line.strip()]


class QuestionForm(forms.ModelForm):
    choices = AnswerLinesField(required=False, label='Javob variantlari', help_text='Har qatorga bitta variant. Qisqa javob uchun bo‘sh qoldiring.')
    accepted_answers = AnswerLinesField(required=False, label='To‘g‘ri javoblar', help_text='Har qatorga bitta qabul qilinadigan javob. Variantli savolda variant bilan aynan bir xil yozing.')

    class Meta:
        model = Question
        fields = '__all__'
        labels = {'position': 'Savol raqami', 'prompt': 'Savol (ingliz tilida)', 'evidence': 'Matndan aniq dalil', 'explanation': 'Xatoni tushuntirish va to‘g‘rilash', 'skill_tag': 'Savol turi'}
        help_texts = {'evidence': 'Reading matni yoki Listening transkriptidan aynan jumlani kiriting. NOT GIVEN uchun bo‘sh qoldiring.', 'explanation': 'To‘g‘ri javobga qanday kelish va shu xatoni qayta qilmaslikni tushuntiring.', 'skill_tag': 'Masalan: true_false_not_given, matching_headings, short_answer.'}

class Questions(admin.StackedInline):
    form=QuestionForm
    model=Question
    verbose_name="Savol"
    verbose_name_plural="Savollar — har biriga javob va dalil kiriting"
    extra=0
    fields=['position','prompt','choices','accepted_answers','skill_tag','evidence','explanation']
    def get_fields(self,request,obj=None):
        if obj and obj.section=='Writing':return ['position','prompt']
        return self.fields
    def has_change_permission(self,request,obj=None):return not obj or not obj.published
    def has_add_permission(self,request,obj=None):return not obj or not obj.published
    def has_delete_permission(self,request,obj=None):return not obj or not obj.published

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    form=ExamForm
    list_display=['title','section','version','published','duration_seconds']
    list_filter=['section','published']
    search_fields=['title']
    inlines=[Questions]
    actions=['publish_checked','duplicate_draft']
    fieldsets=[('1. Test haqida', {'fields':['title','section','duration_seconds','version','published'], 'description':'Avval qoralamani saqlang, savollarni kiriting, keyin ro‘yxatdan «Tekshirish va nashr qilish» amalini tanlang. Nashr qilingan testni o‘zgartirish uchun yangi qoralamaga nusxalang.'}), ('2. Reading matni / topshiriq', {'fields':['passage'], 'description':'Matnni ingliz tilida, paragraflarni bo‘sh qator bilan ajratib kiriting. Vaqt soniyalarda: 60 daqiqa = 3600.'}), ('3. Listening audio', {'fields':['audio_file','audio_url','listening_transcript'], 'description':'Listening: audio faylni yuklang va AI uchun yashirin transkriptni kiriting. Passage faqat sintetik demo uchun: undagi matn ovoz ishlamasa foydalanuvchiga ko‘rinadi.'})]

    class Media:
        css={'all':('exams/admin.css',)}
    def get_fieldsets(self,request,obj=None):
        if obj and obj.section=='Writing':
            return [self.fieldsets[0], ('2. Writing materiallari', {'fields':['passage'], 'description':'Task 1 jadvali yoki umumiy ma’lumotni shu yerga yozing. Quyida raqam 1 — Task 1, raqam 2 — Task 2. Prompt ichiga to‘liq topshiriqni yozing. Variant va javob kaliti kerak emas. Hozircha rasm yuklash qo‘llab-quvvatlanmaydi.'})]
        return self.fieldsets
    def get_readonly_fields(self,request,obj=None):
        return ['title','section','version','duration_seconds','passage','audio_url','audio_file','listening_transcript','published'] if obj and obj.published else ['published']
    def has_delete_permission(self,request,obj=None):return not obj or not obj.published
    @admin.action(description='Tekshirish va nashr qilish')
    def publish_checked(self,request,queryset):
        for exam in queryset:
            try:
                with transaction.atomic():
                    exam=Exam.objects.select_for_update().get(pk=exam.pk)
                    validate_exam(exam)
                    exam.published=True;exam.save(update_fields=['published'])
                self.message_user(request,f'{exam.title}: nashr qilindi.',messages.SUCCESS)
            except ValidationError as exc:self.message_user(request,f'{exam.title}: '+ ' '.join(exc.messages),messages.ERROR)
    @admin.action(description='Yangi versiyaga nusxalash (qoralama)')
    def duplicate_draft(self,request,queryset):
        with transaction.atomic():
            for exam in queryset:
                questions=list(exam.questions.all())
                exam.pk=None;exam.published=False;exam.version+=1;exam.save()
                for q in questions:q.pk=None;q.exam=exam;q.save()
        self.message_user(request,'Yangi qoralamalar yaratildi.',messages.SUCCESS)

@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display=['id','user','exam','state','started_at']
    list_filter=['state','exam__section']
    search_fields=['user__email','exam__title']
    def get_readonly_fields(self,request,obj=None):return [f.name for f in self.model._meta.fields]
    def has_add_permission(self,request):return False
    def has_delete_permission(self,request,obj=None):return False

@admin.register(Entitlement)
class EntitlementAdmin(admin.ModelAdmin):
    list_display=['user','exam','consumed','reference']
    search_fields=['user__email','reference']
    readonly_fields=['consumed']
    def get_readonly_fields(self,request,obj=None):return ['user','exam','consumed','reference'] if obj and obj.consumed else ['consumed']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display=['user','target_band','language','free_attempt_used']
    readonly_fields=['free_attempt_used']
admin.site.site_header='IELTSQA — testlarni boshqarish'

@admin.register(AssessmentJob)
class AssessmentJobAdmin(admin.ModelAdmin):
    list_display=['attempt','state','tries','error_code','available_at']
    list_filter=['state']
    readonly_fields=['attempt','state','tries','available_at','lease','error_code']
    actions=['retry_failed']
    def has_add_permission(self,request):return False
    def has_delete_permission(self,request,obj=None):return False
    @admin.action(description='AI xatosini tuzatgandan keyin qayta baholash')
    def retry_failed(self,request,queryset):
        from django.utils import timezone
        queryset.filter(state='failed',attempt__state='awaiting_assessment').update(state='pending',tries=0,error_code='',lease=None,available_at=timezone.now())
