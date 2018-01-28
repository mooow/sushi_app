import os, sqlite3, datetime, json, traceback
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)
app.config.from_object(__name__)


app.config.update(dict(
    DATABASE = os.path.join(app.root_path, "sushi.db"),
    SECRET_KEY="mariellapd",
    USERNAME="admin",
    PASSWORD="canavacciuolo"
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.route('/form')
@app.route('/')
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

@app.route('/results')
def results():
    # db = get_db()
    # entries = db.execute("select month, nome, ristoranti, days from entries left join users on submitter == id").fetchall()
    # columns = ["Mese", "Nome", "Ristoranti", "Giorni"]
    # mappa = dict(db.execute("select id,nome from ristoranti").fetchall())
    # ristoranti = dict.fromkeys(mappa.values)
    # giorni = {}
    # for entry in entries:
    #     for rist in json.parses(entry.ristoranti):
    #         rist = mappa[rist]
    #         if rist not in ristoranti:
    #             ristoranti[rist] == 1
    #         else: ristoranti[rist] += 1
    #     for giorno in json.parses(entry.days):
    #         if giorno not in giorni:
    #             giorni[giorno] == 1
    #         else: giorni[giorno] += 1
    query_votanti = "select nome from entries left join users using(userid) order by nome"
    query_quando = "select quando, count(*) as count from entries group by quando order by count desc"
    query_days = "select day, count(*) as count from entries_days group by day order by count desc"
    query_rist = "select nome, count(*) as count from entries_rist left join ristoranti using(ristid) group by nome order by count desc"

    d = {}
    db = get_db()
    d['Votanti'] = db.execute(query_votanti).fetchall()
    d['Quando'] = db.execute(query_quando).fetchall()
    d['Giorni'] = db.execute(query_days).fetchall()
    d['Ristoranti'] = db.execute(query_rist).fetchall()
    return render_template('results.html', tables=d)

@app.cli.command('cleandb')
def cleandb():
    db = get_db()
    tables = [ "entries", "entries_days", "entries_rist"]
    for table in tables:
        db.execute("DELETE FROM %s" % table)
    db.commit()
    print("Database cleaned (tables: {})".format(tables))

@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method != "POST": return results()
    ristoranti = request.form.getlist('ristorante')
    month = request.form.get('month')
    days = json.loads(request.form.get('days'))
    userid = request.form.get('user')
    quando = request.form.get('quando')
    db = get_db()
    try:
        db.execute("DELETE FROM entries_rist WHERE (month,userid)=(?,?)", (month, userid))
        db.execute("DELETE FROM entries_days WHERE (month,userid)=(?,?)", (month, userid))
        db.execute("DELETE FROM entries WHERE (month,userid)=(?,?)", (month, userid))
        db.execute("INSERT INTO entries(month, userid, quando) VALUES(?,?,?)", (month,userid,quando))
        for rist in ristoranti:
            print(month,userid,rist)
            db.execute("INSERT INTO entries_rist(month, userid, ristid) VALUES(?,?,?)", (month,userid,rist))
        for day in days:
            print(month,userid,day)
            db.execute("INSERT INTO entries_days(month, userid, day) VALUES(?,?,?)", (month,userid,day))
        db.commit()
        flash("Questionario inviato correttamente!", "info")
    except:
        db.rollback()
        flash("C'è stato un problema nell'invio del messaggio!", "danger")
        traceback.print_exc()
    return results()
