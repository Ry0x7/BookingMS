from flask import Flask, redirect, request, url_for, render_template
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

client = MongoClient(os.getenv('MONGODB_SRV'))
db = client['booking']
collection = db['bookingms'] 

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/booking")
def booking():
    return render_template('booking.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/forms/conference")
def conf():
    return render_template('/forms/conferenceforms.html')

@app.route("/forms/avr")
def avr():
    return render_template('/forms/avrforms.html')

@app.route("/forms/littletheater")
def ltheater():
    return render_template('/forms/ltforms.html')

class Booking:
    def __init__(self, name, email, contact, startdate, enddate, starttime, endtime, venue, purpose):
        self.name = name
        self.email = email
        self.contact = contact
        self.startdate = startdate
        self.enddate = enddate
        self.starttime = starttime
        self.endtime = endtime
        self.venue = venue
        self.purpose = purpose

@app.route("/forms", methods=['POST'])
def booking_post():
    name = request.form.get('name')
    email = request.form.get('email')
    contact = request.form.get('contact')
    startdate = request.form.get('startdate')
    enddate = request.form.get('enddate')
    starttime = request.form.get('starttime')
    endtime = request.form.get('endtime')
    venue = request.form.get('venue')
    purpose = request.form.get('purpose')

    booking = Booking(name, email, contact, startdate, enddate, starttime, endtime, venue, purpose)
    collection.insert_one(booking.__dict__)

    return redirect(url_for('booking'))

if __name__ == "__main__":
    app.run(debug=True)