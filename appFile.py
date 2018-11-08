from flask import Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_restful import marshal, fields
from user import user_api
import os, json

app = Flask(__name__)
cors = CORS(app)

if __name__ == "__main__":
    app.run(debug=os.getenv('DEBUG'),host=os.getenv('HOST'),port=os.getenv('PORT'))