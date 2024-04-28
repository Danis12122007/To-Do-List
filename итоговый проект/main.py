from flask import Flask, abort, render_template, redirect
from flask_login import LoginManager, current_user, login_required
from flask_login import login_user, logout_user
from data import db_session
from data.tasks import Tasks
from data.user import RegisterForm
from forms.login import LoginForm
from forms.account import AccountForm
from data.users import User


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


curr_user_name = ''
curr_user_email = ''


# Route to display the main page
@app.route("/")
def index():
    return render_template("index.html")


# Route to create a new account
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


# Route to display the to-do list
@app.route('/account', methods=["GET", "POST"])
@login_required
def account():
    form = AccountForm()
    if form.validate_on_submit() and form.new_task_field.data:
        print(form.new_task_field.data)
        db_sess = db_session.create_session()
        tasks = Tasks()
        tasks.task = str(form.new_task_field.data)
        tasks.completed = 0
        current_user.tasks.append(tasks)
        db_sess.merge(current_user)
        db_sess.commit()
    db_sess = db_session.create_session()
    tasks = db_sess.query(Tasks).filter(Tasks.user == current_user).all()
    return render_template("account.html", tasks=tasks,
                           current_user_name=curr_user_name,
                           form=form)


# Route to mark a task as complete
@app.route("/complete/<int:task_id>")
def complete(task_id):
    db_sess = db_session.create_session()
    task = db_sess.query(Tasks).filter(Tasks.id == task_id).first()
    task.completed = 1
    db_sess.commit()
    return redirect(f"/{curr_user_name}")


# Route to log in account
@app.route('/login', methods=['GET', 'POST'])
def login():
    global curr_user_email, curr_user_name
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).\
            filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/account')
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


# Route to delete task
@app.route('/tasks_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def tasks_delete(id):
    db_sess = db_session.create_session()
    tasks = db_sess.query(Tasks).filter(Tasks.id == id,
                                        Tasks.user == current_user).first()

    if tasks:
        db_sess.delete(tasks)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/account')


# Route to log out
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == "__main__":
    db_session.global_init("todo.db")
    app.config['SECRET_KEY'] = 'my_secret_key'
    app.run(debug=True)
