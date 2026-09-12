from django.contrib import admin
from .models import Exam,Question,Attempt,Profile,Entitlement
class Questions(admin.TabularInline):
    model=Question;extra=1
    def has_change_permission(self,request,obj=None): return not obj or not obj.published
    def has_add_permission(self,request,obj=None): return not obj or not obj.published
    def has_delete_permission(self,request,obj=None): return not obj or not obj.published
@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display=['title','section','version','published'];list_filter=['section','published'];inlines=[Questions]
    def get_readonly_fields(self,request,obj=None):
        return ['title','section','version','duration_seconds','passage','audio_url','published'] if obj and obj.published else []
    def has_delete_permission(self,request,obj=None): return not obj or not obj.published
@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display=['id','user','exam','state','started_at']
    def get_readonly_fields(self,request,obj=None): return [f.name for f in self.model._meta.fields]
    def has_add_permission(self,request): return False
    def has_delete_permission(self,request,obj=None): return False
admin.site.register(Entitlement)
admin.site.site_header='IELTSQA — testlarni boshqarish'
