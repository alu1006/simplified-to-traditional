from flask import Flask, render_template, request, send_file
import opencc
import os
import zipfile
import tempfile
import shutil
from docx2txt import process as docx2txt

app = Flask(__name__)

@app.route('/')
def index():
    #return render_template('index.html')
    return 'hello world'

@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('files[]')
    temp_dir = tempfile.mkdtemp()

    converted_files = []

    for file in files:
        filename, ext = os.path.splitext(file.filename)
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)

        if ext.lower() == '.docx':
            text = docx2txt(file_path)
            with open(os.path.join(temp_dir, filename + '.txt'), 'w') as txt_file:
                txt_file.write(text)

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as src:
            content = src.read()
            converter = opencc.OpenCC('s2t.json')
            traditional = converter.convert(content)
            converted_file_path = os.path.join(temp_dir, f"{filename}_convert{ext}")
            with open(converted_file_path, "w") as dest:
                dest.write(traditional)
            converted_files.append(converted_file_path)

    zip_file_path = os.path.join(temp_dir, 'converted_files.zip')
    with zipfile.ZipFile(zip_file_path, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for converted_file in converted_files:
            archive.write(converted_file, os.path.basename(converted_file))

    response = send_file(zip_file_path, as_attachment=True)
    shutil.rmtree(temp_dir)
    return response


# if __name__ == '__main__':
#     app.run(debug=True)
