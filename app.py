import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev-secret-key")

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "postgresql://martin_admin:Vj4EBZKu9NetAdILgoaxGV7roXmfLahi@dpg-d8mvl7ojs32c73d4uqcg-a.ohio-postgres.render.com/bibliotheque_db_pl37",
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

FACULTIES = [
    "Informatique",
    "Médecine",
    "Économie",
    "Droit",
    "Santé publique",
    "Lettres",
    "SPA",
    "USAM",
    "Sciences d'éducation",
    "Agronomie",
    "Construction",
]

GENDERS = ["Homme", "Femme", "Autre"]
ROLES = ["Étudiant"]

DEFAULT_BOOKS = [
    {"title": "Programmation en Python", "author": "Antoine de Saint-Exupéry", "faculty": "Informatique", "stock": 4, "total": 4},
    {"title": "Réseaux et télécommunications", "author": "Hugo Martin", "faculty": "Informatique", "stock": 3, "total": 3},
    {"title": "Anatomie humaine", "author": "Éric Baudrillard", "faculty": "Médecine", "stock": 3, "total": 3},
    {"title": "Pharmacologie de base", "author": "Isabelle Laurent", "faculty": "Médecine", "stock": 2, "total": 2},
    {"title": "Macroéconomie", "author": "Marie Curie", "faculty": "Économie", "stock": 5, "total": 5},
    {"title": "Gestion financière", "author": "Paul Bernard", "faculty": "Économie", "stock": 3, "total": 3},
    {"title": "Droit constitutionnel", "author": "Jean Dupont", "faculty": "Droit", "stock": 2, "total": 2},
    {"title": "Procédure civile", "author": "Claire Durand", "faculty": "Droit", "stock": 3, "total": 3},
    {"title": "Épidémiologie", "author": "Sophie Martin", "faculty": "Santé publique", "stock": 3, "total": 3},
    {"title": "Santé communautaire", "author": "Nadia Mbaye", "faculty": "Santé publique", "stock": 4, "total": 4},
    {"title": "Littérature française", "author": "Victor Hugo", "faculty": "Lettres", "stock": 4, "total": 4},
    {"title": "Analyse de texte", "author": "Pauline Roche", "faculty": "Lettres", "stock": 3, "total": 3},
    {"title": "Psychologie SPA", "author": "Anne Leroux", "faculty": "SPA", "stock": 3, "total": 3},
    {"title": "Développement personnel", "author": "Sonia Kebe", "faculty": "SPA", "stock": 2, "total": 2},
    {"title": "Méthodologie de recherche USAM", "author": "Olivier N'Goma", "faculty": "USAM", "stock": 2, "total": 2},
    {"title": "Leadership et management", "author": "Amina Traoré", "faculty": "USAM", "stock": 3, "total": 3},
    {"title": "Pédagogie moderne", "author": "Claire Bernard", "faculty": "Sciences d'éducation", "stock": 4, "total": 4},
    {"title": "Psychopédagogie", "author": "Émilie Robert", "faculty": "Sciences d'éducation", "stock": 3, "total": 3},
    {"title": "Agroécologie", "author": "Pauline Kouassi", "faculty": "Agronomie", "stock": 3, "total": 3},
    {"title": "Production végétale", "author": "Mohamed Dia", "faculty": "Agronomie", "stock": 2, "total": 2},
    {"title": "Gestion de chantier", "author": "Marc Lemoine", "faculty": "Construction", "stock": 2, "total": 2},
    {"title": "Matériaux du bâtiment", "author": "Sarah Ndiaye", "faculty": "Construction", "stock": 3, "total": 3},
]


def get_book_summary(book):
    return (
        f"{book.title} est un ouvrage pratique de {book.faculty}. "
        f"Écrit par {book.author}, il aide les étudiants à comprendre les concepts clés et à appliquer le savoir en contexte réel."
    )


