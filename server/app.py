#!/usr/bin/env python3

from flask import Flask, request, jsonify
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
import os

# Set up the base directory and database URI
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

# Initialize Flask-Migrate
migrate = Migrate(app, db)
db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([{'id': hero.id, 'name': hero.name, 'super_name': hero.super_name} for hero in heroes])

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = Hero.query.get(id)
    if not hero:
        return jsonify({'error': 'Hero not found'}), 404
    
    return jsonify({
        'id': hero.id,
        'name': hero.name,
        'super_name': hero.super_name,
        'hero_powers': [{
            'hero_id': hp.hero_id,
            'id': hp.id,
            'power': {'id': hp.power.id, 'name': hp.power.name, 'description': hp.power.description},
            'power_id': hp.power_id,
            'strength': hp.strength
        } for hp in hero.hero_powers]
    })

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([{'id': power.id, 'name': power.name, 'description': power.description} for power in powers])

@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({'error': 'Power not found'}), 404
    
    return jsonify({'id': power.id, 'name': power.name, 'description': power.description})

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({'error': 'Power not found'}), 404
    
    data = request.get_json()
    description = data.get('description')
    
    if description:
        if len(description) < 20:
            return jsonify({'errors': ['description must be at least 20 characters long']}), 400
        power.description = description
    
    db.session.commit()
    
    return jsonify({'id': power.id, 'name': power.name, 'description': power.description})

@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    data = request.get_json()

    # Validate strength
    if data['strength'] not in ['Strong', 'Weak', 'Average']:
        return jsonify({'errors': ['strength must be one of Strong, Weak, Average']}), 400

    # Validate hero_id and power_id
    hero = Hero.query.get(data['hero_id'])
    power = Power.query.get(data['power_id'])

    if not hero:
        return jsonify({'errors': ['Hero not found']}), 404
    if not power:
        return jsonify({'errors': ['Power not found']}), 404

    hero_power = HeroPower(
        strength=data['strength'],
        hero_id=data['hero_id'],
        power_id=data['power_id']
    )
    db.session.add(hero_power)
    db.session.commit()
    
    return jsonify({
        'id': hero_power.id,
        'hero_id': hero_power.hero_id,
        'power_id': hero_power.power_id,
        'strength': hero_power.strength,
        'hero': {'id': hero_power.hero.id, 'name': hero_power.hero.name, 'super_name': hero_power.hero.super_name},
        'power': {'id': hero_power.power.id, 'name': hero_power.power.name, 'description': hero_power.power.description}
    }), 201

@app.route('/hero_powers/<int:id>', methods=['PATCH'])
def update_hero_power(id):
    hero_power = HeroPower.query.get(id)
    if not hero_power:
        return jsonify({'error': 'HeroPower not found'}), 404

    data = request.get_json()
    
    # Validate strength
    if 'strength' in data and data['strength'] not in ['Strong', 'Weak', 'Average']:
        return jsonify({'errors': ['strength must be one of Strong, Weak, Average']}), 400

    # Update hero_power fields if present in the request
    if 'strength' in data:
        hero_power.strength = data['strength']

    db.session.commit()
    
    return jsonify({
        'id': hero_power.id,
        'hero_id': hero_power.hero_id,
        'power_id': hero_power.power_id,
        'strength': hero_power.strength,
        'hero': {'id': hero_power.hero.id, 'name': hero_power.hero.name, 'super_name': hero_power.hero.super_name},
        'power': {'id': hero_power.power.id, 'name': hero_power.power.name, 'description': hero_power.power.description}
    })

if __name__ == '__main__':
    app.run(port=5555, debug=True)

