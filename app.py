from flask import Flask, redirect, url_for, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime

load_dotenv()
app = Flask(__name__)

client = MongoClient(os.getenv('MONGODB_SRV'))
db = client['booking']


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

@app.route('/report')
def report():

    weeklabels = [
        'Conference Room',
        'Little Theater',
        'Audio Visual Room',
    ]

    weekdata = [5, 4, 7]
    
    mlabels = [
        'Conference Room',
        'Little Theater',
        'Audio Visual Room',
    ]

    mdata = [30, 20, 45]

    return render_template(
        template_name_or_list='report.html',
        wdata=weekdata,
        wlabels=weeklabels,
        mdata=mdata,
        mlabels=mlabels
    )

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['email'] != 'admin@gmail.com' or request.form['password'] != 'admin123':
            error = 'Invalid Credentials. Please try again.'
        else:
            return render_template('loggedin.html')
    return render_template('login.html', error=error)

class Booking:
    def __init__(self, org_name, startdate, enddate, starttime, endtime, venue, purpose, description):
        self.booking_id = str(uuid.uuid4())
        self.org_name = org_name
        self.startdate = startdate
        self.enddate = enddate
        self.starttime = starttime
        self.endtime = endtime
        self.venue = venue
        self.purpose = purpose
        self.description = description

    def to_dict(self):
        return {
            '_id': ObjectId(),
            'booking_id': self.booking_id,
            'org_name': self.org_name,
            'startdate': self.startdate,
            'enddate': self.enddate,
            'starttime': self.starttime,
            'endtime': self.endtime,
            'venue': self.venue,
            'purpose': self.purpose,
            'description': self.description
        }

class Customer:
    def __init__(self, email, contact, org_type, company, payment_method):
        self.cid = str(uuid.uuid4())
        self.email = email
        self.contact = contact
        self.org_type = org_type
        self.company = company
        self.payment_method = payment_method

    def to_dict(self):
        return {
            '_id': ObjectId(),
            'cid': self.cid,
            'email': self.email,
            'contact': self.contact,
            'org_type': self.org_type,
            'company': self.company,
            'payment_method': self.payment_method
        }

@app.route("/forms/submit", methods=['POST'])
def reservation_post():
    try:
        reserv_collection = db['reservation']
        cust_collection = db['customer']

        startdate = request.form.get('start_date')
        enddate = request.form.get('end_date')
        org_name = request.form.get('org_name')
        starttime = request.form.get('start_time')
        endtime = request.form.get('end_time')
        venue = request.form.get('room_number')
        purpose = request.form.get('purpose')
        description = request.form.get('description')

        booking = Booking(org_name, startdate, enddate, starttime, endtime, venue, purpose, description)
        
        email = request.form.get('org_email')
        contact = request.form.get('org_phone')
        org_type = request.form.get('org_type') 
        company = request.form.get('org_name')
        payment_method = request.form.get('payment_method')

        customer = Customer(email, contact, org_type, company, payment_method)
        
        cust_collection.insert_one(customer.to_dict())
        reserv_collection.insert_one(booking.to_dict())

        return render_template('booking.html', success="Reservation successful!")
    except Exception as e:
        return render_template('booking.html', error=str(e))
    
@app.route("/check-time-conflicts", methods=['GET'])
def check_time_conflicts():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')

    conflicts = False

    reserv_collection = db['reservation']
    existing_reservation = reserv_collection.find_one({
        'startdate': start_date,
        'enddate': end_date,
        'starttime': start_time,
        'endtime': end_time
    })
    if existing_reservation:
        conflicts = True

    response = {
        'conflicts': conflicts
    }

    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)