def get_book_reading_content(book):
    introduction = (
        f"Bienvenue dans la lecture de '{book.title}',\n"
        f"par {book.author}.\n\n"
        "Cette lecture interactive vous présente les idées principales du livre "
        f"et des conseils pratiques pour votre parcours en {book.faculty}.\n"
    )
    chapitre_1 = (
        "Chapitre 1 : Concepts fondamentaux\n"
        "Dans ce premier chapitre, le livre introduit les notions essentielles, les termes techniques et les objectifs pédagogiques. "
        "Vous découvrirez comment structurer votre travail et appliquer les méthodes étudiées.\n\n"
    )
    chapitre_2 = (
        "Chapitre 2 : Applications pratiques\n"
        "La suite du contenu propose des exemples concrets, des cas d'étude et des exercices adaptés à votre formation. "
        "Ce passage vous aide à construire une base solide avant de passer à l'étape suivante.\n\n"
    )
    conclusion = (
        "Conclusion : Résumé et prochaines étapes\n"
        "À la fin de cette lecture, vous aurez une meilleure compréhension de la matière et pourrez continuer votre travail avec confiance. "
        "N'oubliez pas de revenir à l'application pour consulter d'autres livres et vos ressources de prêt."
    )
    return introduction + chapitre_1 + chapitre_2 + conclusion


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    gender = db.Column(db.String(16), nullable=False)
    birth_date = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    faculty = db.Column(db.String(100), nullable=True)
    role = db.Column(db.String(32), nullable=False)
    library_section = db.Column(db.String(120), nullable=True)
    office_number = db.Column(db.String(80), nullable=True)
    management_area = db.Column(db.String(120), nullable=True)
    office_phone = db.Column(db.String(30), nullable=True)
    profile_image = db.Column(db.String(255), nullable=True)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    faculty = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    total = db.Column(db.Integer, nullable=False, default=0)
    borrow_records = db.relationship("BorrowRecord", backref="book", lazy=True)


class BorrowRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String(120), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("book.id"), nullable=False)
    book_title = db.Column(db.String(255), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


def find_book(book_id):
    return Book.query.get(book_id)


def find_user_by_username(username):
    return User.query.filter_by(username=username).first()


def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    return User.query.get(user_id)


def init_db():
    with app.app_context():
        try:
            db.create_all()
            if Book.query.count() == 0:
                for book_data in DEFAULT_BOOKS:
                    db.session.add(Book(**book_data))
                db.session.commit()
            print("✅ Base de données initialisée avec succès.")
        except Exception as e:
            print(f"❌ Erreur de connexion à la base de données : {e}")
            print("⚠️  L'application continuera sans accès à la base.")
  

@app.context_processor
def inject_current_user():
    return {"current_user": get_current_user()}


def calculate_monthly_report():
    report = {}
    today = datetime.today()
    month = today.month
    year = today.year
    for record in BorrowRecord.query.all():
        if record.date.month == month and record.date.year == year:
            report.setdefault(record.book_title, 0)
            report[record.book_title] += 1
    return report


@app.route("/")
def home():
    user = get_current_user()
    if user and user.role == "Étudiant":
        faculty_books = Book.query.filter_by(faculty=user.faculty).all()
        return render_template("index.html", user=user, books=faculty_books)
    return render_template("index.html", user=user)


@app.route("/catalog")
def catalog():
    user = get_current_user()
    books = Book.query.order_by(Book.faculty, Book.title).all()
    return render_template("catalog.html", user=user, books=books)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        email = request.form.get("email", "").strip()
        gender = request.form.get("gender", "").strip()
        birth_date = request.form.get("birth_date", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        role = request.form.get("role", "").strip()
        faculty = request.form.get("faculty", "").strip()
        library_section = request.form.get("library_section", "").strip()
        office_number = request.form.get("office_number", "").strip()
        management_area = request.form.get("management_area", "").strip()
        office_phone = request.form.get("office_phone", "").strip()
        if (
            not username
            or not password
            or not email
            or "@" not in email
            or "." not in email
            or gender not in GENDERS
            or not birth_date
            or not phone
            or not address
            or role not in ROLES
            or (role == "Étudiant" and faculty not in FACULTIES)
            or (role == "Bibliothécaire" and (not library_section or not office_number))
            or (role == "Directeur" and (not management_area or not office_phone))
        ):
            flash("Veuillez renseigner tous les champs d'inscription correctement.", "danger")
            return redirect(url_for("register"))
        if find_user_by_username(username):
            flash("Ce nom d'utilisateur existe déjà.", "danger")
            return redirect(url_for("register"))
        if role != "Étudiant":
            faculty = None
        if role != "Bibliothécaire":
            library_section = None
            office_number = None
        if role != "Directeur":
            management_area = None
            office_phone = None
        user = User(
            username=username,
            password=password,
            email=email,
            gender=gender,
            birth_date=birth_date,
            phone=phone,
            address=address,
            faculty=faculty,
            role=role,
            library_section=library_section,
            office_number=office_number,
            management_area=management_area,
            office_phone=office_phone,
            profile_image=None,
        )
        try:
            db.session.add(user)
            db.session.commit()
            print(f"✅ Utilisateur créé avec succès : ID={user.id}, Username={user.username}")
            # Vérification : récupérer l'utilisateur juste créé
            check_user = User.query.filter_by(username=username).first()
            if check_user:
                print(f"✅ Utilisateur retrouvé en base : ID={check_user.id}, Role={check_user.role}")
            else:
                print(f"❌ ATTENTION : Utilisateur NOT retrouvé en base après commit!")
            session["user_id"] = user.id
            flash("Inscription réussie. Vous êtes connecté.", "success")
            if role == "Étudiant":
                return redirect(url_for("student_dashboard"))
            if role == "Bibliothécaire":
                return redirect(url_for("librarian_books"))
            return redirect(url_for("director_stock"))
        except Exception as e:
            db.session.rollback()
            print(f"❌ Erreur SQL : {str(e)}")
            flash(f"Erreur lors de l'enregistrement : {str(e)}", "danger")
            return redirect(url_for("register"))
    return render_template("register.html", faculties=FACULTIES, genders=GENDERS, roles=ROLES)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        user = find_user_by_username(username)
        if user and user.password == password:
            session["user_id"] = user.id
            flash("Connexion réussie.", "success")
            if user.role == "Étudiant":
                return redirect(url_for("student_dashboard"))
            if user.role == "Bibliothécaire":
                return redirect(url_for("librarian_books"))
            return redirect(url_for("director_stock"))
        flash("Nom d'utilisateur ou mot de passe invalide.", "danger")
        return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Vous êtes déconnecté.", "success")
    return redirect(url_for("home"))


@app.route("/reset_password", methods=["GET", "POST"])
def reset_password():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        new_password = request.form.get("new_password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()

        if not username or not email or not new_password or not confirm_password:
            flash("Veuillez remplir tous les champs pour réinitialiser votre mot de passe.", "danger")
            return redirect(url_for("reset_password"))

        if new_password != confirm_password:
            flash("Les mots de passe ne correspondent pas.", "danger")
            return redirect(url_for("reset_password"))

        user = User.query.filter_by(username=username, email=email).first()
        if not user:
            flash("Utilisateur introuvable ou email incorrect.", "danger")
            return redirect(url_for("reset_password"))

        user.password = new_password
        db.session.commit()
        flash("Mot de passe réinitialisé avec succès. Vous pouvez maintenant vous connecter.", "success")
        return redirect(url_for("login"))

    return render_template("reset_password.html")


@app.route("/student", methods=["GET"])
def student_dashboard():
    user = get_current_user()
    if not user:
        flash("Veuillez vous connecter pour accéder à votre espace étudiant.", "warning")
        return redirect(url_for("login"))
    faculty_books = Book.query.filter_by(faculty=user.faculty).all()
    return render_template(
        "student_dashboard.html",
        user=user,
        books=faculty_books[:8],
        total_books=len(faculty_books),
    )


@app.route("/student/books", methods=["GET"])
def student_books():
    user = get_current_user()
    if not user:
        flash("Veuillez vous connecter pour accéder aux livres.", "warning")
        return redirect(url_for("login"))
    query = request.values.get("query", "").strip()
    results = Book.query.filter_by(faculty=user.faculty)
    if query:
        results = results.filter(
            or_(
                Book.title.ilike(f"%{query}%"),
                Book.author.ilike(f"%{query}%"),
            )
        )
    results = results.all()
    return render_template("student_search.html", books=results, query=query, user=user)


@app.route("/student/profile", methods=["GET", "POST"])
def student_profile():
    user = get_current_user()
    if not user:
        flash("Veuillez vous connecter pour accéder à votre profil.", "warning")
        return redirect(url_for("login"))
    if request.method == "POST":
        username = request.form.get("username", user.username).strip()
        password = request.form.get("password", "").strip()
        email = request.form.get("email", user.email).strip()
        gender = request.form.get("gender", user.gender).strip()
        birth_date = request.form.get("birth_date", user.birth_date).strip()
        phone = request.form.get("phone", user.phone).strip()
        address = request.form.get("address", user.address).strip()
        file = request.files.get("profile_image")
        if username and username != user.username and find_user_by_username(username):
            flash("Ce nom d'utilisateur est déjà utilisé.", "danger")
            return redirect(url_for("student_profile"))
        if not email or "@" not in email or "." not in email:
            flash("Veuillez saisir une adresse email valide.", "danger")
            return redirect(url_for("student_profile"))
        if gender not in GENDERS:
            flash("Veuillez sélectionner un genre valide.", "danger")
            return redirect(url_for("student_profile"))
        if not birth_date or not phone or not address:
            flash("Veuillez remplir les informations personnelles.", "danger")
            return redirect(url_for("student_profile"))
        user.username = username
        if password:
            user.password = password
        user.email = email
        user.gender = gender
        user.birth_date = birth_date
        user.phone = phone
        user.address = address
        if file and file.filename:
            if allowed_file(file.filename):
                filename = secure_filename(f"user_{user.id}_" + file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)
                user.profile_image = f"/static/uploads/{filename}"
            else:
                flash("Format de fichier non autorisé. Utilisez png, jpg, jpeg ou gif.", "danger")
                return redirect(url_for("student_profile"))
        db.session.commit()
        flash("Profil mis à jour avec succès.", "success")
        return redirect(url_for("student_profile"))
    return render_template("student_profile.html", user=user, genders=GENDERS)


@app.route("/student/book/<int:book_id>")
def student_book(book_id):
    user = get_current_user()
    if not user:
        flash("Veuillez vous connecter pour accéder aux livres.", "warning")
        return redirect(url_for("login"))
    book = find_book(book_id)
    if not book or book.faculty != user.faculty:
        flash("Livre introuvable ou non disponible pour votre faculté.", "danger")
        return redirect(url_for("student_books"))
    summary = get_book_summary(book)
    return render_template("student_book.html", book=book, user=user, summary=summary)


@app.route("/student/book/<int:book_id>/read")
def student_book_read(book_id):
    user = get_current_user()
    if not user:
        flash("Veuillez vous connecter pour accéder aux livres.", "warning")
        return redirect(url_for("login"))
    book = find_book(book_id)
    if not book or book.faculty != user.faculty:
        flash("Livre introuvable ou non disponible pour votre faculté.", "danger")
        return redirect(url_for("student_books"))
    content = get_book_reading_content(book)
    return render_template("student_book_read.html", book=book, content=content, user=user)


@app.route("/librarian/books")
def librarian_books():
    return render_template("librarian_books.html", books=Book.query.all(), faculties=FACULTIES)


@app.route("/librarian/books/add", methods=["POST"])
def add_book():
    title = request.form.get("title", "").strip()
    author = request.form.get("author", "").strip()
    faculty = request.form.get("faculty", "").strip()
    stock = request.form.get("stock", "0").strip()
    if not title or not author or not stock.isdigit() or faculty not in FACULTIES:
        flash("Veuillez remplir tous les champs correctement.", "danger")
        return redirect(url_for("librarian_books"))
    stock = int(stock)
    book = Book(title=title, author=author, faculty=faculty, stock=stock, total=stock)
    db.session.add(book)
    db.session.commit()
    flash("Livre ajouté avec succès.", "success")
    return redirect(url_for("librarian_books"))


@app.route("/librarian/books/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    book = find_book(book_id)
    if not book:
        flash("Livre introuvable.", "danger")
        return redirect(url_for("librarian_books"))
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        faculty = request.form.get("faculty", "").strip()
        stock = request.form.get("stock", "0").strip()
        if not title or not author or not stock.isdigit() or faculty not in FACULTIES:
            flash("Veuillez remplir tous les champs correctement.", "danger")
            return redirect(url_for("edit_book", book_id=book_id))
        new_stock = int(stock)
        diff = new_stock - book.total
        book.title = title
        book.author = author
        book.faculty = faculty
        book.total = new_stock
        book.stock = max(0, book.stock + diff)
        db.session.commit()
        flash("Livre modifié avec succès.", "success")
        return redirect(url_for("librarian_books"))
    return render_template("edit_book.html", book=book, faculties=FACULTIES)


@app.route("/librarian/books/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    book = find_book(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        flash("Livre supprimé.", "success")
    else:
        flash("Livre introuvable.", "danger")
    return redirect(url_for("librarian_books"))


@app.route("/librarian/borrow", methods=["GET", "POST"])
def librarian_borrow():
    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip()
        book_id = request.form.get("book_id", "").strip()
        action = request.form.get("action")
        if not student_name or not book_id.isdigit():
            flash("Veuillez renseigner le nom de l'étudiant et le numéro du livre.", "danger")
            return redirect(url_for("librarian_borrow"))
        book = find_book(int(book_id))
        if not book:
            flash("Livre introuvable.", "danger")
            return redirect(url_for("librarian_borrow"))
        if action == "borrow":
            if book.stock < 1:
                flash("Stock insuffisant pour emprunter ce livre.", "danger")
            else:
                book.stock -= 1
                record = BorrowRecord(
                    student_name=student_name,
                    book_id=book.id,
                    book_title=book.title,
                    action="emprunt",
                    date=datetime.now(),
                )
                db.session.add(record)
                db.session.commit()
                flash("Emprunt enregistré avec succès.", "success")
        elif action == "return":
            if book.stock >= book.total:
                flash("Ce livre est déjà au stock maximum.", "warning")
            else:
                book.stock += 1
                record = BorrowRecord(
                    student_name=student_name,
                    book_id=book.id,
                    book_title=book.title,
                    action="retour",
                    date=datetime.now(),
                )
                db.session.add(record)
                db.session.commit()
                flash("Retour enregistré et stock mis à jour.", "success")
        return redirect(url_for("librarian_borrow"))
    return render_template("librarian_borrow.html", books=Book.query.all(), borrow_records=BorrowRecord.query.order_by(BorrowRecord.date.desc()).all())


@app.route("/director/stock")
def director_stock():
    return render_template("director_stock.html", books=Book.query.all())


@app.route("/director/reports")
def director_reports():
    monthly_report = calculate_monthly_report()
    return render_template("director_reports.html", report=monthly_report)


@app.route("/director/borrowings")
def director_borrowings():
    return render_template("director_borrowings.html", borrow_records=BorrowRecord.query.order_by(BorrowRecord.date.desc()).all())


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
