from dash import dcc, html, Dash
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    html.H1('Hello Dash'),
    html.Div('Dash: A web application framework for Python.'),
    ])

if __name__ == '__main__':
    # app.run_server(debug=True)
    server.run(debug=True, port=8080, host='0.0.0.0')