# 🚀 HireReady AI - Setup Guide

## 📋 Prerequisites

- Node.js 18+ 
- Python 3.9+
- Git
- Google Gemini API Key
- Firebase Project (optional for production)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd hireready-ai
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

### 3. Backend Setup
```bash
cd ../backend
pip install -r requirements.txt
```

## 🔧 Configuration

### Frontend Environment Variables
Create `frontend/.env`:
```env
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=hireready-ai.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=hireready-ai
VITE_FIREBASE_STORAGE_BUCKET=hireready-ai.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=your_firebase_app_id
VITE_API_URL=http://localhost:8000
```

### Backend Environment Variables
Create `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key
FIREBASE_PROJECT_ID=hireready-ai
FIREBASE_STORAGE_BUCKET=hireready-ai.appspot.com
THE_MUSE_API_KEY=your_the_muse_api_key
SECRET_KEY=your-secret-key-here
DEBUG=True
```

## 🚀 Running the Application

### Start Backend Server
```bash
cd backend
python main.py
```
Backend will run on: `http://localhost:8000`

### Start Frontend Development Server
```bash
cd frontend
npm run dev
```
Frontend will run on: `http://localhost:3000`

## 🎯 API Endpoints

### Resume Analysis
- `POST /api/resume/upload` - Upload and analyze resume
- `GET /api/resume/analysis/{resume_id}` - Get resume analysis
- `POST /api/resume/extract-skills` - Extract skills from text

### Job Insights
- `POST /api/job/insights` - Get job insights
- `POST /api/job/search` - Search for jobs
- `GET /api/job/popular-roles` - Get popular roles
- `GET /api/job/skills-for-role/{role}` - Get skills for role

### Interview System
- `POST /api/interview/generate-questions` - Generate interview questions
- `POST /api/interview/evaluate-answer` - Evaluate answer
- `POST /api/interview/start-session` - Start interview session
- `POST /api/interview/track-behavior` - Track user behavior

### Analytics
- `POST /api/analytics/dashboard` - Get dashboard data
- `POST /api/analytics/performance-trends` - Get performance trends
- `GET /api/analytics/leaderboard` - Get leaderboard

## 🔑 Getting API Keys

### Google Gemini API
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

### Firebase Setup (Optional)
1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com)
2. Enable Authentication, Firestore, and Storage
3. Copy configuration to frontend `.env`
4. Download service account key for backend

### The Muse API (Optional)
1. Register at [The Muse Developers](https://www.themuse.com/developers)
2. Get API key for job search functionality

## 🎨 Features Implemented

### ✅ Frontend Features
- **Landing Page** - Premium glassmorphic design with animations
- **Resume Upload** - Drag & drop PDF upload with AI analysis
- **Interview Setup** - Company/role configuration with job insights
- **AI Interview Room** - Voice + camera interview with real-time tracking
- **Live Feedback** - Instant AI feedback and suggestions
- **Dashboard** - Comprehensive analytics with charts

### ✅ Backend Features
- **Resume Analysis** - Extract skills, experience, education using NLP
- **Question Generation** - Personalized questions based on resume + job
- **Voice Processing** - Speech-to-text and text-to-speech integration
- **Behavior Tracking** - Eye contact, attention, facial expression analysis
- **Answer Evaluation** - AI-powered scoring and feedback
- **Analytics Engine** - Performance tracking and insights

### ✅ AI Integration
- **Gemini API** - Question generation and answer evaluation
- **Computer Vision** - MediaPipe for face detection and tracking
- **Speech Recognition** - Web Speech API for voice interviews
- **Natural Language Processing** - Resume text analysis and skill extraction

## 🌟 Key Technologies

### Frontend Stack
- **React 18** - Modern UI framework
- **Vite** - Fast development server
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Recharts** - Data visualization
- **React Webcam** - Camera integration
- **Firebase** - Authentication and storage

### Backend Stack
- **FastAPI** - Modern Python web framework
- **Google Generative AI** - Gemini API integration
- **MediaPipe** - Face detection and tracking
- **OpenCV** - Computer vision processing
- **NLTK/spaCy** - Natural language processing
- **PyPDF2** - PDF text extraction

## 🔧 Development Notes

### Frontend Architecture
- Component-based structure with reusable UI elements
- Custom hooks for API integration and state management
- Responsive design with mobile-first approach
- Glassmorphic dark theme with neon accents

### Backend Architecture
- Service-oriented architecture with separation of concerns
- Async/await patterns for better performance
- Comprehensive error handling and logging
- Mock data fallbacks for development

### AI Features
- Resume analysis using NLP and pattern matching
- Dynamic question generation based on user profile
- Real-time behavior tracking and analysis
- Comprehensive answer evaluation with feedback

## 🚀 Deployment

### Frontend Deployment (Vercel/Netlify)
```bash
cd frontend
npm run build
# Deploy the dist/ folder
```

### Backend Deployment (Heroku/Railway)
```bash
cd backend
# Install dependencies and start with gunicorn
pip install gunicorn
gunicorn main:app
```

### Environment Variables for Production
- Set all API keys in production environment
- Configure CORS for your domain
- Enable HTTPS for secure connections

## 🐛 Troubleshooting

### Common Issues
1. **CORS Errors** - Ensure backend allows frontend origin
2. **API Key Errors** - Verify API keys are correctly set
3. **Camera Permission** - Enable camera access in browser
4. **Microphone Issues** - Check browser microphone permissions
5. **PDF Upload Fails** - Ensure file is under 10MB and valid PDF

### Development Tips
- Use browser dev tools to inspect API calls
- Check console for JavaScript errors
- Verify backend logs for API issues
- Test with different browsers for compatibility

## 📈 Performance Optimization

### Frontend
- Lazy loading for heavy components
- Image optimization and compression
- Code splitting for better load times
- Service worker for offline support

### Backend
- Async processing for AI operations
- Caching for frequently accessed data
- Database query optimization
- Rate limiting for API protection

## 🔒 Security Considerations

- Sanitize all user inputs
- Validate file uploads
- Implement rate limiting
- Use HTTPS in production
- Secure API key management
- User authentication and authorization

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation
3. Test with mock data first
4. Enable debug mode for detailed logs

---

**🎉 Congratulations! Your HireReady AI platform is ready to use!**

The application provides a complete AI-powered interview preparation system with premium UI and comprehensive features. Users can upload resumes, practice interviews with voice and camera, receive instant AI feedback, and track their progress over time.
