
import pickle
import streamlit as st
import numpy as np

# Load users
try:
    with open('users.pkl', 'rb') as f:
        users = pickle.load(f)
except FileNotFoundError:
    users = {}

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = ''

def login(username, password):
    if username in users and users[username] == password:
        st.session_state.logged_in = True
        st.session_state.username = username
        st.success("Logged in successfully!")
        st.rerun()
    else:
        st.error("Invalid username or password")

def signup(username, password, confirm_password):
    if password != confirm_password:
        st.error("Passwords do not match")
        return
    if username in users:
        st.error("Username already exists")
        return
    users[username] = password
    with open('users.pkl', 'wb') as f:
        pickle.dump(users, f)
    st.session_state.logged_in = True
    st.session_state.username = username
    st.success("Account created and logged in successfully!")
    st.rerun()

def logout():
    st.session_state.logged_in = False
    st.session_state.username = ''
    st.rerun()

if not st.session_state.logged_in:
    st.title("Book Recommender System - Login/Signup")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    with tab1:
        st.header("Login")
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        if st.button("Login"):
            login(username, password)

    with tab2:
        st.header("Signup")
        username = st.text_input("Username", key="signup_username")
        password = st.text_input("Password", type="password", key="signup_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")
        if st.button("Signup"):
            signup(username, password, confirm_password)

else:
    # Set global font to serif
    st.markdown(
        """
        <style>
        body {
            font-family: serif;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Sidebar with project description and logout
    st.sidebar.title("About the Project")
    st.sidebar.write("""
    This is a Book Recommender System built using Machine Learning. It uses a collaborative filtering approach to recommend books based on user ratings.

    Features:
    - Select a book from the dropdown
    - Get personalized recommendations
    - View book posters and search on Google

    The system is trained on a dataset of book ratings and uses cosine similarity to find similar books.
    """)
    st.sidebar.write(f"Logged in as: {st.session_state.username}")
    if st.sidebar.button("Logout"):
        logout()

    st.title('Book Recommender System Using Machine Learning')
    model = pickle.load(open('model.pkl','rb'))
    book_names = pickle.load(open('book_names.pkl','rb'))
    final_rating = pickle.load(open('final_rating.pkl','rb'))
    book_pivot = pickle.load(open('book_pivot.pkl','rb'))


    def fetch_poster(suggestion):
        book_name = []
        ids_index = []
        poster_url = []

        for book_id in suggestion:
            book_name.append(book_pivot.index[book_id])

        for name in book_name[0]:
            ids = np.where(final_rating['title'] == name)[0][0]
            ids_index.append(ids)

        for idx in ids_index:
            url = final_rating.iloc[idx]['image_url']
            poster_url.append(url)

        return poster_url



    def recommend_book(book_name):
        books_list = []
        book_id = np.where(book_pivot.index == book_name)[0][0]
        _ , suggestion = model.kneighbors(book_pivot.iloc[book_id,:].values.reshape(1,-1), n_neighbors=6 )

        poster_url = fetch_poster(suggestion)

        for i in range(len(suggestion)):
                books = book_pivot.index[suggestion[i]]
                for j in books:
                    books_list.append(j)
        return books_list , poster_url


    selected_books = st.selectbox(
        "Select a book",book_names)

    if st.button('Show Recommendation'):
        recommended_books, poster_url = recommend_book(selected_books)

        st.subheader("Recommended Books")

        # Create a row of 5 columns
        cols = st.columns(5)

        for i, col in enumerate(cols):
            with col:
                # Generate Google search URL
                google_search_url = f"https://www.google.com/search?q={recommended_books[i+1].replace(' ', '+')} + book"

                st.markdown(
                    f"""
                    <div style="text-align: center; padding: 10px; border-radius: 10px; background-color: #f9f9f9; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);">
                        <a href="{google_search_url}" target="_blank">
                            <img src="{poster_url[i+1]}" width="120" style="border-radius: 8px; cursor: pointer;">
                        </a><br>
                            <p style="font-weight: bold; color: #333;">{recommended_books[i+1]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
