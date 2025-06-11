from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = "gizli_anahtar"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///randevular.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Randevu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(100), nullable=False)
    telefon = db.Column(db.String(20), nullable=False)
    tarih = db.Column(db.Date, nullable=False)
    saat = db.Column(db.Time, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    randevular = Randevu.query.order_by(Randevu.tarih, Randevu.saat).all()
    return render_template('index.html', randevular=randevular, now=datetime.now)

@app.route('/randevu-al', methods=['GET', 'POST'])
def randevu_al():
    if request.method == 'POST':
        isim = request.form.get('isim')
        telefon = request.form.get('telefon')
        tarih_str = request.form.get('tarih')
        saat_str = request.form.get('saat')

        if not (isim and telefon and tarih_str and saat_str):
            flash("Lütfen tüm alanları doldurun!", "danger")
            return redirect(url_for('randevu_al'))

        try:
            tarih = datetime.strptime(tarih_str, '%Y-%m-%d').date()
            saat = datetime.strptime(saat_str, '%H:%M').time()
            if datetime.combine(tarih, saat) < datetime.now():
                flash("Geçmiş tarih ve saat seçilemez!", "danger")
                return redirect(url_for('randevu_al'))
        except ValueError:
            flash("Geçersiz tarih veya saat formatı!", "danger")
            return redirect(url_for('randevu_al'))

        yeni_randevu = Randevu(isim=isim, telefon=telefon, tarih=tarih, saat=saat)
        db.session.add(yeni_randevu)
        db.session.commit()

        flash("Randevunuz başarıyla alındı!", "success")
        return redirect(url_for('index'))

    return render_template('randevu_al.html', now=datetime.now)

@app.route('/randevu-sil/<int:id>', methods=['POST'])
def randevu_sil(id):
    randevu = Randevu.query.get_or_404(id)
    db.session.delete(randevu)
    db.session.commit()
    flash("Randevu başarıyla silindi.", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
