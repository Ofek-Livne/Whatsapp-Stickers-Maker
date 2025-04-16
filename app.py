from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_COUNT = 30

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_images():
    message = ""
    uploaded_files = []

    if request.method == 'POST':
        pack_name = request.form['pack_name']
        author_name = request.form['author_name']
        add_tray_toggle = 'on' if 'add_tray_toggle' in request.form else 'off'

        if 'files[]' not in request.files:
            message = 'No file part'
            return render_template('index.html', message=message, uploaded_files=uploaded_files)

        files = request.files.getlist('files[]')
        if len(files) > MAX_FILE_COUNT:
            message = f'You can upload a maximum of {MAX_FILE_COUNT} images.'
            return render_template('index.html', message=message, uploaded_files=uploaded_files)

        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                uploaded_files.append(url_for('uploaded_file', filename=filename))
            elif file and not allowed_file(file.filename):
                message += (f'Invalid file type for {file.filename}.'
                            f' Allowed types are: {", ".join(ALLOWED_EXTENSIONS)}<br>')
        print(pack_name, author_name, add_tray_toggle, uploaded_files)
        if not message and uploaded_files:
            message = 'Images uploaded successfully!'
        elif not message:
            message = 'No files were selected.'
    return render_template('index.html', message=message, uploaded_files=uploaded_files)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
