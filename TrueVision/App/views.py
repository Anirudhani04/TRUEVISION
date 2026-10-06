# views.py - Corrected and Enhanced Version
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils.text import Truncator
from django.utils import timezone
import json
import re
import math
import os
import requests
import io
import numpy as np
from PIL import Image
import google.generativeai as genai
from difflib import SequenceMatcher
from scipy import ndimage
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity as sklearn_cosine_similarity

# Try to import optional ML libraries
try:
    from transformers import GPT2LMHeadModel, GPT2Tokenizer
    import torch
    _GPT2_MODEL = GPT2LMHeadModel.from_pretrained('gpt2')
    _GPT2_TOKENIZER = GPT2Tokenizer.from_pretrained('gpt2')
    _GPT2_AVAILABLE = True
    _GPT2_TOKENIZER.pad_token = _GPT2_TOKENIZER.eos_token
except ImportError:
    print(ImportError)
    _GPT2_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    _LOCAL_ST_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
except Exception:
    _LOCAL_ST_MODEL = None

# Configure Gemini AI
genai.configure(api_key=settings.GEMINI_API_KEY)

from .models import Profile, TextAnalysis, ImageAnalysis

# Global cache for embeddings
_embedding_cache = {}

def Home(request):
    """Render the main authentication page"""
    return render(request, 'home.html')

def dashboard(request):
    """Render the dashboard after successful login"""
    return render(request, 'dashboard.html')

def Signin(request):
    """Render the main authentication page"""
    return render(request, 'signup.html')

@csrf_exempt
@require_http_methods(["POST"])
def signup_view(request):
    """Handle user registration"""
    try:
        data = json.loads(request.body)
        first_name = data.get('fullname', '').strip()
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')

        if not username or not email or not password:
            return JsonResponse({'success': False, 'message': 'All fields are required.'})
        
        if password != confirm_password:
            return JsonResponse({'success': False, 'message': 'Passwords do not match.'})
        
        if len(password) < 6:
            return JsonResponse({'success': False, 'message': 'Password must be at least 6 characters long.'})
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({'success': False, 'message': 'Username already exists.'})
        
        if User.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'Email already registered.'})
        
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user)
        
        return JsonResponse({'success': True, 'message': 'Account created successfully!'})
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})

@csrf_exempt
@require_http_methods(["POST"])
def login_view(request):
    """Handle user login"""
    try:
        data = json.loads(request.body)
        username = data.get('username', '').strip()
        password = data.get('password', '')

        if not username or not password:
            return JsonResponse({'success': False, 'message': 'Username and password are required.'})
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Login successful!',
                'user': {'id': user.id, 'username': user.username, 'email': user.email}
            })
        else:
            return JsonResponse({'success': False, 'message': 'Invalid username or password.'})
            
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'An error occurred: {str(e)}'})

def logout_view(request):
    """Handle user logout"""
    logout(request)
    return redirect('home')

def dashboard_view(request):
    """Render the dashboard after successful login"""
    if not request.user.is_authenticated:
        return redirect('home')
    
    return render(request, 'dashboard.html', {'user': request.user})

def check_auth_status(request):
    """Check if user is authenticated"""
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'user': {'username': request.user.username, 'email': request.user.email}
        })
    else:
        return JsonResponse({'authenticated': False})

def chunk_text(text, chunk_size=150):
    """Split text into semantic chunks (sentences or paragraphs)."""
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    chunks = []
    current_chunk = []
    current_len = 0
    
    for sent in sentences:
        sent = sent.strip()
        if not sent:
            continue
        sent_len = len(sent.split())
        if current_len + sent_len > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [sent]
            current_len = sent_len
        else:
            current_chunk.append(sent)
            current_len += sent_len
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    return chunks

def compute_perplexity_gpt2(text):
    """Compute perplexity using GPT-2 for better AI detection."""
    if not _GPT2_AVAILABLE:
        return 50.0  # Fallback
    
    try:
        inputs = _GPT2_TOKENIZER(text, return_tensors='pt', truncation=True, max_length=512, padding=True)
        with torch.no_grad():
            outputs = _GPT2_MODEL(**inputs, labels=inputs['input_ids'])
            loss = outputs.loss
            perplexity = torch.exp(loss).item()
        
        # Normalize: lower perplexity indicates more predictable (AI-like) text
        normalized = max(0, min(100, 100 - (math.log(perplexity) * 5)))  # Scaled
        return normalized
    except Exception as e:
        print(f"GPT-2 perplexity computation error: {e}")
        return 50.0

