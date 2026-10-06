from django.contrib import admin
from .models import Profile
from .models import TextAnalysis
# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username', 'user__email')
    list_filter = ('user__is_staff', 'user__is_active')


@admin.register(TextAnalysis)
class TextAnalysisAdmin(admin.ModelAdmin):
    list_display = ('id', 'analysis_type', 'result', 'confidence', 'word_count', 'created_at')
    search_fields = ('text_preview', 'full_text', 'analysis_type', 'result')
    list_filter = ('analysis_type', 'result')