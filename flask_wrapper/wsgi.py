# import flask_wrapper as wrapper
from flask_wrapper import create_app
from flask_login import login_required
from flask import render_template, send_from_directory, request

app = create_app()


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.errorhandler(403)
def page_not_found(e):
    return render_template('403.html')


@app.route('/robots.txt')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])


if __name__ == '__main__':
    app.run(port=8080, debug=False)