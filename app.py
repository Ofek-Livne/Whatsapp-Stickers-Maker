from os import makedirs
from pathlib import Path
from shutil import rmtree

from flask import Flask, render_template, request, url_for, send_from_directory
from werkzeug.utils import secure_filename

from constants import *
from sticker_pack_maker import make_sticker_pack

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_DIR_NAME
app.config['DOWNLOAD_FOLDER'] = PACKS_DIR_NAME

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'jfif'}  # TODO check gif


def allowed_file(filename) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_images():
    message = ""
    uploaded_files = []
    upload_dir_path = Path(app.config['UPLOAD_FOLDER'])
    if upload_dir_path.exists():
        rmtree(UPLOAD_DIR_NAME)
    makedirs(UPLOAD_DIR_NAME, exist_ok=True)

    if request.method == 'POST':
        pack_name = request.form['pack_name']
        author_name = request.form['author_name']
        include_tray = 'add_tray_toggle' in request.form

        if tray := request.files.getlist('tray'):
            tray = tray[0]
            if allowed_file(tray.filename):
                tray_name = f'tray.{tray.filename.split(".")[-1]}'
                tray_path = upload_dir_path / tray_name
                tray.save(tray_path)
                uploaded_files.append(url_for('uploaded_file', filename=tray_name))

        if 'files[]' not in request.files:
            message = 'No file part'
            return get_return_type(message, uploaded_files)

        files = request.files.getlist('files[]')
        if len(files) > MAX_FILE_COUNT - include_tray:
            # TODO just make more packs
            message = f'You only can create a sticker pack with a maximum of {MAX_FILE_COUNT} images.'
            return get_return_type(message, uploaded_files)

        for file in files:
            if file:
                if allowed_file(file.filename):
                    if tray.filename == file.filename:
                        include_tray = True
                        continue
                    filename = secure_filename(file.filename)
                    filepath = upload_dir_path / filename
                    file.save(filepath)
                    uploaded_files.append(url_for('uploaded_file', filename=filename))
                else:
                    message += (f'Invalid file type for {file.filename}.'
                                f' Allowed types are: {", ".join(ALLOWED_EXTENSIONS)}<br>')
        if not message:
            if uploaded_files:
                pack_file_name = make_sticker_pack(pack_name, author_name, include_tray)
                message = 'Images uploaded successfully! Creating the pack!'
                return get_return_type(message, uploaded_files, pack_file_name)
            else:
                message = 'No files were selected.'
    return get_return_type(message, uploaded_files)


def get_return_type(message, uploaded_files, pack_file_name=None):
    return render_template('index.html', message=message, uploaded_files=uploaded_files,
                           max_size=MAX_FILE_COUNT, pack_file_name=pack_file_name)


@app.route(f'/{UPLOAD_DIR_NAME}/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route(f'/{PACKS_DIR_NAME}/<filename>')
def download_pack(filename):
    return send_from_directory(app.config['DOWNLOAD_FOLDER'], filename)
