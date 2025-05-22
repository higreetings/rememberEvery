from flask import Flask, render_template, request, redirect, url_for
import os
import json
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
DATA_FILE = 'data.json'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump([], f)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form.get('text')
        remark = request.form.get('remark')
        image = request.files.get('image')

        image_url = ''
        if image and image.filename:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        entry = {
            'text': text,
            'remark': remark,
            'image_url': image_url,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        with open(DATA_FILE, 'r+') as f:
            data = json.load(f)
            data.append(entry)
            f.seek(0)
            json.dump(data, f, indent=2)

        return redirect(url_for('records'))

    return render_template('index.html')

@app.route('/records', methods=['GET'])
def records():
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    return render_template('records.html', data=data)

@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    with open(DATA_FILE, 'r+') as f:
        data = json.load(f)
        if 0 <= index < len(data):
            image_url = data[index].get('image_url', '')
            if image_url and os.path.exists(image_url):
                os.remove(image_url)
            del data[index]
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=2)
    return redirect(url_for('records'))

if __name__ == '__main__':
    app.run(debug=True)
