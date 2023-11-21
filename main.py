from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
from sqlalchemy import exc

'''
Install the required packages first: 
Open the Terminal in PyCharm (bottom left). 

On Windows type:
python -m pip install -r requirements.txt

On MacOS type:
pip3 install -r requirements.txt

This will install the packages from requirements.txt for this project.
'''

app = Flask(__name__)

# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

# with app.create_context():
#     db.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random")
def get_random_cafe():
    all_cafes = db.session.execute(db.select(Cafe)).scalars().all()
    random_cafe = random.choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())


@app.route("/all")
def get_all_cafes():
    # list of all the cafes
    all_cafes = db.session.execute(db.select(Cafe).order_by(Cafe.name)).scalars().all()
    # list of all the cafes as dicts
    all_cafes_dict = []
    for cafe in all_cafes:
        all_cafes_dict.append(cafe.to_dict())
    return jsonify(cafes=all_cafes_dict)


@app.route("/search")
def search_cafe():
    query_loc = request.args.get("loc")
    loc_cafes = db.session.execute(db.select(Cafe).where(Cafe.location == query_loc)).scalars().all()
    if loc_cafes:
        return jsonify(cafes=[cafe.to_dict() for cafe in loc_cafes])
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."}), 404


# HTTP POST - Create Record

@app.route("/add", methods=["POST"])
def post_new_cafe():
    try:
        new_cafe_data = Cafe(
             name=request.form.get("name"),
             map_url=request.form.get("map_url"),
             img_url=request.form.get("img_url"),
             location=request.form.get("location"),
             seats=request.form.get("seats"),
             has_toilet=bool(request.form.get("has_toilet")),
             has_wifi=bool(request.form.get("has_wifi")),
             has_sockets=bool(request.form.get("has_sockets")),
             can_take_calls=bool(request.form.get("can_take_calls")),
             coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe_data)
        db.session.commit()
        return jsonify(response={"success": "Successfully added the new cafe."})
    except exc.IntegrityError:
        db.session.rollback()
        return jsonify(response={"Oh no!": "This cafe already exists in the database."})


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def patch_cafe(cafe_id):
    cafe_to_update = db.get_or_404(Cafe, cafe_id)
    new_price = request.args.get("new_price")
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(response={"success": "Successfully updated the price."}), 200


# HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    api_key = "123api"
    cafe_to_delete = db.get_or_404(Cafe, cafe_id)
    input_api_key = request.args.get("api-key")
    if api_key == input_api_key:
        db.session.delete(cafe_to_delete)
        db.session.commit()
        return jsonify(response={"success": "Successfully deleted the cafe from the database."}), 200
    else:
        return jsonify(error={"Error": "Sorry, that's not allowed. Make sure you have the correct api_key."}), 403


# Error handling
@app.errorhandler(404)
def cafe_not_found(e):
    return jsonify(error={"Not Found": "Sorry a cafe with that id was not found in the database."}), 404


if __name__ == '__main__':
    app.run(debug=True)
