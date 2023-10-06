from flask import (
    Flask,
    render_template,
    redirect,
    flash,
    url_for,
    session
)
import math
import numpy as np
from pylfsr import LFSR

from datetime import timedelta
from sqlalchemy.exc import (
    IntegrityError,
    DataError,
    DatabaseError,
    InterfaceError,
    InvalidRequestError,
)
from werkzeug.routing import BuildError


from flask_bcrypt import Bcrypt,generate_password_hash, check_password_hash

from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)

from app import create_app,db,login_manager,bcrypt
from models import User
from forms import login_form,register_form


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

app = create_app()

@app.before_request
def session_handler():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)

@app.route("/", methods=("GET", "POST"), strict_slashes=False)
def index():
    if current_user.is_authenticated:
        longueur = len(current_user.key)
    return render_template("index.html",title="Home")


@app.route("/login/", methods=("GET", "POST"), strict_slashes=False)
def login():
    form = login_form()

    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if check_password_hash(user.pwd, form.pwd.data):
                login_user(user)
                return redirect(url_for('index'))
            else:
                flash("Invalid Username or password!", "danger")
        except Exception as e:
            flash(e, "danger")

    return render_template("auth.html",
        form=form,
        text="Login",
        title="Login",
        btn_action="Login"
        )



# Register route
@app.route("/register/", methods=("GET", "POST"), strict_slashes=False)
def register():
    form = register_form()
    if form.validate_on_submit():
        try:
            email = form.email.data
            pwd = form.pwd.data
            username = form.username.data
            ascii_val = ""
            
            for character in pwd:
                ascii_val = ascii_val + str(format((ord(character)), '08b'))
            len1 = ascii_val[:20]
            dec_len1 = int(ascii_val[:20], base=2)
            print("len1=", dec_len1)
            len2 = ascii_val[20:41]
            dec_len2 = int(ascii_val[20:41], base=2)
            print("len2=", dec_len2)
            len3 = ascii_val[41:]
            dec_len3 = int(ascii_val[41:], base=2)
            print("len3=", dec_len3)
            print("gcd", math.gcd(dec_len1, dec_len2, dec_len3))
           
            len1_tab = []
            for digits in len1:
                len1_tab.append(int(digits))
            print(len1_tab)
            len2_tab = []
            for digits in len2:
                len2_tab.append(int(digits))
            print(len2_tab)
            len3_tab = []
            for digits in len3:
                len3_tab.append(int(digits))
            print(len3_tab)
            
            # calcul k1
            fpoly = [20,2]
            k1 = LFSR(initstate=len1_tab,fpoly=fpoly,counter_start_zero=False)
            #print('count \t state \t\toutbit \t seq')
            #print('-'*50)
            for _ in range(256):
                #print(L.count,L.state,'',L.outbit,L.seq,sep='\t')
                k1.next()
            #print('-'*50)
            print('k1: ',k1.seq)

            # calcul k2
            fpoly = [21,2]
            k2 = LFSR(initstate=len2_tab,fpoly=fpoly,counter_start_zero=False)
            for _ in range(256):
                k2.next()
            print('k2: ',k2.seq)

            # calcul k3
            fpoly = [23,2]
            k3 = LFSR(initstate=len3_tab,fpoly=fpoly,counter_start_zero=False)
            for _ in range(256):
                k3.next()
            print('k3: ',k3.seq)

            #calcul S = ( K1⋀(¬K2) ⊕ (K2⋀K3)
            s = []
            k1.info()
            #print(k1.getFullPeriod())
            for x in range(256):
              s.append(( k1.seq[x] and not(k2.seq[x]))^(k2.seq[x] and k3.seq[x])  )

            print("s:", s)
            print("s:", len(s))



            newuser = User(
                username=username,
                email=email,
                key=ascii_val,
                pwd=bcrypt.generate_password_hash(pwd),

            )
    
            db.session.add(newuser)
            db.session.commit()
            flash(f"Account Succesfully created", "success")
            return redirect(url_for("login"))

        except InvalidRequestError:
            db.session.rollback()
            flash(f"Something went wrong!", "danger")
        except IntegrityError:
            db.session.rollback()
            flash(f"User already exists!.", "warning")
        except DataError:
            db.session.rollback()
            flash(f"Invalid Entry", "warning")
        except InterfaceError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except DatabaseError:
            db.session.rollback()
            flash(f"Error connecting to the database", "danger")
        except BuildError:
            db.session.rollback()
            flash(f"An error occured !", "danger")
    return render_template("auth.html",
        form=form,
        text="Create account",
        title="Register",
        btn_action="Register account"
        )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True)






