import firebase_admin
from firebase_admin import credentials, firestore, db
from scipy import spatial
from user import User

cred = credentials.Certificate('./ServiceAccountKey.json')
defualt_app = firebase_admin.initialize_app(cred, {
    "project_id": "testroommate-2f452",
})

db = firestore.client()


def switch_case_dict(x, y):
    return {
        'animal': {'1': 0.597, '2': 1.195, '0': 0},
        'smoke': {'1': 0.788, '2': 1.577, '0': 0},
        'host': {'1': 0.597, '2': 1.155, '0': 0},
        'gender': {'1': 0.326, '2': 0.653, '0': 0},
        'clean': {'1': 0.984, '2': 1.969, '0': 0},
        'shop': {'1': 0.648, '2': 1.296, '0': 0},
        'kosher': {'1': 0.276, '2': 0.552, '0': 0},
        'vegetarian': {'1': 0.1, '2': 0.201, '0': 0}
    }[x][y]


def normalaize_vector_with_stats(user_vector_dict):
    new_vector = {}
    for x, y in user_vector_dict.items():
        new_vector[x] = switch_case_dict(str(x), str(y))
    return new_vector


def create_user_from_web_input(user_id, vector):
    new_user = User(user_id=user_id, matches={}, user_vector_dict=sort_match_dict(vector))
    doc_ref = db.collection(u'users')
    doc = user_to_doc(new_user, {})
    doc_ref.document(str(new_user.user_id)).set(doc)
    calculate_matches_to_specific_user(new_user)
    return get_best_matches_for_user(new_user)


def user_to_doc(user, matches_dict):
    to_doc = {
        'user id': str(user.user_id),
        'user answers vector': user.user_vector,
        'matches': matches_dict,
    }
    return to_doc


def get_user_by_id(u_id):
    users_ref = db.collection(u'users')
    docs = users_ref.stream()

    for doc in docs:
        user_dict = doc.to_dict()
        user = User(user_id=user_dict.get('user id'), matches=user_dict.get(
            'matches'), user_vector_dict=sort_match_dict(user_dict.get('user answers vector')))
        if user_dict.get('user id') == u_id:
            return user


# Read data from users collection
def get_all_users():
    users_ref = db.collection(u'users')
    docs = users_ref.stream()
    users = []

    for doc in docs:
        user_dict = doc.to_dict()
        user = User(user_id=user_dict.get('user id'), matches=user_dict.get(
            'matches'), user_vector_dict=sort_match_dict(user_dict.get('user answers vector')))
        users.append(user)
    return users


def sort_match_dict(matches_dict):
    matches_dict = {k: v for k, v in sorted(matches_dict.items()
                                            , key=lambda item: item[1], reverse=True)}
    return matches_dict


def calculate_matches_old_with_new(new_user):
    users = get_all_users()
    users_ref = db.collection('users')
    for user in users:
        doc = users_ref.document(str(user.user_id))
        matches_dict = user.matches
        if (user.user_id != new_user.user_id):
            matches_dict[new_user.user_id] = "{:.3f}".format(1 - spatial.distance.cosine(user.convert_to_vector(),
                                                                                         new_user.
                                                                                         convert_to_vector()))
        doc.update({'matches': matches_dict})


def calculate_matches_and_update():
    users = get_all_users()
    users_ref = db.collection('users')

    for user1 in users:
        doc = users_ref.document(str(user1.user_id))
        matches_dict = {}
        for user2 in users:
            if (user1.user_id != user2.user_id):
                matches_dict[user2.user_id] = "{:.3f}".format(1 - spatial.distance.cosine(user1.convert_to_vector(),
                                                                                          user2.convert_to_vector()))
        doc.update({'matches': matches_dict})


def calculate_matches_to_specific_user(user):
    users_ref = db.collection('users')
    doc = users_ref.document(str(user.user_id))
    # old_match_dict = {}
    matches_dict = {}
    users_list = get_all_users()
    for u in users_list:
        # old_user_doc = users_ref.document(str(u.user_id))
        if (user.user_id != u.user_id):
            match = "{:.3f}".format(1 - spatial.distance.cosine(u.convert_to_vector(), user.
                                                                convert_to_vector()))
            matches_dict[u.user_id] = match
    doc.update({'matches': matches_dict})
    return matches_dict


# Return the best matches to specific user,  0.9 <= score
def get_best_matches_for_user(user):
    matches_dict = {}
    doc_ref = db.collection('users').document(str(user.user_id))
    doc = doc_ref.get()
    user_dict = doc.to_dict()
    user_ref_db = User(user_id=user_dict.get('user name'), matches=user_dict.get(
        'matches'), user_vector_dict=user_dict.get('user answers vector'))
    user_matches_sorted = sort_match_dict(user_ref_db.matches)
    if user_ref_db.check_zero_vector():
        user_matches = []
        users = get_all_users()
        for u in users:
            if u.user_id != user.user_id:
                user_matches.append(u.user_id)
            else:
                continue
        return user_matches

    for key, val in user_matches_sorted.items():
        if (float(val) > 0.90):
            matches_dict[key] = val

    return matches_dict


