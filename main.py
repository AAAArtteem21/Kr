import re
import sqlite3
import requests
from flask import Flask, request, render_template

app = Flask(__name__)

conn = sqlite3.connect('database.db')
cursor = conn.cursor()
cursor.execute('''create table if not exists pages
(id integer primary key autoincrement,
url text not null,
count integer not null default 0)''')
conn.commit()

def add_page(url):
cursor.execute('insert into pages(url) values (?)', (url,))
conn.commit()

def search_page(url, query):
response = requests.get(url)
if response.status_code == 200:
content = response.text
count = len(re.findall(query, content))
cursor.execute('update pages set count=? where url=?', (count, url))
conn.commit()

def get_results(query):
cursor.execute('select url, count from pages where url like ?', ('%' + query + '%',))
results = cursor.fetchall()
return sorted(results, key=lambda x: x[1], reverse=True)

@app.route('/')
def index():
return render_template('index.html')

@app.route('/add', methods=['POST'])
def add():
url = request.form['url']
add_page(url)
return 'OK'

@app.route('/search', methods=['POST'])
def search():
query = request.form['query']
cursor.execute('SELECT * from pages')
pages = cursor.fetchall()
for page in pages:
search_page(page[1], query)
results = get_results(query)
return render_template('results.html', results=results)

@app.route('/clear')
def clear():
cursor.execute('delete from pages')
conn.commit()
return 'OK'

if __name__ == '__main__':
app.run(debug=True)