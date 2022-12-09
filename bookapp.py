import traceback

from flask import Flask
from flask import Flask
from flask import render_template
from flask import request
from flask import abort, redirect, url_for
import yaml
import os
import traceback
from urllib.request import urlopen
import json

app = Flask(__name__)

PRIORITIES = {
    0: 'Low',
    1: 'Medium',
    2: 'High'
}


fake_todos = [
    {
        'email': 'm@m.com',
        'task': "TODO 0",
        'priority': 0
     },
    {
        'email': 'a@m.com',
        'task': "TODO 1",
        'priority_idx': 2
    }
]

@app.route('/')
@app.route('/main')
def main():
    todos_list= []
    if os.path.isfile('./books_list.yaml'):
        with open('./books_list.yaml') as f:
            books_list_st = f.read()
            books_list = yaml.safe_load(books_list_st)

    print(len(todos_list), todos_list)

    return render_template('list_of_books.html', books=books_list)

@app.route("/clear")
def clear():
    with open('./todos_list.yaml', 'w') as f:
        yaml.dump([], f, default_flow_style=False)

    return redirect(url_for('main'))

@app.route("/delete")
def delete():
    try:
        if os.path.isfile('./books_list.yaml'):
            with open('./books_list.yaml') as f:
                books_list_st = f.read()
                books_list = yaml.safe_load(books_list_st)

        if request.method == 'GET':
            isbn = request.args.get('idx')
            item_pos_tbd = -1
            for i, todo in enumerate(books_list):
                if todo['isbn'] == isbn:
                    item_pos_tbd = i
            if item_pos_tbd != -1:
                del books_list[item_pos_tbd]

            with open('./books_list.yaml', 'w') as f:
                yaml.dump(books_list, f, default_flow_style=False)

    except Exception as e:
        traceback.print_exc()

    return redirect(url_for('main'))

@app.route("/submit")
def submit():
    todos_list= []
    try:
        if os.path.isfile('./todos_list.yaml'):
            with open('./todos_list.yaml') as f:
                todos_list_st = f.read()
                todos_list = yaml.safe_load(todos_list_st)

        if request.method == 'GET':
            new_todo = {}
            new_todo['priority_idx'] = int(request.args.get('priority'))
            new_todo['task'] = request.args.get('Task')
            if len(new_todo['task']) == 0:
                raise Exception('Task description should be completed!')
            new_todo['email'] = request.args.get('email')
            new_todo['todo_idx'] = max([-1] + [int(todo['todo_idx']) for todo in todos_list]) + 1

            todos_list.append(new_todo)

            with open('./todos_list.yaml', 'w') as f:
                yaml.dump(todos_list, f, default_flow_style=False)
    except Exception as e:
        traceback.print_exc()

    return redirect(url_for('main'))

@app.route('/add')
def add():
    try:
        books_list = []
        if os.path.isfile('./books_list.yaml'):
            with open('./books_list.yaml') as f:
                books_list_st = f.read()
                books_list = yaml.safe_load(books_list_st)
        if request.method == 'GET':
            isbn = request.args.get('isbn')
            print(f'isbn: {isbn}')
            try:
                url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}'
                response = urlopen(url)
                data_json = json.loads(response.read())
                print(data_json)
                item = data_json['items'][0]
                title = item['volumeInfo'].get('title')
                authors = ' // '.join(item['volumeInfo'].get('authors'))
                pageCount = item['volumeInfo'].get('pageCount', 'Not found')
                rating = item['volumeInfo'].get('pageCount', 'Unrated')
                error = ''

                books_list += [
                    {
                        'isbn': isbn,
                        'title': title,
                        'authors': authors,
                        'pageCount': pageCount,
                        'rating': rating,
                    }
                ]
                with open('./books_list.yaml', 'w') as f:
                    yaml.dump(books_list, f, default_flow_style=False)

            except Exception as e:
                traceback.print_exc()
    except Exception as e:
        traceback.print_exc()

    return redirect(url_for('main'))


@app.route("/googleapi")
def googleapi():
    try:
        if request.method == 'GET':
            isbn = request.args.get('isbn')
            print(f'isbn: {isbn}')
            try:
                url = f'https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}'
                response = urlopen(url)
                data_json = json.loads(response.read())
                print(data_json)
                item = data_json['items'][0]
                title = item['volumeInfo'].get('title')
                authors = ' // '.join(item['volumeInfo'].get('authors'))
                pageCount = item['volumeInfo'].get('pageCount', 'Not found')
                rating = item['volumeInfo'].get('pageCount', 'Unrated')
                error = ''
                return render_template('googleapiresult.html', title=title, authors=authors, pageCount=pageCount, rating=rating, error=error, isbn=isbn)
            except KeyError as k:
                title, authors, pageCount, rating = '---', '---', '---', '---'

                return render_template('googleapiresult.html', title=title, authors=authors, pageCount=pageCount, rating=rating, isbn=isbn, error=f'Empty result for {url}')
            except Exception as e:
                title, authors, pageCount, rating = '---', '---', '---', '---'

                error = f'General Error found. (error: {e})'
                return render_template('googleapiresult.html', title=title, authors=authors, pageCount=pageCount, rating=rating, isbn=isbn, error=error)
    except Exception as e:
        traceback.print_exc()


if __name__ == '__main__':
    app.run()
