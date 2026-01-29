from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["jobtracker"]
collection = db["jobs"]


@app.route('/')
def login():
    return render_template('login.html')


# Add Job
@app.route('/add', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        job = {
            "company": request.form['company'],
            "role": request.form['role'],
            "date": request.form['date'],
            "status": request.form['status']
        }
        collection.insert_one(job)
        return redirect('/jobs')

    return render_template('add_job.html')


# View Jobs
@app.route('/jobs')
def view_jobs():
    jobs = list(collection.find())
    return render_template('dashboard.html', jobs=jobs)


# Delete Job
@app.route('/delete/<job_id>')
def delete_job(job_id):
    collection.delete_one({"_id": ObjectId(job_id)})
    return redirect('/jobs')


# Update Job Status
@app.route('/update/<job_id>', methods=['POST'])
def update_job(job_id):
    new_status = request.form['status']
    collection.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"status": new_status}}
    )
    return redirect('/jobs')


if __name__ == '__main__':
    app.run(debug=True, port=5001)
