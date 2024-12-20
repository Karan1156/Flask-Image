from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
import secrets
from PIL import Image

# Configuration
UPLOAD_FOLDER = os.path.join('uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = secrets.token_hex(16)

# Helpers
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process(filename, operation):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    new_path = filepath
    with Image.open(filepath) as img:
        if operation == 'cpng':
            new_path = filepath.rsplit('.', 1)[0] + '.png'
            img.save(new_path)
        elif operation == 'cgray':
            new_path = filepath.rsplit('.', 1)[0] + '_gray.png'
            img.convert('L').save(new_path)
        elif operation == 'cwebp':
            new_path = filepath.rsplit('.', 1)[0] + '.webp'
            img.save(new_path)
        elif operation == 'cjpg':
            new_path = filepath.rsplit('.', 1)[0] + '.jpg'
            img.save(new_path)
    return os.path.basename(new_path)

# Routes
@app.route("/")
def home():
    return render_template('index.html')

@app.route("/edit", methods=["POST"])
def edit():
    if request.method == "POST":
        if 'file' not in request.files:
            flash("No file part in the request")
            return redirect(url_for('home'))

        file = request.files.get('file')
        if file.filename == '':
            flash("No file selected")
            return redirect(url_for('home'))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            try:
                file.save(file_path)
                print(f"File saved successfully at {file_path}")
            except Exception as e:
                flash(f"Error saving file: {str(e)}")
                return redirect(url_for('home'))

            # Process the file if needed
            operation = request.form.get('operation')
            if operation:
                try:
                    processed_filename = process(filename, operation)
                    flash(f"File processed successfully. <a href='/download/{processed_filename}'>Download here</a>", "success")
                except Exception as e:
                    flash(f"Error processing file: {str(e)}")
            return redirect(url_for('home'))
        
        flash("Invalid file format")
        return redirect(url_for('home'))


@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
