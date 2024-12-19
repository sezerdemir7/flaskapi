from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# PostgreSQL bağlantı ayarları
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:123456@localhost:5432/flaskApp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Veritabanı Modelleri

class Building(db.Model):
    __tablename__ = 'buildings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Bina ismi
    latitude = db.Column(db.Float, nullable=False)  # Enlem
    longitude = db.Column(db.Float, nullable=False)  # Boylam
    type = db.Column(db.String(100), nullable=False)  # Bina türü (ör: Akademik Binalar)
    sections = db.relationship('Section', backref='building', cascade="all, delete-orphan", lazy=True)

class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Alt bölüm ismi
    link = db.Column(db.String(200), nullable=False)  # Alt bölüm adresi
    building_id = db.Column(db.Integer, db.ForeignKey('buildings.id'), nullable=False)  # Ana bina ile ilişki
# Ana Sayfa
@app.route('/')
def index():
    return render_template('index.html')

# Binaya bölüm ekleme API'si
@app.route('/building/<int:building_id>/section', methods=['POST'])
def add_section(building_id):
    # JSON verisini al
    data = request.get_json()
    section_name = data.get('name')
    section_link = data.get('link')

    # Bina var mı kontrol et
    building = Building.query.get(building_id)
    if not building:
        return jsonify({"message": "Bina bulunamadı"}), 404

    # Yeni bölüm oluştur
    new_section = Section(
        name=section_name,
        link=section_link,
        building_id=building_id
    )

    # Veritabanına kaydet
    db.session.add(new_section)
    db.session.commit()

    return jsonify({
        "message": "Bölüm başarıyla eklendi",
        "section": {
            "id": new_section.id,
            "name": new_section.name,
            "link": new_section.link,
            "building_id": new_section.building_id
        }
    }), 201


# Bina Ekleme API
@app.route('/building', methods=['POST'])
def add_building():
    data = request.get_json()
    new_building = Building(
        name=data['name'],
        latitude=data['latitude'],
        longitude=data['longitude'],
        type=data['type']
    )
    db.session.add(new_building)
    db.session.commit()
    return jsonify({'message': 'Bina başarıyla eklendi!'}), 201

# Bina Listeleme API
@app.route('/buildings', methods=['GET'])
def get_buildings():
    buildings = Building.query.all()
    result = []
    for building in buildings:
        result.append({
            'id': building.id,
            'name': building.name,
            'latitude': building.latitude,
            'longitude': building.longitude,
            'type': building.type
        })
    return jsonify(result), 200

@app.route('/buildingsWithSection', methods=['GET'])
def get_buildings_with_sections():
    buildings = Building.query.all()
    result = []
    for building in buildings:
        sections = []
        for section in building.sections:
            sections.append({
                'id': section.id,
                'name': section.name,
                'link': section.link
            })
        result.append({
            'id': building.id,
            'name': building.name,
            'latitude': building.latitude,
            'longitude': building.longitude,
            'type': building.type,
            'sections': sections  # Bölümleri de ekliyoruz
        })
    return jsonify(result), 200


# Bina Silme API
@app.route('/building/<int:id>', methods=['DELETE'])
def delete_building(id):
    building = Building.query.get_or_404(id)
    db.session.delete(building)
    db.session.commit()
    return jsonify({'message': 'Bina başarıyla silindi!'}), 200

# Binaya Bölüm Ekleme API
@app.route('/building/<int:building_id>/section', methods=['POST'])
def add_section_to_building(building_id):
    data = request.get_json()
    building = Building.query.get_or_404(building_id)
    new_section = Section(
        name=data['name'],
        link=data['link'],
        building_id=building.id
    )
    db.session.add(new_section)
    db.session.commit()
    return jsonify({'message': 'Bölüm başarıyla eklendi!'}), 201

# Binadaki Bölümü Silme API
@app.route('/building/<int:building_id>/section/<int:section_id>', methods=['DELETE'])
def delete_section_from_building(building_id, section_id):
    section = Section.query.filter_by(id=section_id, building_id=building_id).first_or_404()
    db.session.delete(section)
    db.session.commit()
    return jsonify({'message': 'Bölüm başarıyla silindi!'}), 200

# Veritabanını başlat
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
