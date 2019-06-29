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


class DataSplitter:
    @staticmethod
    def splitByAge(dbData, age, columns=['played_as_child', 'games', 'plays_now', 'type', 'sex', 'age']):
        # Due to database structure age argument must be integer from 1 to 5
        ageSegmentData = {'played_as_child': [],
                          'games': [],
                          'plays_now': [],
                          'type': [],
                          'sex': [],
                          'age': []}
        for index in range(len(dbData['age'])):
            if dbData['age'][index] == age:
                for column in columns:
                    ageSegmentData[column].append(dbData[column][index])

        return ageSegmentData

    @staticmethod
    def splitBySex(dbData, columns=['played_as_child', 'games', 'plays_now', 'type', 'sex', 'age']):
        menData = {'played_as_child' : [],
                   'games' : [],
                   'plays_now' : [],
                   'type' : [],
                   'sex' : [],
                   'age' : []}
        womenData = {'played_as_child': [],
                     'games': [],
                     'plays_now': [],
                     'type': [],
                     'sex': [],
                     'age': []}
        for index in range(len(dbData['sex'])):
            if dbData['sex'][index] == 1:
                for column in columns:
                    menData[column].append(dbData[column][index])
            else:
                for column in columns:
                    womenData[column].append(dbData[column][index])

        return menData, womenData


