import os
import jinja2
import pandas as pd
from crawl import dataframe_preprocessing
from sqlalchemy import create_engine
from flask import Flask
from flask import render_template
app = Flask(__name__)
app.config['DEBUG'] = True
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))


@app.route('/')
@app.route('/index')
def index():
    template = jinja_env.get_template("index.html")
    data = read_papers_from_csv()
    data = dataframe_preprocessing(data)
    data = data.sample(50)
    return template.render(data=data)


def read_papers_from_csv():
    data = pd.read_csv("./data/arxiv_y2020_m11.csv")
    return data


def read_papers_from_db():
    database_path = 'sqlite:///data/data.db'
    engine = create_engine(database_path, echo=False)
    data = pd.read_sql_table("arxiv", database_path)
    engine.dispose()
    data.drop("index", axis=1, inplace=True)
    engine.dispose()
    return data


def main():
    try:
        # set FLASK_ENV=development
        app.run(host='127.0.0.1', port=8889)
    except:
        print('unable to open port')


if __name__ == "__main__":
    main()