# 📸 Seen for Photos - Secure One-Time Photo Sharing

A privacy-focused photo sharing service that allows users to share photos with custom view limits, PIN protection, and automatic deletion. Photos are automatically deleted after being viewed or after 24 hours, ensuring no permanent storage of user data.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v3.0.0-green.svg)
![AWS S3](https://img.shields.io/badge/AWS-S3-orange.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

#### 💎 You can please access the service at [photos.nyvs.me](photos.nyvs.me) 💎
---

## 🎯 Features

### Core Functionality
- **One-Time Photo Sharing**: Photos can be set to disappear after a single view
- **Custom View Limits**: Choose between 1, 3, 5, 10 views, or unlimited views (24-hour expiry)
- **Automatic Deletion**: All photos are automatically deleted after 24 hours via S3 lifecycle policies
- **No Permanent Storage**: Photos are immediately deleted from S3 after reaching view limit

### Security Features
- **PIN Protection**: Optional 4-digit PIN requirement for viewing photos
- **Download Prevention**: Disable right-click and drag-to-save functionality
- **Unique Token URLs**: Non-guessable URLs using UUID tokens
- **Hashed PIN Storage**: PINs are hashed using SHA-256 before storage

### User Experience
- **Drag & Drop Upload**: Simple drag-and-drop interface for photo uploads
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Copy-to-Clipboard**: Easy sharing with one-click URL copying
- **Real-time Feedback**: View count tracking and expiration status

## 🛠️ Tech Stack

### Backend
- **Python 3.8+**: Core programming language
- **Flask 3.0.0**: Lightweight web framework
- **Gunicorn**: Production WSGI HTTP server

### Cloud Services
- **AWS S3**: Object storage for temporary photo hosting
- **S3 Lifecycle Policies**: Automatic cleanup of expired photos

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with gradients and animations
- **Vanilla JavaScript**: No framework dependencies
- **Responsive Design**: Mobile-first approach

### Security
- **python-dotenv**: Environment variable management
- **SHA-256**: PIN hashing
- **UUID**: Token generation

## 📋 Prerequisites

- Python 3.8 or higher
- AWS Account with S3 access, AWS Access Key ID and Secret Access Key

## 🚀 Installation

### 1. Clone the repository
```bash
git clone https://github.com/Kaitzz/seen-photos-python
cd seen-photos-python
```

### 2. Create virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file in the root directory:
```env
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name
SECRET_KEY=your-flask-secret-key
```

### 5. Set up S3 Lifecycle Policy
Run the setup script to configure automatic photo deletion:
```bash
python setup_s3.py
```

### 6. Run the application
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## 📁 Project Structure

```
Seen-Photos-Python/
│
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── storage.py             # S3 storage operations
├── setup_s3.py           # S3 lifecycle policy setup
├── requirements.txt       # Python dependencies
├── .env                  # Environment variables (not in git)
├── .gitignore            # Git ignore rules
│
├── templates/            # HTML templates
│   ├── upload.html       # Upload interface
│   └── view.html         # Photo viewing page
│
└── venv/                 # Virtual environment (not in git)
```

## 🔧 Configuration

### S3 Bucket Settings
- Enable versioning: Optional
- Configure CORS for your domain
- Set lifecycle policy for 24-hour deletion
- Ensure bucket is private (no public access)

### Application Settings (in `config.py`)
- `PHOTO_EXPIRATION`: 86400 seconds (24 hours)
- `MAX_CONTENT_LENGTH`: 10MB file size limit
- `ALLOWED_EXTENSIONS`: png, jpg, jpeg, gif, webp

## 🌐 Deployment

### Deploy to Render (Recommended)

1. Push code to GitHub
2. Connect repository to Render
3. Configure environment variables
4. Deploy with one click

### Deploy to AWS EC2

1. Launch EC2 instance
2. Install Python and dependencies
3. Configure Nginx as reverse proxy
4. Set up SSL with Let's Encrypt
5. Use systemd for process management

### Deploy to Heroku

1. Create `Procfile`:
```
web: gunicorn app:app
```
2. Deploy using Heroku CLI
3. Set environment variables

### Security Considerations

- **Environment Variables**: Never commit `.env` file to version control
- **AWS Credentials**: Use IAM roles in production, not root credentials
- **HTTPS Only**: Always use SSL in production
- **Rate Limiting**: Consider adding rate limiting for production use
- **Input Validation**: File type and size validation implemented
- **Token Security**: UUIDs are cryptographically secure

#### S3 Lifecycle Policy

The application automatically configures S3 lifecycle rules to:
- Delete photos after 24 hours if not accessed
- Remove incomplete multipart uploads
- Clean up expired object markers

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🚨 Disclaimer
Remember to configure your S3 bucket with appropriate lifecycle policies and CORS settings for production use. The application automatically deletes photos, but S3 lifecycle policies provide an additional safety net.