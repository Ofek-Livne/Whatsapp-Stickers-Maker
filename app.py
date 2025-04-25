from os import makedirs
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename

from constants import *
from sticker_pack_maker import make_sticker_pack

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif'}  # TODO check gif

app.config['UPLOAD_FOLDER'] = UPLOAD_DIR_NAME


def allowed_file(filename) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_images():
    message = ""
    uploaded_files = []
    makedirs(UPLOAD_DIR_NAME, exist_ok=True)  # TODO if I dont delete the dir so move it from here

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
            if file:
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = upload_dir_path / filename
                    file.save(filepath)
                    uploaded_files.append(url_for('uploaded_file', filename=filename))
                else:
                    message += (f'Invalid file type for {file.filename}.'
                                f' Allowed types are: {", ".join(ALLOWED_EXTENSIONS)}<br>')
        print(pack_name, author_name, include_tray, uploaded_files)  # TODO delete
        if not message:
            if uploaded_files:
                make_sticker_pack(pack_name, author_name, include_tray)
                message = 'Images uploaded successfully!'
            else:
                message = 'No files were selected.'
    return get_return_type(message, uploaded_files)


def get_return_type(message, uploaded_files):
    return render_template('index.html', message=message, uploaded_files=uploaded_files,
                           max_size=MAX_FILE_COUNT)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# @app.route('/create_sticker_pack', methods=['POST'])
# def create_sticker_pack():
#     print('creating')
#     return render_template('index.html', message=message, uploaded_files=uploaded_files)
