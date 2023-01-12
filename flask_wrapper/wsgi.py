from flask_wrapper import create_app
from flask_login import login_required
from flask import render_template

app = create_app()

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)