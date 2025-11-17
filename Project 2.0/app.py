# app.py

from flask import (
    Flask,
    render_template,
    g,
    request,
    redirect,
    url_for,
    session,
    flash,
)
import mysql.connector
from mysql.connector import Error
from functools import wraps

from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Make sure SECRET_KEY is set for sessions
    if not app.secret_key:
        app.secret_key = "dev-secret-key"

    # ----------------- DB HELPER -----------------

    def get_db():
        """
        Get a per-request DB connection.
        For now it's mostly here so you can plug in queries later.
        """
        if "db" not in g:
            try:
                g.db = mysql.connector.connect(
                    host=app.config["DB_HOST"],
                    user=app.config["DB_USER"],
                    password=app.config["DB_PASSWORD"],
                    database=app.config["DB_NAME"],
                )
            except Error as e:
                print(f"Database connection error: {e}")
                g.db = None
        return g.db

    @app.teardown_appcontext
    def close_db(exception=None):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    # ----------------- AUTH HELPER -----------------

    def login_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                # redirect to login, remember where we came from
                return redirect(url_for("login", next=request.path))
            return view(*args, **kwargs)

        return wrapped

    # ----------------- PUBLIC ROUTES -----------------

    @app.route("/")
    def public_home():
        """
        Public landing page for B2B customers.
        """
        return render_template("public_home.html")

    @app.route("/order", methods=["GET", "POST"])
    def public_order():
        """
        Public order request form.
        Later this will insert into your Client and Client_Purchase_Order tables.
        """
        if request.method == "POST":
            company = request.form.get("company")
            contact = request.form.get("contact")
            email = request.form.get("email")
            phone = request.form.get("phone")
            notes = request.form.get("notes")

            # TODO: replace this with real INSERTs when DB is ready
            print("New public order request:")
            print("  Company:", company)
            print("  Contact:", contact)
            print("  Email:", email)
            print("  Phone:", phone)
            print("  Notes:", notes)

            return redirect(url_for("public_order_thanks"))

        return render_template("public_order.html")

    @app.route("/order/thanks")
    def public_order_thanks():
        """
        Simple thank-you page after public order submission.
        """
        return render_template("public_order_thanks.html")

    # ----------------- AUTH ROUTES -----------------

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """
        Very simple staff login.
        TODO: hook this into a proper Employee/User table.
        """
        if request.method == "POST":
            username = request.form.get("username")
            password = request.form.get("password")

            # Dummy credentials for now
            if username == "admin" and password == "password":
                session["user_id"] = username
                next_url = request.args.get("next") or url_for("admin_dashboard")
                return redirect(next_url)

            flash("Invalid username or password", "error")

        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("public_home"))

    # ----------------- ADMIN / PRIVATE ROUTES -----------------

    @app.route("/admin")
    @login_required
    def admin_dashboard():
        """
        Internal dashboard.
        """
        stats = {
            "client_count": 0,
            "open_work_orders": 0,
            "low_inventory_items": 0,
            "outstanding_receivables": 0.0,
        }
        return render_template("dashboard.html", stats=stats)

    @app.route("/admin/clients")
    @login_required
    def clients():
        """
        Internal client list view.
        Later: SELECT from Client table.
        """
        clients_data = []  # placeholder list
        return render_template("clients.html", clients=clients_data)

    @app.route("/admin/orders")
    @login_required
    def orders():
        """
        Internal client purchase orders / work orders view.
        """
        orders_data = []  # placeholder
        return render_template("orders.html", orders=orders_data)

    @app.route("/admin/inventory")
    @login_required
    def inventory():
        """
        Internal inventory view (components & rods).
        """
        inventory_items = []  # placeholder
        return render_template("inventory.html", inventory_items=inventory_items)

    @app.route("/admin/suppliers")
    @login_required
    def suppliers():
        """
        Internal supplier view.
        """
        suppliers_data = []  # placeholder
        return render_template("suppliers.html", suppliers=suppliers_data)

    @app.route("/admin/reports")
    @login_required
    def reports():
        """
        Internal reports shell.
        """
        return render_template("reports.html")

    # ----------------- ERROR HANDLER -----------------

    @app.errorhandler(404)
    def page_not_found(e):
        # Uses public 404 template
        return render_template("404.html"), 404

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