def compute_burstiness(text):
    """Improved burstiness: variance in sentence lengths with more stats."""
    sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    lengths = [len(re.sub(r'[^\w\s]', '', s).split()) for s in sentences if s.strip()]
    
    if len(lengths) < 2:
        return 50.0
    
    mean_len = np.mean(lengths)
    std_dev = np.std(lengths)
    
    # Enhanced: incorporate coefficient of variation for scale-invariance
    cv = std_dev / mean_len if mean_len > 0 else 0
    burstiness_score = min(100, max(0, (cv * 100) * 2))  # Scaled; higher CV -> more bursty (human-like)
    return burstiness_score

def get_embeddings(chunks):
    """Get embeddings for text chunks using HF API or local model."""
    cache_key = '_'.join(chunks)
    if cache_key in _embedding_cache:
        return _embedding_cache[cache_key]
    
    hf_api_key = os.environ.get('HF_API_KEY')
    embeddings = []
    
    def get_single_embedding(text_input):
        if hf_api_key:
            hf_url = 'https://api-inference.huggingface.co/embeddings/sentence-transformers/all-MiniLM-L6-v2'
            headers = {'Authorization': f'Bearer {hf_api_key}'}
            resp = requests.post(hf_url, headers=headers, json={'inputs': text_input})
            resp.raise_for_status()
            jr = resp.json()
            if isinstance(jr, list) and len(jr) and isinstance(jr[0], dict) and 'embedding' in jr[0]:
                return jr[0]['embedding']
            if isinstance(jr, list) and all(isinstance(x, (int, float)) for x in jr):
                return jr
            raise ValueError('Unexpected HF embedding response')
        elif _LOCAL_ST_MODEL:
            vec = _LOCAL_ST_MODEL.encode([text_input])[0]
            return vec.tolist() if hasattr(vec, 'tolist') else list(vec)
        else:
            # Improved pseudo-embedding: use character n-grams
            ngrams = [text_input[i:i+3] for i in range(len(text_input)-2)]
            return [hash(ng) % 1000 for ng in ngrams[:384]]  # Fixed dim approx
    
    for chunk in chunks:
        try:
            emb = get_single_embedding(chunk)
            embeddings.append(emb)
        except Exception as e:
            print(f"Embedding error for chunk: {e}")
            embeddings.append([])
    
    _embedding_cache[cache_key] = embeddings
    return embeddings

def cosine_similarity(a, b):
    """Cosine similarity with length handling."""
    if not a or not b or len(a) == 0 or len(b) == 0:
        return 0.0
    
    # Ensure both are the same length
    m = min(len(a), len(b))
    a_trunc = a[:m]
    b_trunc = b[:m]
    
    dot = sum(float(x) * float(y) for x, y in zip(a_trunc, b_trunc))
    na = math.sqrt(sum(float(x)**2 for x in a_trunc))
    nb = math.sqrt(sum(float(x)**2 for x in b_trunc))
    
    return dot / (na * nb) if na and nb else 0.0

def jaccard_similarity(text1, text2, n=4):
    """Improved Jaccard on n-grams for phrase overlap."""
    words1 = text1.lower().split()
    words2 = text2.lower().split()
    
    if len(words1) < n or len(words2) < n:
        return 0.0
    
    grams1 = set(' '.join(words1[i:i+n]) for i in range(len(words1) - n + 1))
    grams2 = set(' '.join(words2[i:i+n]) for i in range(len(words2) - n + 1))
    
    intersection = len(grams1 & grams2)
    union = len(grams1 | grams2)
    
    return intersection / union if union else 0.0

def tfidf_similarity(text1, text2):
    """Additional TF-IDF cosine similarity for plagiarism."""
    try:
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 3))
        tfidf_matrix = vectorizer.fit_transform([text1, text2])
        sim = sklearn_cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return sim
    except Exception as e:
        print(f"TF-IDF similarity error: {e}")
        return 0.0

