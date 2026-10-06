from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
   

    def __str__(self):
        return self.user.username


class TextAnalysis(models.Model):
    ANALYSIS_CHOICES = [
        ('plagiarism', 'Plagiarism Detection'),
        ('ai-detection', 'AI Detection'),
    ]

    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    text_preview = models.TextField()
    full_text = models.TextField()
    analysis_type = models.CharField(max_length=32, choices=ANALYSIS_CHOICES)
    result = models.CharField(max_length=64)
    confidence = models.IntegerField()
    word_count = models.IntegerField()
    # Store embeddings as JSON string (list of floats)
    embedding = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.analysis_type} - {self.id}"

from django.core.validators import FileExtensionValidator
class ImageAnalysis(models.Model):
    ANALYSIS_TYPES = [
        ('forgery', 'Image Forgery Detection'),
        ('ai-detection', 'AI Generated Detection'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # Basic information
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_analyses')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Analysis type and status
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # File information
    original_image = models.ImageField(
        upload_to='image_analysis/original/%Y/%m/%d/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'])],
        max_length=500
    )
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # Size in bytes
    file_type = models.CharField(max_length=50)
    
    # Analysis results (matching dashboard.html functionality)
    result = models.CharField(max_length=50)  # e.g., 'Authentic', 'Forged', 'AI Generated', 'Human Created'
    confidence = models.IntegerField()  # Percentage 0-100%
    
    # Technical analysis data stored as JSON
    technical_details = models.JSONField(default=dict, blank=True)
    
    # Metadata extracted from image
    metadata = models.JSONField(default=dict, blank=True)
    
    # Processing timestamps
    analysis_started_at = models.DateTimeField(null=True, blank=True)
    analysis_completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'image_analysis'
        ordering = ['-created_at']
        verbose_name = 'Image Analysis'
        verbose_name_plural = 'Image Analyses'

    def __str__(self):
        return f"{self.file_name} - {self.get_analysis_type_display()} - {self.result}"

    @property
    def processing_time(self):
        """Calculate processing time in seconds"""
        if self.analysis_started_at and self.analysis_completed_at:
            return (self.analysis_completed_at - self.analysis_started_at).total_seconds()
        return None

    @property
    def confidence_percentage(self):
        """Return confidence as percentage string"""
        return f"{self.confidence}%"

    def get_result_color(self):
        """Get CSS color class based on result (matching dashboard.html)"""
        result_lower = self.result.lower()
        if 'authentic' in result_lower or 'human' in result_lower:
            return 'text-emerald-600'
        elif 'suspicious' in result_lower or 'uncertain' in result_lower or 'mixed' in result_lower:
            return 'text-amber-600'
        else:
            return 'text-red-600'