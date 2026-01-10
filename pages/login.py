import dash
from dash import html, dcc, callback, Input, Output, State
import sqlite3

dash.register_page(__name__, path="/login")
# Open a connection to the database users.db
def get_db():
    return sqlite3.connect("users.db", check_same_thread=False)

layout = html.Div([
    # Title and image logo
    html.Img(src="/assets/NAVICARGO.png",
                 style={"height": "20px", "margin-right": "5px"}),
        html.Div("NaviCargo", style={"position": "absolute", "top": "10px", "left": "30px", "font-size": "15px", "font-weight": 550,
                                     "color": "#8b8b8b"}),
        html.Div("Login/ Sign Up", style={"position": "absolute", "top": "10px", "right": "12px", "font-size": "9px",
                                  "font-weight": 450, "color": "#8b8b8b"}),
    html.Div([
    # Invisible box which can be used to display error messages such as invalid credentials
    html.Div(id="login-message", style={"marginTop": "10px", "color": "red"}),
    # Input for email. By using type="email", the browser automatically performs validation
    dcc.Input(id="email", placeholder="Email", type="email", style={"width": "100%", "marginBottom": "10px"}),
    # Input for password
    dcc.Input(id="password", placeholder="Password", type="password", style={"width": "100%", "marginBottom": "10px"}),
    # Button to login
    html.Button("Login", id="login-btn", style={"width": "100%", "marginBottom": "10px", "font-size": "20px", "background-color": "#2c2c2c",
                                                "color": "white", "border": "none", "border-radius": "5px", "cursor": "pointer"}),
    # Button to sign up
    html.Button("Sign Up", id="signup-btn", style={"width":"100%","marginBottom": "10px", "font-size":"20px", "background-color": "#0474ce",
                                                   "color": "white", "border": "none", "border-radius": "5px", "cursor": "pointer"}),
    # Invisible box in which a login messages could be displayed
    html.Div(id="login-message2", style={"marginTop": "10px"}),
    # Link to go back to live map
    html.A("⬅ Back to Live Map", href="/", style={"font-weight": "bold", "font-size": "16px"})],
        style={"width": "300px", "margin": "auto", "marginTop": "120px"}),])

@callback(
    Output("login-message", "children"),
    Output("login-message2", "children"),
    Output("auth-store", "data"),
    Input("login-btn", "n_clicks"),
    Input("signup-btn", "n_clicks"),
    State("email", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def authenticate(login_clicks, signup_clicks, email, password):

    # If neither button was clicked then stop the callback
    if login_clicks is None and signup_clicks is None:
        raise dash.exceptions.PreventUpdate

    if dash.ctx.triggered_id == "signup-btn" or dash.ctx.triggered_id == "login-btn":
        # Verifies that email and password was inputted
        if not email or not password:
            return "Missing email or password", "", None
    # Opens a connection to users.db
    conn = get_db()
    # The cursor is used to execute SQL commands
    cursor = conn.cursor()
    # Create a new table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            email TEXT PRIMARY KEY,
            password TEXT
        )
    """)

    # SIGN UP
    if dash.ctx.triggered_id == "signup-btn":   # Checks which button triggered the callback
        try:
            # Insert new record into the database if the signup button was clicked
            cursor.execute(
                "INSERT INTO users VALUES (?, ?)",
                (email, password)
            )
            conn.commit()
            conn.close()
            # Display a message and route back to the main page
            return "", "Account created. Logged in.", {"email": email}
        # If the user already exists, the function catches this and displays and appropriate message
        except sqlite3.IntegrityError:
            conn.close()
            return "User already exists", "", None

    # LOGIN
    # Returns records from the database where the provided email and password combination exists
    cursor.execute(
        "SELECT * FROM users WHERE email=? AND password=?",
        (email, password)
    )
    # Returns a row from the result of the previous SQL query (returns None if no record was found)
    user = cursor.fetchone()
    conn.close()

    # If the record exists, the login is successful (display appropriate message and go back to the main page)
    if user:
        return "", "Login successful", {"email": email}
    # Returns appropriate message if email or password is wrong and stays on the login page
    return "Invalid credentials", "", None

