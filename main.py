import logging
import logging
from logging import StreamHandler
from flask import Flask, redirect, request, render_template, jsonify
import pandas as pd
import psycopg2
import random
import tweets_roberta
from tweetDataModel import DataModel
import json

host = 'localhost'
port = '5432'
dbname = 'postgres'
user = 'postgres'
password = 'password'

conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)

# pip install gensim
#load the word2vec embeddings
# from gensim import downloader as api #can load a saved model also
# preTW2v_wv = api.load('word2vec-google-news-300')

from gensim.models import KeyedVectors
# Load the saved model from disk
preTW2v_wv = KeyedVectors.load('preTW2v_wv.model')

app = Flask(__name__)
app.logger.addHandler(StreamHandler())
app.logger.setLevel(logging.INFO)

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username == 'admin' and password == 'password':
        return redirect('/results')
    else:
        return 'Invalid login'

@app.route('/results')
def results_page():
    
    return render_template('results.html')

@app.route('/results', methods=['POST'])
def results():
    keywords = request.form['keywords']
    negative_keywords = request.form['neg_keywords']
    # print(keywords)
    # Generate similar keywords
    similar_keywords = get_similar_keywords(keywords, negative_keywords)
    # Save keywords to db
    initial_keywords = [value.strip() for value in keywords.split(',')]
    
    temp_final_keywords = list(set(similar_keywords) - set(initial_keywords))
    
    final_keywords = initial_keywords + temp_final_keywords
    # final_keywords = list(set(final_keywords))
    negative_keywords = [value.strip() for value in negative_keywords.split(',')]

    final_audience = [
    {"name": "Audience 1",
        "twitter_handle": "@Audience1",
        "instagram_handle": "@Audience1",
        "facebook_page": "Audience1"},
    {"name": "Audience 2",
        "twitter_handle": "@Audience2",
        "instagram_handle": "@Audience2",
        "facebook_page": "Audience2"}]
    # Return results in tabular format
    return render_template('results.html', final_keywords=final_keywords, audiences=final_audience, 
                           negative_keywords=negative_keywords, initial_keywords=initial_keywords)


@app.route('/finalize_keywords', methods=['POST'])
def finalize_keywords():
    print("------------------------------->>>>>>>>>>>", request.get_json())
    finalized_keywords = request.get_json().get('finalized_keywords')    
    #save to db
    cur = conn.cursor()
    # Generate a random ID
    id = random.randint(1, 1000)
    # Define the data to be inserted as a list of tuples
    data = [(id, finalized_keywords)]
    # Use an SQL INSERT statement to add the data to the database
    sql = "INSERT INTO keywords (id, keywords) VALUES (%s, %s)"

    #PLEASE UNCOMMENT BELOW LINE ONCE  DATABSE IS INTEGERATED
    # cur.executemany(sql, data)

    print(data)
    # Commit the changes to the database
    conn.commit()
    # Close the cursor
    cur.close()
    # conn.close()
    print(">>>>>>>>finalizeKeywords::",finalized_keywords,"::type is::")
    print(type(finalized_keywords))
    result=get_social(finalized_keywords)
    # data_model=[]
    # for key, value in result.items():
    #     data_model.append(DataModel(key, value[0], value[1]))

    data_dict = []
    for key, value in result.items():
        model_dict = {
            'username': key,
            'text': value[0],
            'roberta_score': value[1]
        }
        data_dict.append(model_dict)

    return jsonify(data=data_dict)

def save_audience(results): 
    # Save to the database
    cur = conn.cursor()
    # Define the data to be inserted as a list of tuples
    data = []
    for key, value in results.items():
        data.append((random.randint(1, 50000), key, value[0], value[1]))
    # Use an SQL INSERT statement to add the data to the database
    sql = "INSERT INTO tweets (id, username, text, roberta_score) VALUES (%s, %s, %s, %s)"

    
    #PLEASE UNCOMMENT BELOW LINE ONCE  DATABSE IS INTEGERATED
    # cur.executemany(sql, data)


    # Commit the changes to the database
    conn.commit()
    # Close the cursor
    cur.close()

def get_similar_keywords(keywords, neg_keywords):
    #Extract the data form previous query into structured data format of pandas dataframe
    
    keywords = [value.strip() for value in keywords.split(',')]
    neg_keywords = [value.strip() for value in neg_keywords.split(',')]

    # Remove any keywords that are not found in the KeyedVectors model
    keywords_found = [keyword for keyword in keywords if keyword in preTW2v_wv.key_to_index]
    neg_keywords_found = [keyword for keyword in neg_keywords if keyword in preTW2v_wv.key_to_index]


    #hanlde error when keywords are not in vocab
    similar_keywords_and_scores = preTW2v_wv.most_similar(positive=keywords_found,
                              negative=neg_keywords_found,topn=100)
    
    similar_keywords_df = pd.DataFrame.from_dict(similar_keywords_and_scores, orient='columns')
    similar_keywords_df.columns=['keywords', 'similarity_score']
    
    #convert the simialr keywords to a lsit
    similar_keywords = similar_keywords_df['keywords']
    # similar_keywords = similar_keywords.tolist()
    similar_keywords = [keyword.lower() for keyword in similar_keywords]
    similar_keywords = list(set(similar_keywords))



    return similar_keywords




def get_social(keywords):
    tweet_dict=tweets_roberta.get_users(keywords)
    return tweet_dict

def save_kw_to_db(keywords):()

def get_sentiment(keywords):()

if __name__ == '__main__':
    app.run(debug=True) #runs on port 5000 by default