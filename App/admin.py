from django.contrib import admin
from .models import *
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
@admin.register(ImageAnalysis)
class ImageAnalysisAdmin(admin.ModelAdmin):          
    list_display = ('id', 'user', 'analysis_type', 'status', 'created_at')
    search_fields = ('user__username', 'analysis_type', 'status')
    list_filter = ('analysis_type', 'status')
@admin.register(DocumentForgery) 
class DocumentForgeryAdmin(admin.ModelAdmin):       
    list_display = ('id', 'user', 'analysis_type', 'status', 'created_at')
    search_fields = ('user__username', 'analysis_type', 'status')
    list_filter = ('analysis_type', 'status')

@admin.register(IntegrityCheck)
class IntegrityCheckAdmin(admin.ModelAdmin):
    list_display = ('id', 'file_name', 'verification_type', 'verification_method', 'result', 'confidence', 'is_authentic', 'created_at')
    search_fields = ('file_name', 'file_hash', 'result', 'verification_type')
    list_filter = ('verification_type', 'verification_method', 'result', 'is_authentic', 'status')
    readonly_fields = ('file_hash', 'created_at', 'updated_at')
    fieldsets = (
        ('File Information', {
            'fields': ('file_name', 'file_size', 'file_type', 'file_hash')
        }),
        ('Verification Details', {
            'fields': ('verification_type', 'verification_method', 'result', 'confidence', 'is_authentic')
        }),
        ('Analysis Data', {
            'fields': ('hash_comparison', 'checksums', 'signature_details', 'technical_details')
        }),
        ('Metadata & History', {
            'fields': ('file_metadata', 'created_timestamp', 'modified_timestamp', 'accessed_timestamp', 'verification_history')
        }),
        ('Findings & Recommendations', {
            'fields': ('findings', 'recommendations', 'red_flags')
        }),
        ('Status & Timestamps', {
            'fields': ('status', 'error_message', 'created_at', 'updated_at')
        }),
    )

@admin.register(IntegrityCheckHistory)
class IntegrityCheckHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'integrity_check', 'change_detected', 'verification_result', 'created_at')
    search_fields = ('integrity_check__file_name', 'previous_hash', 'current_hash')
    list_filter = ('change_detected', 'verification_result', 'created_at')
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Integrity Check Reference', {
            'fields': ('integrity_check',)
        }),
        ('Hash Information', {
            'fields': ('previous_hash', 'current_hash', 'change_detected')
        }),
        ('Change Details', {
            'fields': ('change_details', 'modification_timestamp')
        }),
        ('Verification Result', {
            'fields': ('verification_result', 'created_at')
        }),
    )