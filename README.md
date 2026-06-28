# AI Resume Analyzer & Builder

A Flask-based web application designed to help job seekers optimize their resumes using artificial intelligence. The application provides an interactive resume analyzer that calculates ATS compatibility scores, identifies strengths and weaknesses, rewrites summaries, and enables building/exporting professional resumes.

---

## 🌟 Core Features

- **ATS Analysis**: Upload resumes in PDF or Word (`.docx`) format to receive an instant ATS score.
- **Strengths & Weaknesses Feedback**: Automatically lists areas of strength and highlights fields that require improvement.
- **Smart Resume Builder**: Generate and refine professional resumes based on your extracted details using the Gemini AI model.
- **Export to DOCX**: Download generated resumes as professionally formatted Word documents.
- **Scan History**: Keep track of and review your previously analyzed resumes (requires registration/login).

---

## 🛠️ Technical Stack

- **Backend**: Flask 3.0.0, python-dotenv
- **Document Processing**: PyPDF2, python-docx
- **AI Engine**: Google Gemini API via `google-genai`
- **Database**: SQLite3 (stores user registrations and scan history)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9 or higher
- A Google Gemini API Key

### Installation

1. **Clone or Download the Project**:
   Ensure all files are placed in your working directory.

2. **Set up a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # On Windows: .\venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file in the root directory (or update the existing one) with:
   ```env
   FLASK_SECRET_KEY=your-flask-secret-key
   GEMINI_API_KEY=your-gemini-api-key
   ```

### Running the Application

1. Activate your virtual environment if not already activated:
   ```bash
   .\venv\Scripts\activate
   ```

2. Run the Flask application:
   ```bash
   python app.py
   ```

3. Open your browser and navigate to:
   [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
