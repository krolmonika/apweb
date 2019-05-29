from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import statistics

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///formdata.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'True'

db = SQLAlchemy(app)

class Formdata(db.Model):
    __tablename__ = 'formdata'
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    firstname = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    iff = db.Column(db.String)
    which = db.Column(db.String)
    if_now = db.Column(db.String)
    type = db.Column(db.String)
    q1 = db.Column(db.Integer)
    q2 = db.Column(db.Integer)

    def __init__(self, firstname, email, iff, which, if_now, type, q1, q2):
        self.firstname = firstname
        self.email = email
        self.iff = iff
        self.which = which
        self.if_now = if_now
        self.type = type
        self.q1 = q1
        self.q2 = q2

db.create_all()


@app.route("/")
def welcome():
    return render_template('welcome.html')

@app.route("/form")
def show_form():
    return render_template('form.html')

@app.route("/raw")
def show_raw():
    fd = db.session.query(Formdata).all()
    return render_template('raw.html', formdata=fd)


@app.route("/result")
def show_result():
    fd_list = db.session.query(Formdata).all()

    # Some simple statistics for sample questions
    iff = []
    which = []
    if_now = []
    type = []
    q1 = []
    q2 = []
    for el in fd_list:
        iff.append(int(el.iff))
        which.append(el.which)
        if_now.append(el.if_now)
        type.append(el.type)
        q1.append((el.q1))
        q2.append((el.q2))

    if len(iff) > 0:
        # mean_satisfaction = statistics.mean(satisfaction)
        mean_iff = iff.count('Tak')
    else:
        mean_iff = 0

    # if len(q1) > 0:
    #     mean_q1 = statistics.mean(q1)
    # else:
    #     mean_q1 = 0
    #
    # if len(q2) > 0:
    #     mean_q2 = statistics.mean(q2)
    # else:
    #     mean_q2 = 0

    # Prepare data for google charts
    data = [['Czy grałeś', mean_iff]]

    return render_template('result.html', data=data)


@app.route("/save", methods=['POST'])
def save():
    # Get data from FORM
    firstname = request.form['firstname']
    email = request.form['email']
    iff = request.form['if']
    which = request.form['which']
    if_now = request.form['if_now']
    type = request.form['type']
    q1 = request.form['q1']
    q2 = request.form['q2']

    # Save the data
    fd = Formdata(firstname, email, iff, which, if_now, type, q1, q2)
    db.session.add(fd)
    db.session.commit()

    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)