# 👔 HireReady AI — Intelligent Mock Interview System

A premium AI-powered mock interview platform that simulates real human interviews using voice + camera interactions, dynamic AI questions, and intelligent behavioral tracking.

## 🚀 Features

- **Voice-based Interviews** - No typing required, just speak your answers
- **Camera Behavior Tracking** - Monitors eye contact, attention, and engagement
- **Dynamic AI Questions** - Personalized questions based on your resume and target role
- **Real-time Feedback** - Instant AI analysis of your responses
- **Premium UI/UX** - Glassmorphic dark theme with smooth animations

## 🛠️ Tech Stack

### Frontend
- React (Vite)
- Tailwind CSS
- Framer Motion
- react-webcam
- Recharts
- Firebase

### Backend
- FastAPI (Python)
- Gemini AI API
- MediaPipe Face Detection
- Web Speech API

## 📁 Project Structure

```
hireready-ai/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── api/
│   │   └── firebase/
│   ├── public/
│   └── package.json
├── backend/
│   ├── routes/
│   ├── services/
│   ├── models/
│   ├── utils/
│   └── main.py
└── README.md
```

## 🎯 Getting Started

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## 🔑 Environment Variables

Create `.env` files in both frontend and backend directories.

### Frontend .env
```
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

### Backend .env
```
GEMINI_API_KEY=your_gemini_api_key
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_PRIVATE_KEY=your_private_key
FIREBASE_CLIENT_EMAIL=your_client_email
```

## 🌟 Live Demo

Coming soon...

## 📄 License

MIT License
