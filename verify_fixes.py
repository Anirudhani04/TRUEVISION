import os
import django
import json
from django.test import RequestFactory
from django.contrib.auth.models import User

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Forensic.settings')
django.setup()

from App.views import admin_text_history, admin_document_history

def verify_history_views():
    factory = RequestFactory()
    
    # Create or get an admin user
    user, created = User.objects.get_or_create(username='test_admin', is_staff=True, is_superuser=True)
    
    # 1. Test admin_text_history
    request = factory.get('/api/admin/text/history/')
    request.user = user
    
    response = admin_text_history(request)
    data = json.loads(response.content)
    
    if data['success']:
        print("SUCCESS: admin_text_history returned successfully.")
        if data['history']:
            item = data['history'][0]
            if 'wordCount' in item:
                print(f"VERIFIED: 'wordCount' exists in text history: {item['wordCount']}")
            else:
                print("FAILED: 'wordCount' missing from text history.")
        else:
            print("INFO: No text history entries found to verify 'wordCount'.")
    else:
        print(f"FAILED: admin_text_history error: {data.get('message')}")

    # 2. Test admin_document_history
    request = factory.get('/api/admin/document/history/')
    request.user = user
    
    response = admin_document_history(request)
    data = json.loads(response.content)
    
    if data['success']:
        print("SUCCESS: admin_document_history returned successfully.")
        if data['history']:
            item = data['history'][0]
            if 'word_count' in item:
                print(f"VERIFIED: 'word_count' exists in document history: {item['word_count']}")
            else:
                print("FAILED: 'word_count' missing from document history.")
        else:
            print("INFO: No document history entries found to verify 'word_count'.")
    else:
        print(f"FAILED: admin_document_history error: {data.get('message')}")

if __name__ == '__main__':
    verify_history_views()
