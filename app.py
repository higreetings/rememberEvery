from flask import Flask, render_template, request, redirect, url_for
import os
import json
from werkzeug.utils import secure_filename
from datetime import datetime
import psycopg2


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

conn = psycopg2.connect("postgresql://remember_db_user:1k5tj5smiNjp7piVmQcR78hiO6no8Nbk@dpg-d0oe2g2li9vc7385rs6g-a.oregon-postgres.render.com/remember_db", sslmode='require')
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS records (
        id SERIAL PRIMARY KEY,
        text TEXT,
        remark TEXT,
        image_url TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
''')
conn.commit()

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


        cur.execute (
            "INSERT INTO records (text, remark, image_url) VALUES (%s, %s, %s)",
            (text, remark, image_url)
        )
        conn.commit ()

        return redirect(url_for('records'))

    return render_template('index.html')

@app.route('/records', methods=['GET'])
def records():
    cur.execute ("SELECT id, text, remark, image_url, date FROM records ORDER BY date DESC")
    data = cur.fetchall ()
    return render_template ('records.html', data=data)

@app.route('/delete/<int:index>', methods=['POST'])
def delete(index):
    # Get the image path for the record
    cur.execute("SELECT image_url FROM records WHERE id = %s", (index,))
    result = cur.fetchone()

    if result:
        image_path = result[0]
        # Delete the image file from the filesystem (if it exists)
        if image_path and os.path.exists(image_path):
            os.remove(image_path)

    # Delete the record from the PostgreSQL database
    cur.execute("DELETE FROM records WHERE id = %s", (index,))
    conn.commit()

    return redirect(url_for('records'))

if __name__ == '__main__':
    app.run(debug=True)
