import streamlit as st
from google.cloud import bigquery
import requests
import math

st.set_page_config(layout="wide")

# Connecting to BigQuery
client = bigquery.Client(project="assignment1hugopierazzi")

# Direct URL to background image
background_image_url = "https://i.imgur.com/6Zwwzx6.png"

# CSS for design
background_style = f"""
<style>
.stApp {{
    background-image: url("{background_image_url}");
    background-size: cover;
}}
/* Adjusts the style of the input for the search bar */
.stTextInput>div>div>input {{
    font-size: 1.1em;
    height: 3em;
    color: black;
    background-color: white;
}}
/* Style for placeholder in dark grey */
.stTextInput>div>div>input::placeholder {{
    color: darkgray;
}}
/* CSS to adjust the search bar margins */
.stTextInput {{
    margin-left: auto;
    margin-right: auto;
    width: 65%;
}}
/* CSS to centre the title */
h1 {{
    text-align: center;
}}
</style>
"""

st.markdown(background_style, unsafe_allow_html=True)

# Application title
st.title("Movie Search App")

# Main search entry
search_query = st.text_input("", placeholder="Enter a Film Name", key="movie_search")


# Use of st.session_state to manage the display of filters
if 'show_filters' not in st.session_state:
    st.session_state.show_filters = False

# Button to display filters
if st.button("Filter your criteria"):
    st.session_state.show_filters = not st.session_state.show_filters

if st.session_state.show_filters:
    # Filters visible only after clicking on "Filter your criteria".
    language = st.selectbox("Language", ['Any', 'en', 'fr', 'de', 'es', 'it', 'ja'])
    genre = st.selectbox("Genre", ['Any', 'Adventure', 'Comedy', 'Romance', 'Drama', 'Action'])
    rating_threshold = st.slider("Minimum average rating", 0.0, 5.0, 0.0)
    release_year = st.number_input("Released after year", min_value=1900, max_value=2024, value=1900)
else:
    # Default initialization of filters
    language = 'Any'
    genre = 'Any'
    rating_threshold = 0.0
    release_year = 1900


# API key TMDb
tmdb_api_key = '5ac7174f7f43bf4a0a3eafdb0b353b76'

# Function for obtaining details of a film from TMDb
def get_movie_details(tmdb_id):
    # Film details
    movie_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={tmdb_api_key}&language=en-US"
    movie_response = requests.get(movie_url)
    movie_details = movie_response.json() if movie_response.status_code == 200 else None

    # Casting of the film
    credits_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits?api_key={tmdb_api_key}&language=en-US"
    credits_response = requests.get(credits_url)
    credits_details = credits_response.json() if credits_response.status_code == 200 else None

    return movie_details, credits_details


def get_poster_path(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={tmdb_api_key}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return f"https://image.tmdb.org/t/p/w500{data['poster_path']}" if 'poster_path' in data else None
    return None


# Ensures initialization of movies_found and page_actual in st.session_state
if 'movies_found' not in st.session_state:
    st.session_state.movies_found = []
if 'page_actuelle' not in st.session_state:
    st.session_state.page_actuelle = 0

FILMS_PAR_PAGE = 24  # Number of films to be displayed per page

DETAILS_KEY = "film_details_id"
if 'show_details' not in st.session_state:
    st.session_state.show_details = False
if 'details_data' not in st.session_state:
    st.session_state.details_data = None


# Search button
if st.button("Search"):
    # Building SQL queries with filters
    where_clauses = ["TRUE"]  
    if search_query:
        where_clauses.append(f"LOWER(title) LIKE LOWER('%{search_query}%')")
    if language != 'Any':
        where_clauses.append(f"language = '{language}'")
    if genre != 'Any':
        where_clauses.append(f"genres LIKE '%{genre}%'")
    if release_year:
        where_clauses.append(f"release_year > {release_year}")

    where_statement = " AND ".join(where_clauses)

    query = f"""
        SELECT m.title, m.genres, m.release_year, AVG(r.rating) as avg_rating, m.tmdbId
        FROM `assignment1hugopierazzi.assignment1.movies` m
        LEFT JOIN `assignment1hugopierazzi.assignment1.ratings` r ON m.movieId = r.movieId
        WHERE {where_statement}
        GROUP BY m.title, m.genres, m.release_year, m.tmdbId
        HAVING AVG(r.rating) > {rating_threshold}
        ORDER BY avg_rating DESC
    """
    query_job = client.query(query)  # Executes the request

    # Retrieve the results and store them in st.session_state
    st.session_state.movies_found = [(row.title, row.tmdbId) for row in query_job]

    # Indicates to the user that the search has been completed
    st.write(f"Found {len(st.session_state.movies_found)} movies matching your criteria.")

    st.session_state.page_actuelle = 0

    # Resets the details displayed when a new search is performed
    st.session_state[DETAILS_KEY] = None

    st.session_state.show_details = False  # Ensures that details are not displayed after a new search



# Conditional display of film details
if st.session_state.show_details and st.session_state.details_data:
    with st.container():
        movie_details, credits_details = st.session_state.details_data
        if movie_details:
        # Displays details in a separate container
            with st.container():
                st.write(f"### {movie_details['title']}")
                st.image(f"https://image.tmdb.org/t/p/w500{movie_details['poster_path']}", width=300)
                st.write(f"**Overview**: {movie_details['overview']}")
                if credits_details and 'cast' in credits_details:
                    cast_names = [cast_member['name'] for cast_member in credits_details['cast'][:5]]
                    st.write(f"**Casting**: {', '.join(cast_names)}")
                # Button to close the details of the selected film and return to the search results
                if st.button("Close details"):
                    st.session_state.show_details = False
                    st.session_state.details_data = None



# Ensures that films_page_actual is calculated before attempting to display it
if st.session_state.movies_found:
    nombre_total_pages = math.ceil(len(st.session_state.movies_found) / FILMS_PAR_PAGE)
    start_index = st.session_state.page_actuelle * FILMS_PAR_PAGE
    end_index = start_index + FILMS_PAR_PAGE
    films_page_actuelle = st.session_state.movies_found[start_index:end_index] 

    # Uses st.columns to organise and display the films on the current page
    cols = st.columns(6)
    for index, (title, tmdb_id) in enumerate(films_page_actuelle):
        col = cols[index % 6]
        poster_path = get_poster_path(tmdb_id)
        if poster_path:
            col.image(poster_path, width=150)
            if col.button("View details", key=f"details_{index}_{tmdb_id}"):
                # Update session status instead of displaying it directly
                st.session_state.show_details = True
                st.session_state.details_data = get_movie_details(tmdb_id)



# Pagination
# Calculating the total number of pages
nombre_total_pages = math.ceil(len(st.session_state.movies_found) / FILMS_PAR_PAGE)

# Display pagination buttons if necessary
if nombre_total_pages > 1:
    col1, col2 = st.columns(2)

    # Previous page button
    if col1.button('Previous'):
        if st.session_state.page_actuelle > 0:
            st.session_state.page_actuelle -= 1

    # Next page button
    if col2.button('Next'):
        if st.session_state.page_actuelle < nombre_total_pages - 1:
            st.session_state.page_actuelle += 1

    # Displays the current page number
    st.write(f"Page {st.session_state.page_actuelle + 1} sur {nombre_total_pages}")


