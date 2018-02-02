import os, sqlite3, datetime, json, traceback, logging
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask_sslify import SSLify

logging.basicConfig(filename='flask.log', level=logging.DEBUG)
application = Flask(__name__)
application.config.from_object(__name__)
sslify = SSLify(application)

application.config.update(dict(
    DATABASE = os.path.join(application.root_path, "sushi.db"),
    SECRET_KEY='exjqocjsiqf43ucmrlzwvym34t8zksxfj43ydhtwjesej1qrsx'
))
application.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    rv = sqlite3.connect(application.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@application.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with application.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@application.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@application.route('/form')
@application.route('/')
def index():
    db = get_db()
    users = db.execute('select * from users order by nome').fetchall()
    ristoranti = db.execute('select * from ristoranti').fetchall()
    return render_template('index.html', calendar=_cal(), users=users, ristoranti=ristoranti)

def _cal():
    today = datetime.date.today()

    if today.day < 10:
        # current month
        return today.year, today.month
    elif today.month < 12:
        return today.year, today.month + 1
    else: return today.year + 1, 1

def _month():
    return "%04d%02d" % _cal()

@application.route('/results')
def results():
    month = request.args.get("month") or _month()

    query_votanti = "SELECT nome from entries left join users using(userid) WHERE month=? order by nome"
    query_quando = "SELECT quando, count(*) as count from entries WHERE month=? group by quando order by count desc"
    query_days = "SELECT day, count(*) as count from entries_days WHERE month=? group by day order by count desc"
    query_rist = "SELECT nome, count(*) as count from entries_rist left join ristoranti using(ristid) WHERE month=? group by nome order by count desc"
    d = {}
    db = get_db()
    d['Votanti'] = db.execute(query_votanti, (month, )).fetchall()
    d['Quando'] = db.execute(query_quando, (month, )).fetchall()
    d['Giorni'] = db.execute(query_days, (month, )).fetchall()
    d['Ristoranti'] = db.execute(query_rist, (month, )).fetchall()
    return render_template('results.html', tables=d, month=month)

@application.cli.command('cleandb')
def cleandb():
    db = get_db()
    tables = [ "entries", "entries_days", "entries_rist"]
    for table in tables:
        db.execute("DELETE FROM %s" % table)
    db.commit()
    print("Database cleaned (tables: {})".format(tables))

@application.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method != "POST": return results()
    ristoranti = request.form.getlist('ristorante')
    month = request.form.get('month')
    days = json.loads(request.form.get('days'))
    print(request.form.get('days'))
    print(days)
    userid = request.form.get('user')
    quando = request.form.get('quando')
    db = get_db()
    try:
        db.execute("DELETE FROM entries_rist WHERE month=? AND userid=?", (month, userid))
        db.execute("DELETE FROM entries_days WHERE month=? AND userid=?", (month, userid))
        db.execute("DELETE FROM entries WHERE month=? AND userid=?", (month, userid))
        db.execute("INSERT INTO entries(month, userid, quando) VALUES(?,?,?)", (month,userid,quando))
        for rist in ristoranti:
            db.execute("INSERT INTO entries_rist(month, userid, ristid) VALUES(?,?,?)", (month,userid,rist))
        for day in days:
            db.execute("INSERT INTO entries_days(month, userid, day) VALUES(?,?,?)", (month,userid,day))
        db.commit()
        flash("Questionario inviato correttamente!", "info")
    except:
        db.rollback()
        flash("C'è stato un problema nell'invio del messaggio!", "danger")
        logging.error(traceback.format_exc())
    return results()


    # run the app.
if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    application.run()
