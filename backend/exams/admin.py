from django.contrib import admin,messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.html import format_html
from .admin_forms import ExamForm,QuestionForm
from .models import Exam,Question,Attempt,Profile,Entitlement,AssessmentJob
from .services import validate_exam

class Questions(admin.StackedInline):
    model=Question
    form=QuestionForm
    extra=1
    verbose_name='Savol'
    verbose_name_plural='Savollar — har bir savol uchun bitta blok to\u2018ldiring'
    fields=['part','position','prompt','audio_file','choices','accepted_answers','skill_tag','evidence','explanation']
    def has_change_permission(self,request,obj=None):return not obj or not obj.published
    def has_add_permission(self,request,obj=None):return not obj or not obj.published
    def has_delete_permission(self,request,obj=None):return not obj or not obj.published

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    form=ExamForm
    list_display=['title','section','version','published','duration_seconds','audio_state','question_count']
    list_filter=['section','published']
    search_fields=['title']
    inlines=[Questions]
    actions=['publish_checked','duplicate_draft']
    fieldsets=[
        ('1. Test haqida',{'fields':['title','section','duration_seconds'],
            'description':'Avval bo\u2018limni tanlang \u2014 keyingi maydonlardan qaysi biri kerakligi shunga bog\u2018liq.'}),
        ('2. Material',{'fields':['passage','audio_file','audio_url'],
            'description':'Reading \u2192 matn majburiy. Listening \u2192 audio fayl yuklang (yoki HTTPS havola), '
                          'transkriptni matn maydoniga qo\u2018ying. Writing \u2192 matn maydoni ixtiyoriy, '
                          'topshiriqlarni quyidagi savollar bo\u2018limiga yozing. '
                          'Speaking \u2192 bu maydonlar bo\u2018sh; har bir savolga qism va o\u2018z audiosini bering.'}),
        ('3. Holat',{'fields':['published'],
            'description':'Bu yerdan belgilamang. Pastdagi ro\u2018yxatdan testni tanlab, '
                          '\u00abTekshirish va nashr qilish\u00bb amalini ishlating \u2014 u avval xatolarni tekshiradi. '
                          'Nashr qilingandan keyin test o\u2018zgarmas bo\u2018lib qoladi.'}),
    ]
    @admin.display(description='Audio')
    def audio_state(self,obj):
        if obj.section!='Listening':return '\u2014'
        if obj.audio_file:return format_html('<b style="color:#1b7f3b">fayl</b>')
        if obj.audio_url:return 'tashqi havola'
        return format_html('<b style="color:#b3200f">YO\u2018Q</b>')
    @admin.display(description='Savollar')
    def question_count(self,obj):return obj.questions.count()
    def get_readonly_fields(self,request,obj=None):
        return ['title','section','version','duration_seconds','passage','audio_file','audio_url','published'] if obj and obj.published else ['published']
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
