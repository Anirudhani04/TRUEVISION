#!/usr/bin/env python3
"""Add missing imports to views.py"""

import sys

# Read the file
with open('App/views.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the line with "from django.http import JsonResponse, HttpResponseBadRequest"
# and add the missing imports after it
new_lines = []
for i, line in enumerate(lines):
    new_lines.append(line)
    if 'from django.http import JsonResponse, HttpResponseBadRequest' in line:
        # Add the missing imports
        new_lines.append('from django.views.decorators.csrf import csrf_exempt\n')
        new_lines.append('from django.views.decorators.http import require_http_methods\n')
        new_lines.append('import json\n')
        new_lines.append('import re\n')
        new_lines.append('import math\n')
        new_lines.append('import os\n')
        new_lines.append('import requests\n')
        new_lines.append('import hashlib\n')
        new_lines.append('import google.generativeai as genai\n')
        new_lines.append('from django.conf import settings\n')
        new_lines.append('from django.utils.text import Truncator\n')
        new_lines.append('from difflib import SequenceMatcher\n')
        new_lines.append('import numpy as np\n')
        new_lines.append('from sklearn.feature_extraction.text import TfidfVectorizer\n')
        new_lines.append('from sklearn.metrics.pairwise import cosine_similarity\n')

# Write back
with open('App/views.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Successfully added missing imports to views.py")
