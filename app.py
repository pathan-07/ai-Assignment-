import os
import logging
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import base64
import cv2
import numpy as np
from werkzeug.security import generate_password_hash, check_password_hash
from utils.ocr import extract_text_from_image
from utils.analyzer import analyze_text, calculate_score

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Configure the SQLite database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///assignments.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models
    import models
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        if 'image_data' not in request.form:
            flash('No image captured. Please capture an image first.', 'danger')
            return redirect(url_for('analyze'))
        
        try:
            # Get image data from the form
            image_data = request.form['image_data']
            
            if not image_data:
                flash('No image data received. Please capture an image first.', 'danger')
                return redirect(url_for('analyze'))
                
            # Check if data URL prefix exists and handle accordingly
            if ',' in image_data:
                # Remove the data URL prefix
                image_data = image_data.split(',')[1]
            
            # Log for debugging
            logger.debug(f"Image data length: {len(image_data)}")
            
            # Decode base64 image
            try:
                image_bytes = base64.b64decode(image_data)
                if len(image_bytes) == 0:
                    flash('Received empty image. Please try again.', 'warning')
                    return redirect(url_for('analyze'))
                    
                # Log success
                logger.debug(f"Successfully decoded base64 data, length: {len(image_bytes)}")
                
                # Convert to numpy array
                nparr = np.frombuffer(image_bytes, np.uint8)
                
                # Decode image
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if image is None:
                    flash('Failed to decode image. Please try again with a different image.', 'warning')
                    return redirect(url_for('analyze'))
                
                # Log success
                logger.debug(f"Successfully decoded image, shape: {image.shape}")
                
            except Exception as e:
                logger.error(f"Error decoding image: {str(e)}")
                flash(f'Error decoding image: {str(e)}', 'danger')
                return redirect(url_for('analyze'))
            
            # Extract text using OCR
            extracted_text = extract_text_from_image(image)
            
            if not extracted_text:
                flash('Could not extract text from image. Please try again with a clearer image.', 'warning')
                return redirect(url_for('analyze'))
            
            # Store the extracted text in session
            session['extracted_text'] = extracted_text
            
            # Get reference text
            reference_texts = []
            reference_ids = []
            with app.app_context():
                references = models.ReferenceData.query.all()
                for ref in references:
                    reference_texts.append(ref.content)
                    reference_ids.append(ref.id)
            
            # If no reference data is available, redirect to add reference
            if not reference_texts:
                flash('No reference data available. Please add reference data first.', 'warning')
                return redirect(url_for('reference'))
            
            # Analyze the extracted text against all reference data
            best_score = 0
            best_ref_id = None
            best_analysis = None
            
            for i, ref_text in enumerate(reference_texts):
                analysis = analyze_text(extracted_text, ref_text)
                score = calculate_score(analysis)
                
                if score > best_score:
                    best_score = score
                    best_ref_id = reference_ids[i]
                    best_analysis = analysis
            
            # Store the analysis results in session
            session['analysis'] = best_analysis
            session['score'] = best_score
            session['reference_id'] = best_ref_id
            
            # Save the assignment result
            with app.app_context():
                assignment = models.Assignment(
                    content=extracted_text,
                    reference_id=best_ref_id,
                    score=best_score
                )
                db.session.add(assignment)
                db.session.commit()
                session['assignment_id'] = assignment.id
            
            return redirect(url_for('results'))
        
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            flash(f'Error analyzing image: {str(e)}', 'danger')
            return redirect(url_for('analyze'))
    
    return render_template('analyze.html')

@app.route('/reference', methods=['GET', 'POST'])
def reference():
    if request.method == 'POST':
        title = request.form.get('title', '')
        content = request.form.get('content', '')
        keywords = request.form.get('keywords', '')
        
        if not title or not content:
            flash('Title and content are required.', 'danger')
            return redirect(url_for('reference'))
        
        try:
            # Create new reference data
            with app.app_context():
                reference = models.ReferenceData(
                    title=title,
                    content=content,
                    keywords=keywords
                )
                db.session.add(reference)
                db.session.commit()
            
            flash('Reference data added successfully.', 'success')
            return redirect(url_for('reference'))
        
        except Exception as e:
            logger.error(f"Error adding reference data: {str(e)}")
            flash(f'Error adding reference data: {str(e)}', 'danger')
            return redirect(url_for('reference'))
    
    # Get all reference data
    references = []
    with app.app_context():
        references = models.ReferenceData.query.all()
    
    return render_template('reference.html', references=references)

@app.route('/delete_reference/<int:id>', methods=['POST'])
def delete_reference(id):
    try:
        with app.app_context():
            reference = models.ReferenceData.query.get(id)
            if reference:
                db.session.delete(reference)
                db.session.commit()
                flash('Reference data deleted successfully.', 'success')
            else:
                flash('Reference data not found.', 'danger')
    except Exception as e:
        logger.error(f"Error deleting reference data: {str(e)}")
        flash(f'Error deleting reference data: {str(e)}', 'danger')
    
    return redirect(url_for('reference'))

@app.route('/results')
def results():
    # Get data from session
    extracted_text = session.get('extracted_text', '')
    analysis = session.get('analysis', {})
    score = session.get('score', 0)
    reference_id = session.get('reference_id')
    assignment_id = session.get('assignment_id')
    
    reference = None
    if reference_id:
        with app.app_context():
            reference = models.ReferenceData.query.get(reference_id)
    
    return render_template('results.html', 
                           extracted_text=extracted_text, 
                           analysis=analysis, 
                           score=score, 
                           reference=reference,
                           assignment_id=assignment_id)

@app.route('/assignments')
def assignments():
    # Get all assignments
    with app.app_context():
        assignments = models.Assignment.query.order_by(models.Assignment.created_at.desc()).all()
    
    return render_template('assignments.html', assignments=assignments)

@app.route('/assignment/<int:id>')
def assignment_detail(id):
    with app.app_context():
        assignment = models.Assignment.query.get(id)
        if not assignment:
            flash('Assignment not found.', 'danger')
            return redirect(url_for('assignments'))
        
        reference = models.ReferenceData.query.get(assignment.reference_id)
        analysis = analyze_text(assignment.content, reference.content if reference else "")
    
    return render_template('assignment_detail.html', 
                           assignment=assignment, 
                           reference=reference, 
                           analysis=analysis)
