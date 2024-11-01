from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float
from flask_ckeditor import CKEditorField, CKEditor

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)
ckeditor = CKEditor(app)


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class lists(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    list_n: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)


class tasks(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    list_n: Mapped[str] = mapped_column(String(250), nullable=False)
    task_n: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    task_d: Mapped[str] = mapped_column(String(800), nullable=False)



class done(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    list_n: Mapped[str] = mapped_column(String(250), nullable=False)
    task_n: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    task_d: Mapped[str] = mapped_column(String(800), nullable=False)


class List_form(FlaskForm):
    name = StringField("List_name")
    add = SubmitField("ADD")


class Task_form(FlaskForm):
    t_name = StringField("Task_Name")
    t_body = CKEditorField("Description")
    add_task = SubmitField("Add Task")

class Edit_task(FlaskForm):
    t_name = StringField("Task_Name")
    t_body = CKEditorField("Description")
    edit_task = SubmitField("Edit Task")

@app.route("/")
def home():
    task_dict = {}
    task_list = []
    with app.app_context():
        rows = db.session.execute(db.select(lists)).scalars()
        for i in rows:
            task = db.session.execute(db.select(tasks).where(tasks.list_n == i.list_n)).scalars()
            for j in task:
                task_list.append(j.task_n)
            task_dict[i.list_n] = task_list
            task_list = []

    with app.app_context():
        d_rows = db.session.execute(db.select(done)).scalars()
        return render_template("index.html", list_task=task_dict, done=d_rows)


@app.route('/add_list', methods=['POST', 'GET'])
def add_list():
    form = List_form()
    if form.validate_on_submit():
        with app.app_context():
            row = lists(list_n=form.name.data)
            db.session.add(row)
            db.session.commit()
            return redirect(url_for("home"))
    return render_template('add.html', form=form)


@app.route('/add_task/<list>', methods=['POST', 'GET'])
def add_task(list):
    form = Task_form()
    if form.validate_on_submit():
        with app.app_context():
            row = tasks(list_n=list, task_n=form.t_name.data, task_d=form.t_body.data)
            db.session.add(row)
            db.session.commit()
            return redirect(url_for('home'))

    return render_template('add_task.html', form=form)


@app.route('/remove_list/<list>')
def remove_list(list):
    with app.app_context():
        row_list = db.session.execute(db.select(lists).where(lists.list_n == list)).scalar()
        db.session.delete(row_list)
        row_task = db.session.execute(db.select(tasks).where(tasks.list_n == list)).scalars()
        for i in row_task:
            db.session.delete(i)
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/remove_task/<task>')
def remove_task(task):
    with app.app_context():
        row = db.session.execute(db.select(tasks).where(tasks.task_n == task)).scalar()
        db.session.delete(row)
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/add_done/<task>')
def add_done(task):
    with app.app_context():
        row = db.session.execute(db.select(tasks).where(tasks.task_n == task)).scalar()
        d_row = done(list_n=row.list_n, task_n=row.task_n, task_d=row.task_d)
        db.session.add(d_row)
        db.session.delete(row)
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/remove_done/<task>')
def remove_done(task):
    with app.app_context():
        row = db.session.execute(db.select(done).where(done.task_n == task)).scalar()
        db.session.delete(row)
        db.session.commit()
        return redirect(url_for('home'))


@app.route('/task/<task>')
def task(task):
    with app.app_context():
        row = db.session.execute(db.select(tasks).where(tasks.task_n == task)).scalar()
        d_row = db.session.execute(db.select(done).where(done.task_n == task)).scalar()
        return render_template('task.html', task=row, done=d_row)


@app.route('/edit_task/<task>', methods=['POST', 'GET'])
def edit_task(task):
        form = Edit_task()
        if form.validate_on_submit():
            row = db.session.execute(db.select(tasks).where(tasks.task_n == task)).scalar()
            row.task_n = form.t_name.data
            row.task_d = form.t_body.data
            db.session.commit()
            return redirect(url_for('task', task=form.t_name.data))
        return render_template('edit_task.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)
