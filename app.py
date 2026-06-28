import os
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

import utils.resume_parser as resume_parser
import utils.analyzer as analyzer
import utils.db as db

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-1234-change-this-in-env')
# Keep everything in memory if possible, but Flask needs a temp dir for uploads if we save them
# We will process files directly from memory without saving to disk where possible.
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

# Initialize Database
db.init_db()

@app.context_processor
def inject_user():
    user_id = session.get('user_id')
    if user_id:
        user = db.get_user_by_id(user_id)
        return dict(current_user=user)
    return dict(current_user=None)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/build')
def build():
    return render_template('build_resume.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('user_id'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not name or not email or not password:
            return render_template('register.html', error='All fields are required.')
        if password != confirm_password:
            return render_template('register.html', error='Passwords do not match.')
            
        user_id = db.create_user(email, name, password)
        if not user_id:
            return render_template('register.html', error='Email address is already registered.')
            
        session['user_id'] = user_id
        return redirect(url_for('index'))
        
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            return render_template('login.html', error='Email and password are required.')
            
        user = db.verify_user(email, password)
        if not user:
            return render_template('login.html', error='Invalid email or password.')
            
        session['user_id'] = user['id']
        return redirect(url_for('index'))
        
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/history')
def history():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
        
    scans = db.get_user_scans(user_id)
    return render_template('history.html', scans=scans)

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if file:
        filename = secure_filename(file.filename)
        # Parse the file in-memory
        try:
            resume_text = resume_parser.extract_text(file)
            
            # Process and analyze
            analysis_result = analyzer.analyze_resume(resume_text)
            
            if analysis_result.get('is_resume') is False:
                return jsonify({'success': False, 'error': analysis_result.get('error', 'Invalid document.')})
            
            # Save to scan history if logged in
            user_id = session.get('user_id')
            if user_id:
                try:
                    db.save_scan(
                        user_id=user_id,
                        filename=filename,
                        ats_score=analysis_result.get('ats_score', 0),
                        recommended_title=analysis_result.get('recommended_job_title', 'Unknown'),
                        summary=analysis_result.get('summary', '')
                    )
                except Exception as db_err:
                    print(f"Error saving scan to history: {db_err}")
            
            return jsonify({
                'success': True,
                'analysis': analysis_result
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

@app.route('/build-resume', methods=['POST'])
def build_resume():
    data = request.json
    try:
        # Generate a better resume layout/content using AI
        generated_resume = analyzer.generate_resume(data)
        return jsonify({'success': True, 'resume_content': generated_resume})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download-docx', methods=['POST'])
def download_docx():
    data = request.json
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    try:
        import utils.docx_exporter as docx_exporter
        from io import BytesIO
        from flask import send_file
        
        doc = docx_exporter.create_resume_docx(data)
        
        file_stream = BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)
        
        name = data.get('name', 'Resume').strip()
        if not name:
            name = 'Resume'
        # Sanitize filename
        safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c in (' ', '_', '-')]).rstrip()
        safe_name = safe_name.replace(' ', '_')
        filename = f"{safe_name}_Resume.docx"
        
        return send_file(
            file_stream,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        print(f"Error generating DOCX: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
