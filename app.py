from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['RESTX_JSON'] = {'ensure_ascii': False, 'indent': 2}
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)
api = Api(app)

movie_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genres_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)


@movie_ns.route('/')
class MoviesView(Resource):
    def get(self):
        data_gen = request.args.get('genre_id', False)
        data_dir = request.args.get('director_id', False)
        movies = Movie.query
        if data_gen and data_dir:
            movies = movies.filter(Movie.genre_id == data_gen, Movie.director_id == data_dir)
        elif data_gen:
            movies = movies.filter(Movie.genre_id == data_gen)
        elif data_dir:
            movies = movies.filter(Movie.director_id == data_dir)
        return movies_schema.dump(movies.all()), 200


@movie_ns.route('/<int:m_id>')
class MovieView(Resource):
    def get(self, m_id):
        movie = Movie.query.get(m_id)
        return movie_schema.dump(movie), 200


@director_ns.route('/')
class DirectorsView(Resource):
    def post(self):
        data = request.json
        director = Director(**data)
        db.session.add(director)
        db.session.commit()
        return "", 201


@director_ns.route('/<int:d_id>')
class DirectorView(Resource):
    def put(self, d_id):
        data = request.json
        director = Director.query.filter(Director.id == d_id).one()
        director.name = data.get("name")
        db.session.add(director)
        db.session.commit()
        return "", 204

    def patch(self, d_id):
        director = Director.query.get(d_id)
        data = request.json
        if data.get("name"):
            director.name = data.get("name")
        db.session.add(director)
        return "", 204

    def delete(self, d_id):
        Director.query.filter(Director.id == d_id).delete()
        db.session.commit()
        return "", 204


@genres_ns.route('/')
class GenresView(Resource):
    def post(self):
        data = request.json
        genre = Genre(**data)
        db.session.add(genre)
        db.session.commit()
        return "", 201


@genres_ns.route('/<int:g_id>')
class GenreView(Resource):
    def put(self, g_id):
        data = request.json
        genre = Genre.query.filter(Genre.id == g_id).one()
        genre.name = data.get("name")
        db.session.add(genre)
        db.session.commit()
        return "", 204

    def patch(self, g_id):
        genre = Genre.query.get(g_id)
        data = request.json
        if data.get('name'):
            genre.name = data.get("name")
        db.session.add(genre)
        return "", 204

    def delete(self, g_id):
        Genre.query.filter(Genre.id == g_id).delete()
        db.session.commit()
        return "", 204


if __name__ == '__main__':
    app.run(debug=True)
