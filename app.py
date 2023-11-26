from flask import Flask, redirect, url_for, render_template, request

app = Flask(__name__)


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
    def __init__(self, email, contact, address, org_type, company):
        self.cid = str(uuid.uuid4())
        self.email = email
        self.contact = contact
        self.org_type = org_type
        self.company = company

    def to_dict(self):
        return {
            '_id': ObjectId(),
            'cid': self.cid,
            'email': self.email,
            'contact': self.contact,
            'address': self.address,
            'org_type': self.org_type,
            'company': self.company
        }

@app.route("/forms", methods=['POST'])
def reservation_post():
    try:
        reserv_collection = db['reservation']

        startdate = request.form.get('start-date')
        enddate = request.form.get('end-date')

        existing_booking = reserv_collection.find_one({
            'startdate': {'$lte': enddate},
            'enddate': {'$gte': startdate}
        })

        if existing_booking:
            return "Error: There is already a booking in the specified date range."

        org_name = request.form.get('org_name')
        starttime = request.form.get('start-time')
        endtime = request.form.get('end-time')
        venue = request.form.get('room_number')
        purpose = request.form.get('purpose')
        description = request.form.get('description')

        booking = Booking(org_name, startdate, enddate, starttime, endtime, venue, purpose, description)
        reserv_collection.insert_one(booking.to_dict())

        cust_collection = db['customer']
        
        email = request.form.get('org_email')
        contact = request.form.get('org_phone')
        address = request.form.get('org_address')
        org_type = request.form.get('org_type') 
        company = request.form.get('org_company')

        customer = Customer(email, contact, address, org_type, company)
        cust_collection.insert_one(customer.to_dict())

        return redirect(url_for('booking'))
    except Exception as e:
        return f"An error occurred: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True)