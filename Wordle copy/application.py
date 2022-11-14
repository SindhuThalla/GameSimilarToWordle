from flask import Flask, render_template,request,redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import datetime as dt
import random
from sqlalchemy import select, func, Integer, Table, Column, MetaData
global id , win
app = Flask(__name__)
limiter = Limiter(app, key_func=get_remote_address)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///todo.db'

db = SQLAlchemy(app)


#Table to store Game data
class Game(db.Model):
    id= db.Column(db.Integer, primary_key=True, autoincrement=True)
    guess = db.Column(db.String(10))
    win= db.Column(db.Boolean)
    day = db.Column(db.String(20))


    def __repr__(self):
        return f"{self.guess}"


@app.before_first_request
def create_tables():
    db.create_all()

#Endpoint to enter the user guess

@app.route('/', methods=["GET","POST"])
@limiter.limit("6/day")
def index():
    if request.method == 'POST':
        guess = request.form['guess']
        return redirect(url_for("predict", user_guess=guess))   
         
    return render_template("index.html")
    
@app.errorhandler(429)
def ratelimit_handler(e):
  return "You run out of lives."

#Endpoint to computing the user guess is correct or not and storing the user guess to Game table 
@app.route('/<user_guess>', methods=["POST", "GET"])
@limiter.limit("6/day")
def predict(user_guess):
    
    word=['share','shirt', 'earth', 'chart','curve','crowd']
    secret_word = random.choice(word)
    guessed_word_correctly = False
   
    
    if user_guess == secret_word:
        guessed_word_correctly = True
        day = dt.date.today().strftime('%Y-%m-%d')
        game = Game(guess=user_guess,win=guessed_word_correctly, day=day)    
        db.create_all()
        db.session.add(game)
        db.session.commit()
        return 'You guessed the correct word! You win ' 
        
    else:
        day = dt.date.today().strftime('%Y-%m-%d')
        game = Game(guess=user_guess,win=guessed_word_correctly, day=day)    
        db.create_all()
        db.session.add(game)
        db.session.commit()
        return "Sorry, you lost. Try again"

#Endpoint to view entire Game results
@app.route('/result', methods=["GET"])
def result1():
   output=[]
   games= Game.query.order_by(Game.id.desc()).all()
   for game in games:
    game_data = {'guess':game.guess, "win":game.win, "day":game.day}
    output.append(game_data)

   return {"games": output}   
    
    
    
#Endpoint to view the summary of user guesses
  
@app.route('/result/<day>', methods=["GET"])
def result(day):
   output=[]
   games= Game.query.filter(Game.day== day).all()
   for game in games:
    game_data = {'guess':game.guess, "win":game.win, "day":game.day}
    output.append(game_data)

    if True in output:
        return "Win"
    else:
       return "Lost"
    
#Endpoint to get the count of user guesses of a particular date
@app.route('/resultcount/<day>', methods=["GET"])
def resultcount(day):
   output=[]
   games= Game.query.filter(Game.day== day).all()
   for game in games:
    game_data = {'guess':game.guess, "win":game.win, "day":game.day}
    output.append(game_data)

   return {"count": len(output)}
    
if __name__== '__main__':
    app.run(debug=True)
   