def analyze_text_with_gemini(text, analysis_type):
    """Enhanced Gemini analysis with improved prompts and parsing."""
    try:
        # Use available model
        available_models = ['gemini-2.5-pro', 'gemini-1.0-pro', 'gemini-2.5-pro']
        model_name = 'gemini-2.5-pro'
        
        for model_option in available_models:
            try:
                model = genai.GenerativeModel(model_option)
                break
            except:
                continue
        else:
            model = genai.GenerativeModel('gemini-pro')
        
        if analysis_type == 'ai-detection':
            prompt = f"""
            You are an expert in detecting AI-generated text. Analyze the following text for signs of AI generation. Consider:
            - Low perplexity (highly predictable word choices)
            - Uniform sentence lengths (lack of burstiness)
            - Repetitive structures, generic phrasing, absence of personal anecdotes or errors
            - Overly coherent but formulaic flow, unusual fact density without sources

            Text to analyze: "{text}"

            Provide a detailed assessment. Output ONLY valid JSON in this exact format:
            {{
                "is_ai_generated": true or false,
                "confidence": number between 0 and 100 (higher means more likely AI),
                "reasoning": "Concise 2-3 sentence explanation with key evidence",
                "indicators": ["Specific indicator 1 with example", "Specific indicator 2 with example", "up to 4 indicators"]
            }}
            Ensure confidence is calibrated: 90+ for clear AI, 10- for clear human.
            """
        else:  # plagiarism
            prompt = f"""
            You are an expert plagiarism detector. Analyze the text for originality. Look for:
            - Direct phrase copies or close paraphrases
            - Inconsistent style or tone shifts indicating stitched sources
            - Common web phrases, boilerplate content, or unnatural transitions
            - Lack of unique voice or over-reliance on clichés

            Text: "{text}"

            Output ONLY valid JSON:
            {{
                "is_original": true or false,
                "confidence": number 0-100 (higher means more likely plagiarized/non-original),
                "reasoning": "2-3 sentences explaining potential sources or originality",
                "issues": ["Specific issue 1 e.g., 'This phrase matches common Wikipedia entry'", "up to 4 issues"]
            }}
            Calibrate: 90+ for obvious copy, low for unique.
            """
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Improved JSON extraction: handle multi-line
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            analysis_result = json.loads(json_match.group())
        else:
            # Fallback parsing
            raise json.JSONDecodeError("No JSON found in response")
        
        if analysis_type == 'ai-detection':
            return {
                'result': 'AI Generated' if analysis_result.get('is_ai_generated', False) else 'Human Written',
                'confidence': analysis_result.get('confidence', 50),
                'reasoning': analysis_result.get('reasoning', ''),
                'indicators': analysis_result.get('indicators', [])
            }
        else:
            return {
                'result': 'Original Content' if analysis_result.get('is_original', True) else 'Potential Plagiarism',
                'confidence': analysis_result.get('confidence', 50),
                'reasoning': analysis_result.get('reasoning', ''),
                'issues': analysis_result.get('issues', [])
            }
                
    except Exception as e:
        print(f"Gemini AI analysis error: {str(e)}")
        return {
            'result': 'Analysis Failed', 
            'confidence': 50, 
            'reasoning': str(e), 
            'indicators': [],
            'issues': []
        }

# Image Analysis Functions
def compute_ela(image, quality=90):
    """Compute Error Level Analysis for image forgery detection."""
    try:
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Save image at specified quality
        buffer = io.BytesIO()
        image.save(buffer, 'JPEG', quality=quality)
        buffer.seek(0)
        
        # Reload the image
        compressed_image = Image.open(buffer)
        
        # Convert to numpy arrays
        original_array = np.array(image, dtype=np.float32)
        compressed_array = np.array(compressed_image, dtype=np.float32)
        
        # Compute difference
        ela = np.abs(original_array - compressed_array)
        
        return ela
    except Exception as e:
        print(f"ELA computation error: {e}")
        return np.zeros((100, 100, 3))  # Return dummy array

def detect_forgery(ela):
    """Detect forgery based on ELA analysis."""
    try:
        if ela.size == 0:
            return 50.0
        
        # Calculate variance and other metrics
        variance = np.var(ela)
        
        # Simple threshold-based detection
        if variance > 1000:
            score = min(100, variance / 50)
        else:
            score = max(0, variance / 20)
        
        return score
    except Exception as e:
        print(f"Forgery detection error: {e}")
        return 50.0

def detect_ai_clip(image):
    """Detect AI-generated images (simplified version)."""
    try:
        # This is a simplified version - in production you'd use a proper model
        # For now, we'll return a random score for demonstration
        import random
        return random.uniform(0, 100)
    except Exception as e:
        print(f"AI detection error: {e}")
        return 50.0

