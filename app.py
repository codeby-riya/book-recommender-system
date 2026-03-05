from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np

popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

app = Flask(__name__)

# ---------------- HOME PAGE ----------------

@app.route('/')
def index():
    return render_template(
        'index.html',
        book_name=list(popular_df['Book-Title'].values),
        author=list(popular_df['Book-Author'].values),
        image=list(popular_df['Image-URL-M'].values),
        votes=list(popular_df['num_ratings'].values),
        rating=list(popular_df['avg_rating'].values)
    )


# ---------------- RECOMMEND PAGE ----------------

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


# ---------------- RECOMMEND BOOKS ----------------

@app.route('/recommend_books', methods=['POST'])
def recommend():

    user_input = request.form.get('user_input')

    # check if book exists in pivot table
    if user_input not in pt.index:
        return render_template(
            'recommend.html',
            data=None,
            error="Book not found in recommendation system"
        )

    index = np.where(pt.index == user_input)[0][0]

    similar_items = sorted(
        list(enumerate(similarity_scores[index])),
        key=lambda x: x[1],
        reverse=True
    )[1:5]

    data = []

    for i in similar_items:

        temp_df = books[books['Book-Title'] == pt.index[i[0]]]

        item = []

        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))

        data.append(item)

    return render_template('recommend.html', data=data)


# ---------------- AUTOCOMPLETE API ----------------

@app.route('/autocomplete', methods=['GET'])
def autocomplete():

    query = request.args.get('q')

    suggestions = []

    if query:
        for book in pt.index:
            if query.lower() in book.lower():
                suggestions.append(book)

            if len(suggestions) >= 10:
                break

    return jsonify(suggestions)


# ---------------- RUN SERVER ----------------

if __name__ == '__main__':
    app.run(debug=True)