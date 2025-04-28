from flask import render_template

def page_not_found(e):
    code = 404
    return render_template('error.html', code=code, message=e), code

def internal_server_error(e):
    code = 500
    return render_template('error.html', code=code, message=e), code