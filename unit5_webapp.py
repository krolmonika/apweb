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


class DatabaseLoader:
    def __init__(self):
        self.queryResponse = db.session.query(Formdata).all()
        self.dbData = {'played_as_child' : [],
                       'games' : [],
                       'plays_now' : [],
                       'type' : [],
                       'sex' : [],
                       'age' : []}

    def loadAsDictionary(self):
        for databaseRecord in self.queryResponse:
            self.dbData['played_as_child'].append(databaseRecord.iff)
            self.dbData['games'].append(databaseRecord.which)
            self.dbData['plays_now'].append(databaseRecord.if_now)
            self.dbData['type'].append(databaseRecord.type)
            self.dbData['sex'].append(databaseRecord.q1)
            self.dbData['age'].append(databaseRecord.q2)
        return self.dbData


class ResultsDisplayer:
    def __init__(self):
        databaseLoader = DatabaseLoader()
        self.dbData = databaseLoader.loadAsDictionary()
        self.chartData = {}

    def getAmount(self, column, value=None):
        if value is None:
            return len(self.dbData[column])
        else:
            print(value)
            return self.dbData[column].count(value)

    def prepareBarChart(self):
        playedAsChild = self.getAmount('played_as_child', 'Tak')
        playedSpecificGame = self.getAmount('games', 'Chińczyk')
        self.chartData['barChart'] = [['Czy grałeś', playedAsChild], ['W co', playedSpecificGame]]

    def prepareCharts(self):
        self.prepareBarChart()
        return self.chartData


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
    resultsDisplayer = ResultsDisplayer()
    return render_template('result.html', data=resultsDisplayer.prepareCharts())

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