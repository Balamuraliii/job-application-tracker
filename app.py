import os
from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_bcrypt import Bcrypt
import datetime
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
app.secret_key = "secretkey"
bcrypt = Bcrypt(app)

client = MongoClient(os.environ.get("MONGO_URI"))


db = client["jobtracker"]

jobs_collection = db["jobs"]
users_collection = db["users"]


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = users_collection.find_one({"email": email})

        if user and bcrypt.check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            return redirect('/jobs')

        return "Wrong email or password"

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = bcrypt.generate_password_hash(
            request.form['password']).decode('utf-8')

        users_collection.insert_one({
            "email": email,
            "password": password
        })

        return redirect('/')

    return render_template('register.html')


@app.route('/add', methods=['GET', 'POST'])
def add_job():
    if 'user_id' not in session:
        return redirect('/')

    if request.method == 'POST':
        jobs_collection.insert_one({
            "user_id": ObjectId(session['user_id']),
            "company": request.form['company'],
            "role": request.form['role'],
            "techstack": request.form['techstack'],
            "date_applied": request.form['date_applied'],
            "status": request.form['status'],
            "notes": request.form['notes'],
            "created_at": datetime.datetime.now()
        })
        return redirect('/jobs')

    return render_template('add_job.html')


@app.route('/jobs')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')

    jobs = list(jobs_collection.find({
        "user_id": ObjectId(session['user_id'])
    }))

    return render_template('dashboard.html', jobs=jobs)


@app.route('/update/<job_id>', methods=['POST'])
def update_job(job_id):
    new_status = request.form['status']
    jobs_collection.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"status": new_status}}
    )
    return redirect('/jobs')


@app.route('/delete/<job_id>')
def delete_job(job_id):
    jobs_collection.delete_one({"_id": ObjectId(job_id)})
    return redirect('/jobs')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

