from flask import Flask, redirect, url_for, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


load_dotenv()
app = Flask(__name__)

client = MongoClient(os.getenv('MONGODB_SRV'))
db = client['booking']
records = db.users



@app.route("/")
def home():
    return render_template('home.html')

@app.route("/booking")
def booking():
    return render_template('booking.html')

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/user/home")
def logged():
    return render_template('loggedin.html')

@app.route("/user/about")
def alogged():
    return render_template('aboutlogged.html')

@app.route("/admin/home")
def admin():
    return render_template('admin.html')

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

class Users:
    def __init__(self, email, password):
        self.booking_id = str(uuid.uuid4())
        self.email = email
        self.password = password
        
    def to_dict(self):
        return {
            '_id': ObjectId(),
            'email': self.email,
            'password': self.password
        }    

class Booking:
    def __init__(self, org_name, startdate, enddate, starttime, endtime, venue, purpose, description, status):
        self.booking_id = str(uuid.uuid4())
        self.org_name = org_name
        self.startdate = startdate
        self.enddate = enddate
        self.starttime = starttime
        self.endtime = endtime
        self.venue = venue
        self.purpose = purpose
        self.description = description
        self.status = status

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
            'description': self.description,
            'status': self.status
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
        status = "Pending"

        booking = Booking(org_name, startdate, enddate, starttime, endtime, venue, purpose, description, status)
        
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

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    message = ''
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_found = records.find_one({"email": email})
        if user_found:
            message = 'There already is a user with that name'
        else:
            user_input = {'email': email, 'password': generate_password_hash(password)}
            records.insert_one(user_input)
            return render_template('loggedin.html')
    return render_template('signup.html', message=message)

@app.route('/login', methods=['POST', 'GET'])
def login():
    message = ''
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user_found = records.find_one({"email": email})
        if user_found:
            if check_password_hash(user_found['password'], password):
                return render_template('loggedin.html')
            else:
                message = 'Wrong password'
        else:
            message = 'Username not found'
    return render_template('login.html', message=message)

def combine_collections():
    cust_collection = db['customer']
    reserv_collection = db['reservation']
    
    booked_data = []
    for customer in cust_collection.find():
        reservations = reserv_collection.find({'org_name': customer['company']})
        for reservation in reservations:
            specific_data = {
                'booking_id': reservation.get('booking_id'),
                'org_name': reservation.get('org_name'),
                'startdate': reservation.get('startdate'),
                'enddate': reservation.get('enddate'),
                'starttime': reservation.get('starttime'),
                'endtime': reservation.get('endtime'),
                'venue': reservation.get('venue'),
                'purpose': reservation.get('purpose'),
                'description': reservation.get('description'),
                'status': reservation.get('status')
            }
            booked_data.append(specific_data)

    return booked_data

@app.route('/booked', methods=['GET'])
def booked():
    try:
        if request.method == 'GET':
            data = combine_collections()
        return render_template('booked.html', data=data)
    except Exception as e:
        return str(e)
    
@app.route('/updateBooking', methods=['POST'])
def update_booking():
    try:
        reserv_collection = db['reservation']
        data = request.get_json()
        booking_id = data['booking_id']
        org_name = data['org_name']
        startdate = data['startdate']
        enddate = data['enddate']
        starttime = data['starttime']
        endtime = data['endtime']
        venue = data['venue']
        purpose = data['purpose']
        description = data['description']
        status = data['status']
        reserv_collection.update_one({'booking_id': booking_id}, {'$set': {
            'org_name': org_name,
            'startdate': startdate,
            'enddate': enddate,
            'starttime': starttime,
            'endtime': endtime,
            'venue': venue,
            'purpose': purpose,
            'description': description,
            'status': status
        }})
        return jsonify({'message': 'Booking updated successfully'}), 200
    except Exception as e:
        return str(e), 400
    
@app.route('/deleteBooking/<booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    try:
        reserv_collection = db['reservation']
        result = reserv_collection.delete_one({'booking_id': booking_id})
        if result.deleted_count == 0:
            return jsonify({'message': 'No booking found with that ID'}), 404
        else:
            return jsonify({'message': 'Booking deleted successfully'}), 200
    except Exception as e:
        return str(e), 400
if __name__ == "__main__":
    app.run(debug=True)