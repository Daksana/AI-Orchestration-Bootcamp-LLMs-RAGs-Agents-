# CV-Job Description Matcher

An AI-powered recruitment tool developed during the AI Orchestration Bootcamp by **Senzmate IoT Intelligence**. Uses Google Gemini AI to automatically match resumes with job descriptions and generate compatibility scores.

## Features

- **PDF Processing**: Extracts structured data from resume PDFs
- **Intelligent Scoring**: Weighted algorithm (Skills: 70%, Education: 20%, Experience: 10%)
- **Score**: Generates score charts and detailed reasoning

## Getting Started

1. **Install dependencies:**
```bash
pip install google-generativeai python-dotenv matplotlib
```

2. **Set up API key:**
Create `.env` file with: `GOOGLE_API_KEY=your_key_here`

3. **Run:**
```bash
python cv_jd_matcher.py
```

## How It Works

1. Extracts structured data from PDF resumes using Google Gemini AI
2. Processes job descriptions to identify requirements
3. Calculates compatibility scores with weighted criteria
4. Generates JSON outputs, scores and reasoning


*Project developed under AI Orchestration Bootcamp by Senzmate IoT Intelligence*
