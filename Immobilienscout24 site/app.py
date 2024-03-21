from flask import Flask, render_template, request, redirect, url_for, flash, session, g
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, EqualTo
import threading
import subprocess
import os
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')

class ScrapingForm(FlaskForm):
    start_scraping = SubmitField('Start Scraping')

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.username.data == 'admin' and form.password.data == 'admin':
            return redirect(url_for('scrape'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html', form=form)


@app.route('/scrape', methods=['GET', 'POST'])
def scrape():
    form = ScrapingForm()
    if form.validate_on_submit():
        city = request.form.get('city')
        subregion = request.form.get('subregion')
        apart_or_house = request.form.get('apart_or_house')
        words_to_check = request.form.get('words_to_check')  # Retrieve words to check input

        if city and apart_or_house:
            g.scraping_finished = False
            threading.Thread(target=run_scraper, args=(city, subregion, apart_or_house, words_to_check)).start() 
            flash('Scraping started!', 'success')
        else:
            flash('Please fill all required fields.', 'error')

    if g.get('scraping_finished', False):
        flash('Scraper has finished!', 'info')

    return render_template('scrape.html', form=form)


@app.route('/view-database')
def view_database():
    database_contents = get_database_contents()
    return render_template('view_database.html', database_contents=database_contents)


def run_scraper(city, subregion, apart_or_house, words_to_check):
    # Ask the user for input
    base_url = ""
    while True:
        if city != "":
            break
        else:
            flash("City name cannot be empty. Please enter a valid city name.", "error")
            return

    while True:
        if apart_or_house == "wohnung" or apart_or_house == 'haus':
            break
        elif apart_or_house == "":
            flash("This field cannot be empty. Please enter what are you buying.", "error")
        else:
            flash("Please enter either 'wohnung' or 'haus'.", "error")
            return

    if subregion:
        base_url = f"https://www.immobilienscout24.de/Suche/de/{city}/{city}/{subregion}/{apart_or_house}-kaufen"
    else:
        base_url = f"https://www.immobilienscout24.de/Suche/de/{city}/{city}/{apart_or_house}-kaufen"

    # Run the scraper script with the provided inputs and base_url
    subprocess.run(['python', 'scraper.py', city, subregion, apart_or_house, base_url, words_to_check])

    return redirect(url_for('scrape'))


def get_database_contents():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT * FROM houses''')
    database_contents = cursor.fetchall()
    conn.close()
    return database_contents



if __name__ == '__main__':
    app.run(debug=True)
