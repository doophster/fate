from http.server import HTTPServer, BaseHTTPRequestHandler
import sqlite3
import json
from datetime import datetime
from urllib.parse import urlparse, parse_qs
import os

# HOW TO RUN THIS:
#   1. open terminal in the /machine folder
#   2. type:  python3 data.py
#   3. server starts at http://localhost:5000
#   4. open index.html in your browser and play
#   5. check http://localhost:5000/api/stats to see collective data

def init_db():
    # connect to (or create) the database file
    conn = sqlite3.connect('folklore_data.db')
    c = conn.cursor()

    # table for every single interaction — one row per button click
    c.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            superstition  TEXT NOT NULL,
            outcome       TEXT NOT NULL,
            luck_change   INTEGER,
            timestamp     TEXT NOT NULL,
            session_id    TEXT
        )
    ''')

    # table for per-session totals — one row per browser session
    c.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id          TEXT PRIMARY KEY,
            total_luck          INTEGER DEFAULT 0,
            interactions_count  INTEGER DEFAULT 0,
            first_interaction   TEXT,
            last_interaction    TEXT
        )
    ''')

    conn.commit()
    conn.close()


# helper functions

def get_db():
    # returns a connection to the database
    # row_factory allows access to columns by name (row['outcome'])
    # instead of just by index (row[1])
    conn = sqlite3.connect('folklore_data.db')
    conn.row_factory = sqlite3.Row
    return conn


def json_response(handler, data, status=200):
    # sends a json response back to whoever called the api
    body = json.dumps(data).encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Content-Length', len(body))
    # cors headers — these allow your html pages to talk to this server
    # even though they're on different "ports" (file vs localhost:5000)
    handler.send_header('Access-Control-Allow-Origin', '*')
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type')
    handler.end_headers()
    handler.wfile.write(body)


def error_response(handler, message, status=400):
    json_response(handler, {'error': message, 'success': False}, status)


# request handler
# this is the main class that receives requests
# from html pages and figures out what to do