class ResultsDisplayer:
    def __init__(self):
        databaseLoader = DatabaseLoader()
        self.dbData = databaseLoader.loadAsDictionary()
        self.chartData = {}

    @staticmethod
    def getAgeSegmentName(value):
        converter = {1: 'do 18',
                     2: '19-25',
                     3: '26-45',
                     4: '46-55',
                     5: '55+'}
        return converter[value]

    def getAmount(self, column, value=None, data=None):
        if data is None:
            data = self.dbData
        if value is None:
            return len(data[column])
        else:
            return data[column].count(value)

    def prepareGamingHabitsOverTimeChart(self):
        gamingHabits = [['Nadal gra', 0],
                        ['Zaczęło grać', 0],
                        ['Przestało grać', 0],
                        ['Nadal nie gra', 0]]
        for index in range(len(self.dbData['played_as_child'])):
            if self.dbData['played_as_child'][index] == 'Tak':
                if self.dbData['plays_now'][index] == 'Tak':
                    gamingHabits[0][1] += 1
                else:
                    gamingHabits[2][1] += 1
            else:
                if self.dbData['plays_now'][index] == 'Tak':
                    gamingHabits[1][1] += 1
                else:
                    gamingHabits[3][1] += 1
        self.chartData['gamingHabits'] = gamingHabits

    def prepareGamingHabitsOverTimeMenChart(self):
        gamingHabits = [['Nadal gra', 0],
                        ['Zaczęło grać', 0],
                        ['Przestało grać', 0],
                        ['Nadal nie gra', 0]]
        menData, _ = DataSplitter.splitBySex(self.dbData, ['played_as_child', 'plays_now'])
        for index in range(len(menData['played_as_child'])):
            if menData['played_as_child'][index] == 'Tak':
                if menData['plays_now'][index] == 'Tak':
                    gamingHabits[0][1] += 1
                else:
                    gamingHabits[2][1] += 1
            else:
                if menData['plays_now'][index] == 'Tak':
                    gamingHabits[1][1] += 1
                else:
                    gamingHabits[3][1] += 1
        self.chartData['gamingHabitsMen'] = gamingHabits

    def prepareGamingHabitsOverTimeWomenChart(self):
        gamingHabits = [['Nadal gra', 0],
                        ['Zaczęło grać', 0],
                        ['Przestało grać', 0],
                        ['Nadal nie gra', 0]]
        _, womenData = DataSplitter.splitBySex(self.dbData, ['played_as_child', 'plays_now'])
        for index in range(len(womenData['played_as_child'])):
            if womenData['played_as_child'][index] == 'Tak':
                if womenData['plays_now'][index] == 'Tak':
                    gamingHabits[0][1] += 1
                else:
                    gamingHabits[2][1] += 1
            else:
                if womenData['plays_now'][index] == 'Tak':
                    gamingHabits[1][1] += 1
                else:
                    gamingHabits[3][1] += 1
        self.chartData['gamingHabitsWomen'] = gamingHabits

    def prepareMostPopularGamesChart(self):
        mostPopularGames = []
        for game in set(self.dbData['games']):
            mostPopularGames.append([game, self.getAmount('games', game)])
        self.chartData['mostPopularGames'] = mostPopularGames

    def prepareMostPopularGamesMenChart(self):
        menData, _ = DataSplitter.splitBySex(self.dbData, ['games'])
        mostPopularGames = []
        for game in set(menData['games']):
            mostPopularGames.append([game, self.getAmount('games', game, menData)])
        self.chartData['mostPopularGamesMen'] = mostPopularGames

    def prepareMostPopularGamesWomenChart(self):
        _, womenData = DataSplitter.splitBySex(self.dbData, ['games'])
        mostPopularGames = []
        for game in set(womenData['games']):
            mostPopularGames.append([game, self.getAmount('games', game, womenData)])
        self.chartData['mostPopularGamesWomen'] = mostPopularGames

    def prepareMostPopularTypesChart(self):
        mostPopularTypes = []
        for type in set(self.dbData['type']):
            mostPopularTypes.append([type, self.getAmount('type', type)])
        self.chartData['mostPopularTypes'] = mostPopularTypes

    def prepareMostPopularTypesMenChart(self):
        menData, _ = DataSplitter.splitBySex(self.dbData, ['type'])
        mostPopularTypes = []
        for type in set(menData['type']):
            mostPopularTypes.append([type, self.getAmount('type', type, menData)])
        self.chartData['mostPopularTypesMen'] = mostPopularTypes

    def prepareMostPopularTypesWomenChart(self):
        _, womenData = DataSplitter.splitBySex(self.dbData, ['type'])
        mostPopularTypes = []
        for type in set(womenData['type']):
            mostPopularTypes.append([type, self.getAmount('type', type, womenData)])
        self.chartData['mostPopularTypesWomen'] = mostPopularTypes

    def prepareWhoPlayedChart(self):
        playedAsChild = self.getAmount('played_as_child', 'Tak')
        notPlayedAsChild = self.getAmount('played_as_child', 'Nie')
        self.chartData['whoPlayed'] = [['Grali', playedAsChild], ['Nie grali', notPlayedAsChild]]

    def prepareWhoPlayedAgeChart(self):
        whoPlayedAge = []
        divide = lambda a, b: a / b if b != 0 else 0
        for age in [1, 2, 3, 4, 5]:
            ageSegmentData = DataSplitter.splitByAge(self.dbData, age, ['played_as_child'])
            whoPlayedAge.append([ResultsDisplayer.getAgeSegmentName(age),
                                100 * divide(self.getAmount('played_as_child', 'Tak', ageSegmentData),
                                             self.getAmount('played_as_child', data=ageSegmentData))])
        self.chartData['whoPlayedAge'] = whoPlayedAge


    def prepareWhoPlayedMenChart(self):
        menData, _ = DataSplitter.splitBySex(self.dbData, ['played_as_child'])
        playedAsChild = self.getAmount('played_as_child', 'Tak', menData)
        notPlayedAsChild = self.getAmount('played_as_child', 'Nie', menData)
        self.chartData['whoPlayedMen'] = [['Grali', playedAsChild], ['Nie grali', notPlayedAsChild]]

    def prepareWhoPlayedWomenChart(self):
        _, womenData = DataSplitter.splitBySex(self.dbData, ['played_as_child'])
        playedAsChild = self.getAmount('played_as_child', 'Tak', womenData)
        notPlayedAsChild = self.getAmount('played_as_child', 'Nie', womenData)
        self.chartData['whoPlayedWomen'] = [['Grały', playedAsChild], ['Nie grały', notPlayedAsChild]]

    def prepareWhoPlaysChart(self):
        playNow = self.getAmount('plays_now', 'Tak')
        notPlayNow = self.getAmount('plays_now', 'Nie')
        self.chartData['whoPlays'] = [['Grają', playNow], ['Nie grają', notPlayNow]]

    def prepareWhoPlaysAgeChart(self):
        whoPlaysAge = []
        divide = lambda a, b: a / b if b != 0 else 0
        for age in [1, 2, 3, 4, 5]:
            ageSegmentData = DataSplitter.splitByAge(self.dbData, age, ['plays_now'])
            whoPlaysAge.append([ResultsDisplayer.getAgeSegmentName(age),
                                100 * divide(self.getAmount('plays_now', 'Tak', ageSegmentData),
                                             self.getAmount('plays_now', data=ageSegmentData))])
        self.chartData['whoPlaysAge'] = whoPlaysAge

    def prepareWhoPlaysMenChart(self):
        menData, _ = DataSplitter.splitBySex(self.dbData, ['plays_now'])
        playNow = self.getAmount('plays_now', 'Tak', menData)
        notPlayNow = self.getAmount('plays_now', 'Nie', menData)
        self.chartData['whoPlaysMen'] = [['Grają', playNow], ['Nie grają', notPlayNow]]

    def prepareWhoPlaysWomenChart(self):
        _, womenData = DataSplitter.splitBySex(self.dbData, ['plays_now'])
        playNow = self.getAmount('plays_now', 'Tak', womenData)
        notPlayNow = self.getAmount('plays_now', 'Nie', womenData)
        self.chartData['whoPlaysWomen'] = [['Grają', playNow], ['Nie grają', notPlayNow]]

    def prepareCharts(self):
        self.prepareWhoPlayedChart()
        self.prepareWhoPlayedWomenChart()
        self.prepareWhoPlayedMenChart()
        self.prepareMostPopularGamesChart()
        self.prepareMostPopularGamesWomenChart()
        self.prepareMostPopularGamesMenChart()
        self.prepareMostPopularTypesChart()
        self.prepareMostPopularTypesWomenChart()
        self.prepareMostPopularTypesMenChart()
        self.prepareWhoPlaysChart()
        self.prepareWhoPlaysAgeChart()
        self.prepareWhoPlaysWomenChart()
        self.prepareWhoPlaysMenChart()
        self.prepareGamingHabitsOverTimeChart()
        self.prepareGamingHabitsOverTimeWomenChart()
        self.prepareGamingHabitsOverTimeMenChart()
        self.prepareWhoPlayedAgeChart()
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