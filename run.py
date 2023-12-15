from bottle import run, request, static_file, post

from components.canvas import Canvas


@post('/cad')
def index():
    canvas = Canvas(request.json)
    canvas.draw()

    return static_file(canvas.filename, root='/', download=True)


run(host='0.0.0.0', port=5002, reloader=True)