class FolkloreHandler(BaseHTTPRequestHandler):

    # silence the default request logging (it's noisy)
    # comment this out if you want to see every request in the terminal
    def log_message(self, format, *args):
        pass

    # handle preflight cors requests — browsers send these before POST requests
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    # GET requests — fetching data
    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path
        params = parse_qs(parsed.query)

        # /api/stats — collective data across all users
        if path == '/api/stats':
            self.handle_stats()

        # /api/luck?session_id=abc123 — luck score for one session
        elif path == '/api/luck':
            session_id = params.get('session_id', [None])[0]
            self.handle_get_luck(session_id)

        # /api/history?session_id=abc123 — full history for one session
        elif path == '/api/history':
            session_id = params.get('session_id', [None])[0]
            self.handle_history(session_id)

        else:
            error_response(self, 'not found', 404)

    # POST requests — saving data
    def do_POST(self):
        parsed = urlparse(self.path)
        path   = parsed.path

        # /api/record — save a new interaction
        if path == '/api/record':
            # read the request body
            length = int(self.headers.get('Content-Length', 0))
            body   = self.rfile.read(length)

            # parse the json — wrap in try/except in case it's malformed
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                error_response(self, 'invalid json')
                return

            self.handle_record(data)

        else:
            error_response(self, 'not found', 404)


    # endpoint handlers — one function per api route

    def handle_record(self, data):
        # pull fields out of the incoming json
        superstition = data.get('superstition')
        outcome      = data.get('outcome')
        luck_change  = data.get('luck_change', 0)
        session_id   = data.get('session_id')
        timestamp    = datetime.now().isoformat()

        # validate — we need at least these three
        if not superstition or not outcome or not session_id:
            error_response(self, 'missing required fields: superstition, outcome, session_id')
            return

        conn = get_db()
        c    = conn.cursor()

        try:
            # save the interaction
            c.execute('''
                INSERT INTO interactions (superstition, outcome, luck_change, timestamp, session_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (superstition, outcome, luck_change, timestamp, session_id))

            # check if this session already exists
            c.execute('SELECT total_luck, interactions_count FROM sessions WHERE session_id = ?', (session_id,))
            session = c.fetchone()

            if session:
                # update existing session totals
                new_luck  = session['total_luck'] + luck_change
                new_count = session['interactions_count'] + 1
                c.execute('''
                    UPDATE sessions
                    SET total_luck = ?, interactions_count = ?, last_interaction = ?
                    WHERE session_id = ?
                ''', (new_luck, new_count, timestamp, session_id))
            else:
                # create a new session row
                c.execute('''
                    INSERT INTO sessions (session_id, total_luck, interactions_count, first_interaction, last_interaction)
                    VALUES (?, ?, 1, ?, ?)
                ''', (session_id, luck_change, timestamp, timestamp))

            conn.commit()

            # fetch the updated luck score to send back
            c.execute('SELECT total_luck FROM sessions WHERE session_id = ?', (session_id,))
            current_luck = c.fetchone()['total_luck']

            json_response(self, {
                'success': True,
                'current_luck': current_luck
            })

        except Exception as e:
            conn.rollback()
            error_response(self, f'database error: {str(e)}', 500)

        finally:
            conn.close()


    def handle_get_luck(self, session_id):
        if not session_id:
            error_response(self, 'missing session_id')
            return

        conn = get_db()
        c    = conn.cursor()
        c.execute('SELECT total_luck FROM sessions WHERE session_id = ?', (session_id,))
        row = c.fetchone()
        conn.close()

        luck = row['total_luck'] if row else 0
        json_response(self, {'luck': luck, 'session_id': session_id})


    def handle_stats(self):
        conn = get_db()
        c    = conn.cursor()

        # total interactions across everyone
        c.execute('SELECT COUNT(*) as n FROM interactions')
        total_interactions = c.fetchone()['n']

        # total unique sessions (= unique visitors roughly)
        c.execute('SELECT COUNT(*) as n FROM sessions')
        total_users = c.fetchone()['n']

        # breakdown by superstition — fortune rate, misfortune rate, etc.
        c.execute('''
            SELECT
                superstition,
                COUNT(*) as total,
                SUM(CASE WHEN outcome = "fortune"    THEN 1 ELSE 0 END) as fortunes,
                SUM(CASE WHEN outcome = "misfortune" THEN 1 ELSE 0 END) as misfortunes
            FROM interactions
            GROUP BY superstition
            ORDER BY total DESC
        ''')

        breakdown = []
        for row in c.fetchall():
            total = row['total']
            breakdown.append({
                'superstition':  row['superstition'],
                'total':         total,
                'fortunes':      row['fortunes'],
                'misfortunes':   row['misfortunes'],
                'fortune_rate':  round(row['fortunes'] / total * 100, 1) if total > 0 else 0
            })

        # average luck score across all sessions
        c.execute('SELECT AVG(total_luck) as avg FROM sessions')
        avg_result = c.fetchone()['avg']
        avg_luck   = round(avg_result, 2) if avg_result is not None else 0

        conn.close()

        json_response(self, {
            'total_interactions':    total_interactions,
            'total_users':           total_users,
            'average_luck':          avg_luck,
            'superstition_breakdown': breakdown
        })


    def handle_history(self, session_id):
        if not session_id:
            error_response(self, 'missing session_id')
            return

        conn = get_db()
        c    = conn.cursor()
        c.execute('''
            SELECT superstition, outcome, luck_change, timestamp
            FROM interactions
            WHERE session_id = ?
            ORDER BY timestamp DESC
        ''', (session_id,))

        history = [dict(row) for row in c.fetchall()]
        conn.close()

        json_response(self, {'history': history, 'session_id': session_id})


# run the server

if __name__ == '__main__':
    # create the database if it doesn't exist yet ??
    init_db()

    port   = 5000
    server = HTTPServer(('localhost', port), FolkloreHandler)

    print()
    print('  translation machine — backend running')
    print(f'  http://localhost:{port}')
    print()
    print('  endpoints:')
    print(f'    GET  http://localhost:{port}/api/stats')
    print(f'    GET  http://localhost:{port}/api/luck?session_id=xxx')
    print(f'    GET  http://localhost:{port}/api/history?session_id=xxx')
    print(f'    POST http://localhost:{port}/api/record')
    print()
    print('  press ctrl+c to stop')
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  server stopped.')
        server.server_close()