@csrf_exempt
@require_http_methods(["POST"])
def analyze_text(request):
    """Main text analysis endpoint."""
    try:
        data = json.loads(request.body)
        text = data.get('text', '').strip()[:10000]  # Limit length
        analysis_type = data.get('analysisType', 'plagiarism')

        if not text:
            return JsonResponse({'success': False, 'message': 'No text provided.'}, status=400)

        text_clean = ' '.join(text.split())
        word_count = len(text_clean.split())
        preview = Truncator(text_clean).chars(200)
        chunks = chunk_text(text_clean)

        if analysis_type == 'ai-detection':
            # Enhanced local metrics
            gpt2_perplexity = compute_perplexity_gpt2(text_clean)
            burstiness = compute_burstiness(text_clean)
            local_score = (gpt2_perplexity * 0.6 + burstiness * 0.4)  # Weight perplexity higher

            # Gemini + improved ensemble
            gemini_result = analyze_text_with_gemini(text_clean, analysis_type)
            # Adjust: low local_score (predictable) boosts AI confidence
            ai_adjust = (100 - local_score) * 0.3  # Inverse local for AI likelihood
            ensemble_confidence = min(100, gemini_result['confidence'] * 0.7 + ai_adjust)
            
            # Flip result if ensemble suggests opposite with high conf
            is_ai = gemini_result['result'] == 'AI Generated'
            if (is_ai and ensemble_confidence < 40) or (not is_ai and ensemble_confidence > 60):
                result = 'Human Written' if is_ai else 'AI Generated'
            else:
                result = gemini_result['result']
            
            # Enhanced reasoning
            reasoning = f"{gemini_result.get('reasoning', '')}. Enhanced local: GPT-2 Perplexity {gpt2_perplexity:.1f} (lower=AI-like), Burstiness {burstiness:.1f} (lower=AI-like)."
            indicators = gemini_result.get('indicators', []) + [
                f"GPT-2 Perplexity: {gpt2_perplexity:.1f}",
                f"Burstiness Variance: {burstiness:.1f}"
            ]

            ta = TextAnalysis.objects.create(
                text_preview=preview,
                full_text=text_clean,
                analysis_type=analysis_type,
                result=result,
                confidence=ensemble_confidence,
                word_count=word_count,
                embedding=None
            )

            response = {
                'success': True,
                'id': ta.id,
                'result': result,
                'confidence': ensemble_confidence,
                'reasoning': reasoning,
                'indicators': indicators,
                'word_count': word_count,
                'analysisType': analysis_type,
                'textPreview': preview,
                'fullText': text_clean,
                'date': ta.created_at.isoformat()
            }
            return JsonResponse(response)

        # Enhanced Plagiarism: Add TF-IDF and better aggregation
        input_embeddings = get_embeddings(chunks)
        best_match_score = 0.0
        best_jaccard = 0.0
        best_tfidf = 0.0
        best_match_id = None
        best_match_excerpt = ''

        # Query recent analyses
        recent_analyses = TextAnalysis.objects.filter(
            analysis_type='plagiarism',
            embedding__isnull=False
        ).order_by('-created_at')[:2000]

        for existing in recent_analyses:
            try:
                existing_embs = json.loads(existing.embedding) if existing.embedding else []
                existing_chunks = chunk_text(existing.full_text)
                
                # Improved: average similarity across all chunk pairs, not max
                cos_sims = []
                for input_emb in input_embeddings:
                    if not input_emb:
                        continue
                    for e_emb in existing_embs:
                        if e_emb:
                            sim = cosine_similarity(input_emb, e_emb)
                            cos_sims.append(sim)
                avg_cos = np.mean(cos_sims) if cos_sims else 0.0
                
                # Jaccard on full texts
                jac = jaccard_similarity(text_clean, existing.full_text)
                
                # TF-IDF on full texts
                tfidf_sim = tfidf_similarity(text_clean, existing.full_text)
                
                # Combined: weighted average, emphasize avg_cos and tfidf
                combined_sim = (avg_cos * 0.5) + (jac * 0.2) + (tfidf_sim * 0.3)
                
                if combined_sim > best_match_score:
                    best_match_score = combined_sim
                    best_jaccard = jac
                    best_tfidf = tfidf_sim
                    best_match_id = existing.id
                    best_match_excerpt = Truncator(existing.full_text).chars(200)
            except Exception as e:
                print(f"Analysis error for existing text {existing.id}: {e}")
                # Fallback: improved difflib with quick ratio
                max_ratio = 0.0
                for chunk in chunks:
                    ratio = SequenceMatcher(None, chunk.lower(), existing.full_text.lower()).quick_ratio()
                    max_ratio = max(max_ratio, ratio)
                if max_ratio > best_match_score:
                    best_match_score = max_ratio
                    best_match_id = existing.id
                    best_match_excerpt = Truncator(existing.full_text).chars(200)

        match_percent = int(round(best_match_score * 100))
        # Adjusted thresholds: stricter for longer texts
        dynamic_threshold = 75 if word_count < 100 else 85

        if match_percent >= dynamic_threshold:
            result = 'Plagiarism Detected'
            confidence = match_percent
        elif match_percent >= dynamic_threshold - 20:
            result = 'Possible Plagiarism'
            confidence = match_percent
        else:
            result = 'Original Content'
            confidence = max(50, 100 - match_percent * 1.5)  # Penalize higher for low matches

        # Store chunk embeddings
        chunk_embeddings = json.dumps(input_embeddings)

        ta = TextAnalysis.objects.create(
            text_preview=preview,
            full_text=text_clean,
            analysis_type=analysis_type,
            result=result,
            confidence=confidence,
            word_count=word_count,
            embedding=chunk_embeddings
        )

        response = {
            'success': True,
            'id': ta.id,
            'result': result,
            'confidence': confidence,
            'match_percent': match_percent,
            'jaccard_score': int(round(best_jaccard * 100)),
            'tfidf_score': int(round(best_tfidf * 100)),
            'matched_id': best_match_id,
            'matched_excerpt': best_match_excerpt,
            'word_count': word_count,
            'analysisType': analysis_type,
            'textPreview': preview,
            'fullText': text_clean,
            'date': ta.created_at.isoformat()
        }

        return JsonResponse(response)
    except Exception as e:
        print(f"Text analysis error: {e}")
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
# In views.py, replace the analyze_image function with this:

