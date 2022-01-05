from flask import Flask
from flask_cors import CORS


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins":"*"}})

@app.route("/basic")
def test_route():
  basicResponse = dict()
  basicResponse["string"] = "this is a test string"
  return basicResponse

app.run()