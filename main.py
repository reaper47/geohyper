from flask import Flask, render_template, request, jsonify
from geoip import lookup

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/lookup/<ip>', methods=['POST'])
def get_ip_info(ip):
    return jsonify(lookup(ip))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=1)
