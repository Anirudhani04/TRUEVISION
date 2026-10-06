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
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='text_analyses')
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
    analysis_image = models.ImageField(
        upload_to='image_analysis/results/%Y/%m/%d/',
        null=True,
        blank=True,
        max_length=500,
        help_text='Visual analysis result with ELA, edges, and detection overlay'
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


class DocumentForgery(models.Model):
    ANALYSIS_TYPES = [
        ('forgery', 'Document Forgery Detection'),
        ('plagiarism', 'Document Plagiarism Detection'),
        ('ai-detection', 'Document AI Detection'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    # Basic information
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='document_analyses', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Analysis type and status
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # File information
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField()  # Size in bytes
    file_type = models.CharField(max_length=50)
    
    # Document content
    document_text = models.TextField()
    text_preview = models.TextField()
    word_count = models.IntegerField(default=0)
    # Analysis results
    result = models.CharField(max_length=100)  # e.g., 'Authentic', 'Forged', 'AI Generated'
    confidence = models.IntegerField()  # Percentage 0-100%
    
    # Forgery-specific analysis data stored as JSON
    forgery_indicators = models.JSONField(default=list, blank=True)
    technical_details = models.JSONField(default=dict, blank=True)
    metadata_analysis = models.JSONField(default=dict, blank=True)
    
    # Similarity data for plagiarism detection
    match_percent = models.IntegerField(default=0)
    matched_document_id = models.IntegerField(null=True, blank=True)
    matched_excerpt = models.TextField(blank=True)
    
    # Processing timestamps
    analysis_started_at = models.DateTimeField(null=True, blank=True)
    analysis_completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'document_forgery'
        ordering = ['-created_at']
        verbose_name = 'Document Forgery Analysis'
        verbose_name_plural = 'Document Forgery Analyses'

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
        """Get CSS color class based on result"""
        result_lower = self.result.lower()
        if 'authentic' in result_lower or 'human' in result_lower or 'original' in result_lower:
            return 'text-emerald-600'
        elif 'suspicious' in result_lower or 'uncertain' in result_lower or 'possible' in result_lower:
            return 'text-amber-600'
        else:
            return 'text-red-600'


class IntegrityCheck(models.Model):
    """Model for file integrity verification and checksums"""
    
    VERIFICATION_TYPE_CHOICES = [
        ('hash', 'Hash Verification'),
        ('signature', 'Digital Signature'),
        ('blockchain', 'Blockchain Verification'),
        ('checksum', 'Checksum Verification'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    INTEGRITY_RESULT_CHOICES = [
        ('authentic', 'Authentic - Verified'),
        ('modified', 'Modified - Changes Detected'),
        ('corrupted', 'Corrupted - Data Integrity Failed'),
        ('unknown', 'Unknown - Unable to Verify'),
    ]
    
    # User association (optional for API access)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='integrity_checks'
    )
    
    # File information
    file_name = models.CharField(max_length=500)
    file_size = models.BigIntegerField()
    file_type = models.CharField(max_length=100)
    file_hash = models.CharField(max_length=256, db_index=True)    
    # Verification details
    verification_type = models.CharField(
        max_length=20, 
        choices=VERIFICATION_TYPE_CHOICES, 
        default='hash'
    )
    verification_method = models.CharField(max_length=50)  # e.g., SHA-256, MD5, RSA
    
    # Results
    result = models.CharField(
        max_length=20, 
        choices=INTEGRITY_RESULT_CHOICES, 
        default='unknown'
    )
    confidence = models.FloatField(default=0.0)  # 0-100 confidence score
    is_authentic = models.BooleanField(default=False)
    
    # Detailed analysis
    hash_comparison = models.JSONField(default=dict, blank=True)  # Original vs Current hash
    signature_details = models.JSONField(default=dict, blank=True)  # Digital signature info
    modification_details = models.JSONField(default=list, blank=True)  # List of modifications
    checksums = models.JSONField(default=dict, blank=True)  # Various checksums (MD5, SHA1, SHA256)
    
    # Metadata analysis
    created_timestamp = models.DateTimeField(null=True, blank=True)
    modified_timestamp = models.DateTimeField(null=True, blank=True)
    accessed_timestamp = models.DateTimeField(null=True, blank=True)
    file_metadata = models.JSONField(default=dict, blank=True)
    
    # Verification chain
    previous_verification_id = models.ForeignKey(
        'self', 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        related_name='next_verification'
    )
    verification_history = models.JSONField(default=list, blank=True)
    
    # Status and tracking
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)
    
    # Report and recommendations
    findings = models.JSONField(default=list, blank=True)  # List of findings
    recommendations = models.JSONField(default=list, blank=True)  # Recommendations
    red_flags = models.JSONField(default=list, blank=True)  # Critical issues
    
    # Technical details
    technical_details = models.JSONField(default=dict, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'file_hash']
        indexes = [
            models.Index(fields=['file_hash']),
            models.Index(fields=['verification_type']),
            models.Index(fields=['status']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['result']),
        ]
        verbose_name = 'Integrity Check'
        verbose_name_plural = 'Integrity Checks'
    
    def __str__(self):
        return f"{self.file_name} - {self.result} ({self.verification_type})"
    
    def get_verification_type_display_long(self):
        """Get full display name for verification type"""
        return dict(self.VERIFICATION_TYPE_CHOICES).get(self.verification_type, 'Unknown')
    
    def is_verified_authentic(self):
        """Check if file is verified as authentic"""
        return self.result == 'authentic' and self.confidence >= 90
    
    def has_modifications(self):
        """Check if file has modifications"""
        return self.result == 'modified'
    
    def get_risk_level(self):
        """Determine risk level based on result"""
        if self.result == 'authentic':
            return 'Low'
        elif self.result == 'modified':
            return 'High'
        elif self.result == 'corrupted':
            return 'Critical'
        else:
            return 'Unknown'
    
    def calculate_integrity_score(self):
        """Calculate overall integrity score (0-100)"""
        if self.result == 'authentic':
            return 100
        elif self.result == 'modified':
            return max(0, 100 - len(self.modification_details) * 15)
        elif self.result == 'corrupted':
            return 0
        else:
            return 50


class IntegrityCheckHistory(models.Model):
    """Model to track integrity check history for comparison"""
    
    integrity_check = models.ForeignKey(
        IntegrityCheck, 
        on_delete=models.CASCADE, 
        related_name='history_records'
    )
    
    # Historical data
    previous_hash = models.CharField(max_length=256, blank=True)
    current_hash = models.CharField(max_length=256)
    change_detected = models.BooleanField(default=False)
    
    # Change details
    change_details = models.JSONField(default=dict, blank=True)
    modification_timestamp = models.DateTimeField(null=True, blank=True)
    
    # Verification result at this point
    verification_result = models.CharField(max_length=50, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Integrity Check History'
        verbose_name_plural = 'Integrity Check Histories'
    
    def __str__(self):
        return f"History: {self.integrity_check.file_name} - {self.created_at}"