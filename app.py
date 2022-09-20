# Flask setup

import os
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# Google Sheets API setup
import gspread as gc
from oauth2client.service_account import ServiceAccountCredentials

credential = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])

client = gc.authorize(credential)

# Get the instance of the Spreadsheet
sheet = client.open("Flask-GSheets-API")

@app.route("/", methods=["GET"])
def index():
    return "Hello World! Flask backend for GDSC Google Sheets API"

@app.route("/all_reviews", methods=["GET"])
def all_reviews():
    # Get the first sheet of the Spreadsheet
    sheet_instance = sheet.get_worksheet(0)

    return jsonify(sheet_instance.get_all_values())

@app.route("/user:<email>", methods=["GET"])
def user_reviews(email):
    # Get the first sheet of the Spreadsheet
    sheet_instance = sheet.get_worksheet(0)

    # Get all the records of a user with id <email>
    records = sheet_instance.findall(email)

    if len(records) == 0:
        abort(404, description="User not found")

    # Get the row number of the first record of the user
    row = records[0].row

    # Get all the values in the row
    values = sheet_instance.row_values(row)

    return jsonify(values)

@app.route("/add_review", methods=["POST"])
def add_review():
    req = request.get_json()
    row = [req["email"], req["date"], req["score"]]
    sheet_instance = sheet.get_worksheet(0)
    sheet_instance.insert_row(row, 2)
    return jsonify(sheet_instance.get_all_values())


@app.route("/del_review/", methods=["POST"])
def del_review(email):
    req = request.get_json()
    row = [req["email"], req["date"], req["score"]]
    
    # Get the first sheet of the Spreadsheet
    wrksht = sheet.get_worksheet(0)
    cells = wrksht.findall(str(email))
    if cells == []:
        return jsonify({"error": "Email not found"})
    for c in cells:                
        wrksht.update_cell(c.row, c.col, "TODELETE")
        # wrksht.update(c, "")
    return jsonify(wrksht.get_all_values())

@app.route("/update_review", methods=["PATCH"])
def update_review():
    req = request.get_json()
    cells = sheet.findall(str(req["email"]))
    for c in cells:
        sheet.update_cell(c.row, 3, req["score"])
    return jsonify(sheet.get_all_records())

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)