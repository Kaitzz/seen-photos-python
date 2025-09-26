from flask import Flask, render_template, request, jsonify, Response, abort
import uuid
import os
import hashlib
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from storage import S3Storage
from config import Config
from flask_cors import CORS
import json

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, origins=['https://photos.nyvs.me/'])
# Initialize S3 storage
storage = S3Storage()

# In-memory store for token to S3 key mapping
# In production, use Redis or a database
token_store = {}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Display upload page"""
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_photo():
    """Handle photo upload with enhanced options"""
    if 'photo' not in request.files:
        return jsonify({'error': 'No photo provided'}), 400
    
    file = request.files['photo']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Allowed: jpg, jpeg, png, gif, webp'}), 400
    
    # Get options from form
    max_views = int(request.form.get('max_views', 1))
    pin = request.form.get('pin', '').strip()
    prevent_download = request.form.get('prevent_download', 'false') == 'true'
    
    # Validate PIN if provided
    if pin and (not pin.isdigit() or len(pin) != 4):
        return jsonify({'error': 'PIN must be exactly 4 digits'}), 400
    
    # Hash PIN if provided
    pin_hash = hashlib.sha256(pin.encode()).hexdigest() if pin else None
    
    # Get file extension
    file_extension = file.filename.rsplit('.', 1)[1].lower()
    
    # Read file data
    file_data = file.read()
    
    # Check file size
    if len(file_data) > Config.MAX_CONTENT_LENGTH:
        return jsonify({'error': 'File too large. Max 10MB'}), 400
    
    # Upload to S3
    photo_key = storage.upload_photo(file_data, file_extension)
    
    if not photo_key:
        return jsonify({'error': 'Upload failed'}), 500
    
    # Generate unique token for URL
    token = str(uuid.uuid4())
    
    # Store token with metadata
    token_store[token] = {
        's3_key': photo_key,
        'max_views': max_views,
        'views_remaining': max_views,
        'pin_hash': pin_hash,
        'prevent_download': prevent_download,
        'created_at': datetime.utcnow().isoformat(),
        'expires_at': (datetime.utcnow() + timedelta(hours=24)).isoformat()
    }
    
    # Generate URL
    one_time_url = f"{request.host_url}view/{token}"
    
    # Prepare response message
    if max_views == -1:
        view_message = "This link will work unlimited times for 24 hours."
    elif max_views == 1:
        view_message = "This link will work only once."
    else:
        view_message = f"This link will work {max_views} times."
    
    if pin:
        view_message += f" PIN protection enabled."
    
    return jsonify({
        'success': True,
        'url': one_time_url,
        'message': f'Photo uploaded! {view_message}',
        'details': {
            'max_views': max_views,
            'pin_protected': bool(pin),
            'download_prevented': prevent_download
        }
    })

@app.route('/view/<token>')
def view_photo_page(token):
    """Display photo view page with PIN entry if needed"""
    # Check if token exists
    if token not in token_store:
        return render_template('view.html', error="Photo not found or link expired"), 404
    
    photo_data = token_store[token]
    
    # Check if expired
    if datetime.fromisoformat(photo_data['expires_at']) < datetime.utcnow():
        del token_store[token]
        storage.delete_photo(photo_data['s3_key'])
        return render_template('view.html', error="Link has expired"), 404
    
    # Check if views exhausted
    if photo_data['max_views'] != -1 and photo_data['views_remaining'] <= 0:
        return render_template('view.html', error="Maximum views reached"), 404
    
    return render_template('view.html', 
                         token=token, 
                         pin_required=bool(photo_data['pin_hash']),
                         prevent_download=photo_data['prevent_download'],
                         views_remaining=photo_data['views_remaining'])

@app.route('/api/view/<token>', methods=['POST'])
def api_view_photo(token):
    """API endpoint to view photo with PIN verification"""
    if token not in token_store:
        return jsonify({'error': 'Photo not found'}), 404
    
    photo_data = token_store[token]
    
    # Check PIN if required
    if photo_data['pin_hash']:
        provided_pin = request.json.get('pin', '')
        if hashlib.sha256(provided_pin.encode()).hexdigest() != photo_data['pin_hash']:
            return jsonify({'error': 'Invalid PIN'}), 403
    
    # Decrement view count
    if photo_data['max_views'] != -1:
        photo_data['views_remaining'] -= 1
        
        # If no views remaining, prepare for deletion
        if photo_data['views_remaining'] <= 0:
            # Get photo before deleting
            photo_bytes, content_type = storage.get_photo(photo_data['s3_key'])
            
            # Clean up
            del token_store[token]
            storage.delete_photo(photo_data['s3_key'])
        else:
            # Just get the photo
            photo_bytes, content_type = storage.get_photo(photo_data['s3_key'])
    else:
        # Unlimited views for 24h
        photo_bytes, content_type = storage.get_photo(photo_data['s3_key'])
    
    if not photo_bytes:
        return jsonify({'error': 'Failed to retrieve photo'}), 500
    
    # Convert to base64 for JSON response
    import base64
    photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')
    
    return jsonify({
        'success': True,
        'image': f'data:{content_type};base64,{photo_base64}',
        'views_remaining': photo_data['views_remaining'] if photo_data['max_views'] != -1 else 'unlimited',
        'prevent_download': photo_data['prevent_download']
    })

@app.route('/api/cleanup', methods=['POST'])
def cleanup_expired():
    """Clean up expired photos (can be called periodically)"""
    current_time = datetime.utcnow()
    expired_tokens = []
    
    for token, data in token_store.items():
        if datetime.fromisoformat(data['expires_at']) < current_time:
            expired_tokens.append(token)
            storage.delete_photo(data['s3_key'])
    
    for token in expired_tokens:
        del token_store[token]
    
    return jsonify({'cleaned': len(expired_tokens)})

@app.route('/view/<token>')
def view_photo(token):
    """View and delete photo"""
    # Check if token exists
    if token not in token_store:
        abort(404, description="Photo not found or already viewed")
    
    # Get S3 key
    photo_key = token_store[token]
    
    # Remove token immediately (one-time use)
    del token_store[token]
    
    # Get and delete photo from S3
    photo_data, content_type = storage.get_and_delete_photo(photo_key)
    
    if not photo_data:
        abort(404, description="Photo not found")
    
    return Response(photo_data, mimetype=content_type)

@app.errorhandler(404)
def not_found(e):
    """Custom 404 page"""
    return render_template('upload.html', error="Photo not found or already viewed"), 404

if __name__ == '__main__':
    # Use environment variable for port if available (for deployment)
    port = int(os.environ.get('PORT', 5000))
    # Disable debug in production
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)