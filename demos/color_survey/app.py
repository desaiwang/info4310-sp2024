# app.py
from flask import *
from whitenoise import WhiteNoise
import random
import io
import csv
import os

# helper functions for db access via postgres
from flask_sqlalchemy import SQLAlchemy
# helper functions for compressing server responses
from flask_compress import Compress
from flask_cors import CORS  # helper functions for cross-origin requests

if os.getenv('SQLALCHEMY_DATABASE_URI'):
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI').replace(
        "postgres://", "postgresql://", 1)
elif os.getenv('DATABASE_URL'):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL').replace(
        "postgres://", "postgresql://", 1)
else:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASEDIR, 'instance', 'app.db')}"

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['COMPRESS_MIMETYPES'] = ['text/html', 'text/css', 'text/plain']
app.wsgi_app = WhiteNoise(app.wsgi_app, root='static/',
                          prefix='static/', index_file="index.htm", autorefresh=True)
compress = Compress(app)
cors = CORS(app)
db = SQLAlchemy(app)

# put your database class at the top of the file


class Entry(db.Model):
    __tablename__ = "colorData"

    # figure out what the columns are and their datatypes
    id = db.Column(db.Integer, primary_key=True)  # id column, guaranteed value
    colorValue = db.Column(db.String(8), nullable=False)
    colorName = db.Column(db.String(40), nullable=False)
    genderIdentity = db.Column(db.String(2), nullable=False)
    colorBlind = db.Column(db.String(10), nullable=False)
    surveyType = db.Column(db.String(20), nullable=False)

    # init function to make rows
    def __init__(self, colVal, colName, genIdent, colBlind, survType):
        self.colorValue = colVal
        self.colorName = colName
        self.genderIdentity = genIdent
        self.colorBlind = colBlind
        self.surveyType = survType

    def getRow(self):
        return [self.colorValue,
                self.colorName,
                self.genderIdentity,
                self.colorBlind,
                self.surveyType]


# init database here
engine = db.create_engine(SQLALCHEMY_DATABASE_URI)
inspector = db.inspect(engine)

# if not inspector.has_table("color_Data"):
#     with app.app_context():
#         db.create_all()
# app.logger_info

# serve a hello world test page


@app.route('/', methods=['GET'])
def hello():
    return make_response("Greetings.")


def randomChroma():
    # Random function to generate fully saturated colors on surface of color cube
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    # The intuition here is that fully saturated colors MUST have either a 0 or 255 value on
    #  at least one of the color channels (so that it's on one of the sides of the cube)
    c = random.choice(['r', 'g', 'b'])
    if random.randint(0, 1) == 0:
        if c == 'r':
            r = 0
        elif c == 'g':
            g = 0
        elif c == 'b':
            b = 0
    else:
        if c == 'r':
            r = 255
        elif c == 'g':
            g = 255
        elif c == 'b':
            b = 255

    return '#%02x%02x%02x' % (r, g, b)


# serve one of two survey templates to the user randomly
#  if they have POSTed data using a form, save that data in the DB and then serve a template
@app.route('/survey', methods=['POST', 'GET'])
def survey():
    pass


# send a CSV of the database entries to the user
#  usually not a good idea to publish raw DB contents, but here we have no identifiable information hopefully
@app.route('/dump_data')
def dump():
    pass


if __name__ == "__main__":
    app.run(threaded=True, port=5000)
