from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
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
        dictionary={}
        for column in self.__table__.columns:
            dictionary[column.name] = getattr(self, column.name)
        return dictionary
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}

@app.route("/")
def home():
    return render_template("index.html")

## HTTP GET - Read Record

@app.route("/random")
def get_random_cafe():
    all_cafes=Cafe.query.all()
    random_cafe=random.choice(all_cafes)
    return jsonify(cafe=random_cafe.to_dict())

@app.route("/all")
def all():
    cafe_list=[]
    all_cafes=Cafe.query.all()
    for cafe in all_cafes:
        cafe_list.append(cafe.to_dict())

    return jsonify(cafe=cafe_list)

@app.route("/search")
def search():
    loc=request.args.get("loc")
    if loc==None:
        return jsonify( error= {"Not found": "Sorry we don't have cafe at that location"})

    else:
        cafe_search=Cafe.query.filter_by(location=loc)
        cafe_list=[cafe.to_dict() for cafe in cafe_search]
        return jsonify(cafe=cafe_list)



## HTTP POST - Create Record

@app.route("/add", methods = ["POST"])
def add():
    new_cafe=Cafe(
        name=request.args.get("name"),
        map_url=request.args.get("map_url"),
        img_url = request.args.get("img_url"),
        location = request.args.get("loc"),
        seats = request.args.get("seats"),
        has_toilet = bool(request.args.get("toilet")),
        has_wifi = bool(request.args.get("wifi")),
        has_sockets = bool(request.args.get("sockets")),
        can_take_calls = bool(request.args.get("calls")),
        coffee_price = request.args.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={"success": "Successfuly added a new cafe."})

## HTTP PUT/PATCH - Update Record

@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def patch_price(cafe_id):
    cafe_to_patch=Cafe.query.get(cafe_id)
    if cafe_to_patch:
        cafe_to_patch.coffee_price=request.args.get("coffee_price")
        db.session.commit()
        return jsonify(response={"success": "Successfuly patched a cafe."})
    else:
        return jsonify(error={"not found": "Not found such id"}),404



## HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete(cafe_id):
    if request.args.get("api-key")=="TopSecretAPIKey":
        cafe_to_delete=db.session.query(Cafe).get(cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"successs":"Cafe successfully deleted"}),200
        else:
            return jsonify(error={"not found": "Not found such id"}), 404
    else:
        return jsonify(error={"ari error": "wrong api key"}), 403


if __name__ == '__main__':
    app.run(debug=True)
