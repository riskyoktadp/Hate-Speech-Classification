import sqlite3
import pandas as pd
from flask import Flask, request, jsonify, make_response
from flask_swagger_ui import get_swaggerui_blueprint

# Init app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False  #Agar Return JSON dalam urutan yang benar

# Database
db = sqlite3.connect('binar_challenge.db', check_same_thread=False) 
db.row_factory = sqlite3.Row
mycursor = db.cursor()

# flask swagger configs
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Tworst!"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


# Homepage
@app.route('/', methods=['GET'])
def get():
    return "Welcome to Tworst!"


# Tweet
@app.route("/tweet", methods=["GET","POST"])
def tweet():
    if request.method == "POST":
        input_text = str(request.form["text"])
        output_text = process_text(input_text)

        query_text = "insert into tweet (Tweet ,tweet_ready) values (?, ?)"
        val = (input_text, output_text)
        mycursor.execute(query_text, val)
        db.commit()
        print(input_text)
        print(output_text)
        
        return "Success Input Data"


    elif request.method == "GET":        
        query_text = "select * from tweet"
        select_tweet = mycursor.execute(query_text)
        tweet = [
            dict(tweet_id=row[0],  Tweet=row[1], tweet_ready=row[2])
            for row in select_tweet.fetchall()
        ]
        return jsonify(tweet)




@app.route("/tweet/<string:tweet_id>", methods=["GET","PUT","DELETE"])
def tweet_id(tweet_id):
    if request.method == "GET":   
        
        query_text = "select * from tweet where Tweet = ?"
        val = str(tweet_id)
        select_tweet = mycursor.execute(query_text, [val])
        tweet = [
            dict(tweet_id=row[0], Tweet=row[1], tweet_ready=row[2])
            for row in select_tweet.fetchall()
        ]
        print(tweet)
        return jsonify(tweet)


    elif request.method == "DELETE":

        query_text = "delete from tweet where tweet_id = ?"
        val = tweet_id
        mycursor.execute(query_text, [val])
        db.commit()
        return "Success Delete Data"

    elif request.method == "PUT":
        
        input_text = str(request.form["text"])
        output_text = process_text(input_text)
        query_text = "update tweet set Tweet = ?, tweet_ready = ? where tweet_id = ?"
        val = (input_text, output_text, tweet)
        mycursor.execute(query_text, val)
        db.commit()
        
        return "Success Update Data"



# Upload CSV File
@app.route("/tweet/csv", methods=["POST"])
def tweet_csv():
    if request.method == 'POST':
        file = request.files['file']
        
        
        try:
            data = pd.read_csv(file, encoding='iso-8859-1')
        except:
            data = pd.read_csv(file, encoding='utf-8') 
        process_csv(data)
        return "DONE"


# error handling
@app.errorhandler(400)
def handle_400_error(_error):
    "Return a http 400 error to client"
    return make_response(jsonify({'error': 'Misunderstood'}), 400)


@app.errorhandler(401)
def handle_401_error(_error):
    "Return a http 401 error to client"
    return make_response(jsonify({'error': 'Unauthorised'}), 401)


@app.errorhandler(404)
def handle_404_error(_error):
    "Return a http 404 error to client"
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(500)
def handle_500_error(_error):
    "Return a http 500 error to client"
    return make_response(jsonify({'error': 'Server error'}), 500)


#Run Server
if __name__ == '__main__':
    app.run(debug=True)
