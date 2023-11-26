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



if __name__ == "__main__":
    app.run(debug=True)