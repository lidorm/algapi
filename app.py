import threading

from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from database_connection import create_user_from_web_input, normalaize_vector_with_stats, get_user_by_id, \
    get_best_matches_for_user, calculate_matches_and_update

app = Flask(__name__)
CORS(app)
app.config["DEBUG"] = False


@app.route('/getuser', methods=['POST'])
def get_matches_for_new_user():
    _build_cors_prelight_response()
    user_vector_dict = {}
    request_json = request.get_json()
    u_id = request_json.get("userid")
    user_answer_dict = request_json.get("myAnswers")

    for item in user_answer_dict:
        user_vector_dict[item.get('id')] = item.get('answer')

    print(user_vector_dict)
    vector = normalaize_vector_with_stats(user_vector_dict)
    create_user_from_web_input(u_id, vector)
    return jsonify({}, 200)


@app.route('/getbyid', methods=['GET'])
def get_matches_by_id():
    _build_cors_prelight_response()
    matches = []
    u_id = request.args.get('userId')
    user_by_id = get_user_by_id(u_id)
    user_matches_dict = get_best_matches_for_user(user_by_id)
    for user in user_matches_dict:
        matches.append(user)
    return jsonify(matches)


def _build_cors_prelight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response


@app.route('/')
def index():
    return "<h1>Server is running...</h1>"


if __name__ == '__main__':
    threading.Timer(21600.0, calculate_matches_and_update).start()
    app.run(port=5000)


