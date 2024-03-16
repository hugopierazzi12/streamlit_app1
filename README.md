# Cloud & Advanced Analytics 2024 - Assignment 1

## Objective

The goal of this assignment is to implement a simple interface that interacts with a BigQuery cloud database. The application runs on Google Cloud and allows querying a movie database with various search functionalities.

## Deployment

The application is deployed on Google Cloud Run and can be accessed at the following URL: [Link to my application](https://my-streamlit-app-sxemxtbyeq-oa.a.run.app)

![Image Description](https://i.imgur.com/FvwQ5IX.png)

## Features

The web application enables:

- Autocomplete functionality to help explore movie titles based on typed input.
- Filters by language, movie genre, average rating, and release year.
- Displaying search results with additional details if a movie is selected, including the movie's cover and more information such as an overview and the cast, utilizing OpenMovieDatabase or The Movie Database.

## Technologies Used

- **BigQuery**: For storing and querying the movie database.
- **SQL**: For executing advanced queries in BigQuery.
- **Docker**: For containerizing the Streamlit application.
- **Google Cloud**: For hosting the containerized application.
- **Streamlit**: For creating the user interface.


## Getting Started

To run the application locally, follow these steps:

1. Clone the repository:
