from os import makedirs
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

from constants import *

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_COUNT = 30

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_images():
    message = ""
    uploaded_files = []
    makedirs(UPLOAD_FOLDER, exist_ok=True)  # TODO if I dont delete the dir so move it from here

    if request.method == 'POST':
        pack_name = request.form['pack_name']
        author_name = request.form['author_name']
        include_tray = 'add_tray_toggle' in request.form

        if 'files[]' not in request.files:
            message = 'No file part'
            return get_return_type(message, uploaded_files)

        files = request.files.getlist('files[]')
        if len(files) > MAX_FILE_COUNT - include_tray:
            message = f'You only can create a sticker pack with a maximum of {MAX_FILE_COUNT} images.'
            return get_return_type(message, uploaded_files)

        upload_dir_path = Path(app.config['UPLOAD_FOLDER'])
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = upload_dir_path / filename
                file.save(filepath)
                uploaded_files.append(url_for('uploaded_file', filename=filename))
            elif file and not allowed_file(file.filename):
                message += (f'Invalid file type for {file.filename}.'
                            f' Allowed types are: {", ".join(ALLOWED_EXTENSIONS)}<br>')
        print(pack_name, author_name, include_tray, uploaded_files)  # TODO delete
        if not message:
            message = 'Images uploaded successfully!' if uploaded_files else 'No files were selected.'
    return get_return_type(message, uploaded_files)


def get_return_type(message, uploaded_files):
    return render_template('index.html', message=message, uploaded_files=uploaded_files,
                           max_size=MAX_FILE_COUNT)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    app.run(debug=True)
