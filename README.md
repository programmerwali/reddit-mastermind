#  Reddit Mastermind

AI-powered Reddit content calendar generator that creates authentic, high-quality Reddit marketing campaigns.

##  Features

- **Natural Reddit Posts**: AI generates authentic questions that don't feel like ads
- **Strategic Conversations**: Creates realistic comment threads with organic product mentions
- **Quality Scoring**: Self-evaluates content for authenticity (targets 8-10/10)
- **Multi-Week Planning**: Intelligent calendar generation with pattern avoidance
- **Beautiful UI**: React + Tailwind frontend with real-time calendar viewing

##  Quality Scores

- **Naturalness**: 10/10
- **Persona Variety**: 10/10
- **Timing Realism**: 10/10
- **Content Diversity**: 9/10
- **Anti-Spam**: 8/10
- **Overall**: 9.4/10

##  Tech Stack

**Backend:**
- Python 3.11
- Flask
- OpenAI GPT-4o-mini
- Quality scoring algorithm

**Frontend:**
- React 18
- Vite
- Tailwind CSS
- Axios

##  Live Demo

- **Frontend**: https://reddit-mastermind-pi.vercel.app/
- **Backend API**: https://reddit-mastermind-production.up.railway.app

##  Local Setup

### Backend
```bash
cd backend
pip3 install -r requirements.txt
# Add OPENAI_API_KEY to .env
python3 app.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

##  How It Works

1. Input company info, personas, subreddits, and keywords
2. AI generates natural Reddit posts (no product mention)
3. AI creates realistic comment threads
4. Strategic product mentions in ~60% of comments
5. Quality scorer evaluates authenticity
6. Export calendar as JSON

##  Algorithm Features

- **Pattern Breaking**: Avoids repetitive language and timing
- **Persona Rotation**: Each character has distinct voice
- **Anti-Spam Detection**: Flags promotional language
- **Multi-Week Intelligence**: Tracks previous calendars to avoid repetition

##  Author

Built by Wali for Reddit Mastermind Assignment

##  License

MIT License