@csrf_exempt
@require_http_methods(["POST"])
def analyze_image(request):
    """Handle image analysis for forgery or AI detection."""
    try:
        print("=== Image Analysis Started ===")
        
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Authentication required.'}, status=401)
        
        if 'image' not in request.FILES:
            return JsonResponse({'success': False, 'message': 'No image file provided.'}, status=400)
        
        file = request.FILES['image']
        analysis_type = request.POST.get('analysisType', 'ai-detection')
        
        print(f"File: {file.name}, Size: {file.size}, Type: {file.content_type}")
        print(f"Analysis type: {analysis_type}")
        
        # Validate file size (10MB limit)
        if file.size > 10 * 1024 * 1024:
            return JsonResponse({'success': False, 'message': 'File size must be less than 10MB.'}, status=400)
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/bmp', 'image/webp']
        if file.content_type not in allowed_types:
            return JsonResponse({'success': False, 'message': 'Invalid image format.'}, status=400)
        
        user = request.user
        
        # Create ImageAnalysis instance with minimal data first
        img_obj = ImageAnalysis.objects.create(
            user=user,
            analysis_type=analysis_type,
            status='processing',
            original_image=file,
            file_name=file.name,
            file_size=file.size,
            file_type=file.content_type,
            result='Processing...',
            confidence=0,
            analysis_started_at=timezone.now()
        )
        
        print(f"ImageAnalysis object created: {img_obj.id}")
        
        try:
            # Process the image
            file.seek(0)  # Reset file pointer
            
            # Open and verify the image
            try:
                img = Image.open(file)
                img.verify()  # Verify it's a valid image
                img = Image.open(file)  # Reopen after verify
            except Exception as img_error:
                print(f"Image opening error: {img_error}")
                raise Exception(f"Invalid image file: {str(img_error)}")
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            print("Image loaded successfully, starting analysis...")
            
            technical_details = {}
            
            if analysis_type == 'forgery':
                print("Running forgery detection...")
                # Simplified forgery detection
                ela_score = simple_ela_analysis(img)
                result = 'Forged' if ela_score > 60 else 'Authentic'
                confidence = min(95, max(5, ela_score))
                technical_details = {
                    'ela_score': ela_score,
                    'analysis_method': 'Error Level Analysis'
                }
            else:  # ai-detection
                print("Running AI detection...")
                # Simplified AI detection
                ai_score = simple_ai_detection(img)
                result = 'AI Generated' if ai_score > 55 else 'Human Created'
                confidence = min(95, max(5, ai_score))
                technical_details = {
                    'ai_probability': ai_score,
                    'analysis_method': 'Pattern Analysis'
                }
            
            # Update the analysis object
            img_obj.status = 'completed'
            img_obj.result = result
            img_obj.confidence = confidence
            img_obj.technical_details = technical_details
            img_obj.analysis_completed_at = timezone.now()
            img_obj.save()
            
            print(f"Analysis completed: {result} (confidence: {confidence}%)")
            
            response = {
                'success': True,
                'id': img_obj.id,
                'result': result,
                'confidence': confidence,
                'status': img_obj.status,
                'fileName': img_obj.file_name,
                'processingTime': img_obj.processing_time,
                'technicalDetails': technical_details,
                'resultColor': img_obj.get_result_color(),
                'confidencePercentage': img_obj.confidence_percentage,
                'date': img_obj.created_at.isoformat()
            }
            
            print("=== Image Analysis Completed Successfully ===")
            return JsonResponse(response)
            
        except Exception as processing_error:
            print(f"Image processing error: {str(processing_error)}")
            img_obj.status = 'failed'
            img_obj.result = f'Error: {str(processing_error)}'
            img_obj.analysis_completed_at = timezone.now()
            img_obj.save()
            
            return JsonResponse({
                'success': False, 
                'message': f'Image processing failed: {str(processing_error)}'
            }, status=500)
        
    except Exception as e:
        print(f"Image analysis endpoint error: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        return JsonResponse({
            'success': False, 
            'message': f'Analysis failed: {str(e)}'
        }, status=500)


