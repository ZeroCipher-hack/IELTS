from django.contrib import admin,messages
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Exam,Question,Attempt,Profile,Entitlement
from .services import validate_exam

class Questions(admin.StackedInline):
    model=Question
    extra=0
    fields=['position','prompt','choices','accepted_answers','skill_tag','evidence','explanation']
    def has_change_permission(self,request,obj=None):return not obj or not obj.published
    def has_add_permission(self,request,obj=None):return not obj or not obj.published
    def has_delete_permission(self,request,obj=None):return not obj or not obj.published

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display=['title','section','version','published','duration_seconds']
    list_filter=['section','published']
    search_fields=['title']
    inlines=[Questions]
    actions=['publish_checked','duplicate_draft']
    def get_readonly_fields(self,request,obj=None):
        return ['title','section','version','duration_seconds','passage','audio_url','published'] if obj and obj.published else ['published']
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
