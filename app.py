from flask import Flask, request
from user import user_api
import os

app = Flask(__name__)
app.register_blueprint(user_api)

if __name__ == "__main__":
    app.run(debug=os.getenv('DEBUG'),host=os.getenv('HOST'),port=os.getenv('PORT'))