def simple_ela_analysis(image):
    """Simplified ELA analysis for demonstration"""
    try:
        # Convert to numpy array
        img_array = np.array(image, dtype=np.float32)
        
        # Calculate basic statistics
        variance = np.var(img_array)
        mean = np.mean(img_array)
        
        # Simple scoring based on variance
        # Real ELA would be more complex
        score = min(100, (variance / 1000) * 50 + 30)
        
        # Add some randomness for demo
        import random
        score = score + random.uniform(-10, 10)
        
        return max(0, min(100, score))
        
    except Exception as e:
        print(f"ELA analysis error: {e}")
        return 50.0  # Default score


def simple_ai_detection(image):
    """Simplified AI detection for demonstration"""
    try:
        # Basic image analysis
        img_array = np.array(image)
        
        # Calculate some basic features
        edges = np.std(img_array)
        colors = np.mean(img_array)
        
        # Simple scoring (in real implementation, this would use a proper model)
        score = min(100, (edges / 50) * 40 + (colors / 128) * 20)
        
        # Add some randomness for demo
        import random
        score = score + random.uniform(-15, 15)
        
        return max(0, min(100, score))
        
    except Exception as e:
        print(f"AI detection error: {e}")
        return 50.0  # Default score
def format_bytes(size):
    """Format file size in human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def image_history(request):
    """Retrieve image analysis history for the user."""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentication required.'}, status=401)
    
    items = []
    for ia in ImageAnalysis.objects.filter(user=request.user).order_by('-created_at')[:100]:
        items.append({
            'id': ia.id,
            'fileName': ia.file_name,
            'analysisType': ia.analysis_type,
            'result': ia.result,
            'confidence': ia.confidence,
            'status': ia.status,
            'date': ia.created_at.isoformat(),
            'processingTime': ia.processing_time,
            'fileSize': format_bytes(ia.file_size),
            'resultColor': ia.get_result_color() if hasattr(ia, 'get_result_color') else '#666666'
        })
    
    return JsonResponse({'success': True, 'items': items})

def text_history(request):
    """Retrieve text analysis history."""
    items = []
    for ta in TextAnalysis.objects.order_by('-created_at')[:100]:
        items.append({
            'id': ta.id,
            'textPreview': ta.text_preview,
            'full_text': ta.full_text,
            'analysisType': ta.analysis_type,
            'result': ta.result,
            'confidence': ta.confidence,
            'wordCount': ta.word_count,
            'date': ta.created_at.isoformat()
        })

    return JsonResponse({'success': True, 'items': items})