from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
from datetime import datetime
from math import ceil
from nltk.stem import PorterStemmer
from nltk import RegexpTokenizer
import json
import joblib

app = Flask(__name__, static_folder='static')

# Path to the job CSV file
DATA = 'data/jobs.csv'

# Load the trained CountVectorizer
loaded_count_vectorizer = joblib.load('models/count_vectorizer_model.pkl')

# Load the trained Random Forest Classifier
loaded_rf_classifier = joblib.load('models/random_forest_classifier.pkl')

# Initialise PorterStemmer
stemmer = PorterStemmer()

# Function to load job data from the CSV
def load_jobs():
    """
    Load job data from the CSV file and preprocesses it.
    - Reads the CSV file.
    - Replaces NaN values with "Not specified".
    - Returns the job data as a list of dictionaries.
    """
    df = pd.read_csv(DATA)
    df= df.fillna("Not specified")

    return df.to_dict(orient='records')

# Function to save job data to the CSV
def save_jobs(jobs):
    """
    Save job data to the CSV file.
    - Converts the job data from a list of dictionaries to a DataFrame.
    - Writes the DataFrame to the CSV file.
    """
    df = pd.DataFrame(jobs)
    df.to_csv(DATA, index=False)

# Function to get top jobs
def get_top_jobs(jobs):
    """
    Get the top 10 highest paying jobs and the top 10 most recent jobs.
    """
    # Convert list of dictionaries to DataFrame
    df = pd.DataFrame(jobs)
    df['Salary'] = df['Salary'].replace('[\$,\/year]', '', regex=True).astype(float)
    df['Post_Date'] = pd.to_datetime(df['Post_Date'], format='%d/%m/%Y')
    
    # Sort by 'Salary' descending and 'Post_Date' descending
    df_sorted_salary = df.sort_values(by='Salary', ascending=False)
    df_sorted_date = df.sort_values(by='Post_Date', ascending=False)

    # Get top 10 jobs by salary
    top_salary_jobs = df_sorted_salary.head(10)
    # Get top 10 recent jobs by post date
    top_recent_jobs = df_sorted_date.head(10)

    # Convert Post_Date back to dd/mm/yyyy format
    top_salary_jobs['Post_Date'] = top_salary_jobs['Post_Date'].dt.strftime('%d/%m/%Y')
    top_recent_jobs['Post_Date'] = top_recent_jobs['Post_Date'].dt.strftime('%d/%m/%Y')

    # Convert back to list of dictionaries
    top_salary_jobs = top_salary_jobs.to_dict(orient='records')
    top_recent_jobs = top_recent_jobs.to_dict(orient='records')

    return top_salary_jobs, top_recent_jobs

@app.route('/')
def index():
    """
    Route for the home page.
    - Loads all jobs and retrieves unique categories.
    - Gets the top 10 highest paying jobs and the top 10 most recent jobs.
    - Renders the home page with categories, highest paying jobs and recent jobs.
    """
    # Load all jobs
    jobs = load_jobs()

    # Get a unique set of categories from the existing jobs
    categories = set(job['Category'] for job in jobs)

    # Get the top 10 highest paying jobs and the top 10 most recent jobs
    highest_paying, recent = get_top_jobs(jobs)

    # Render the index.html template with categories, highest paying jobs, and recent jobs
    return render_template('index.html', categories=categories, highest_paying=highest_paying, recent=recent)


@app.context_processor
def inject_globals():
    """
    Injects global functions into the Jinja2 template context.
    This allows using the `max` and `min` functions directly in templates.
    """
    return dict(max=max, min=min)

@app.route('/search', methods=['GET'])
def search_jobs():
    """
    Route for searching jobs based on keyword and category.
    - Retrieves search parameters from the request.
    - Filters jobs by keyword and category.
    - Returns the filtered job data with pagination.
    """
    # Get search parameters from the request
    keyword = request.args.get('keyword', '').lower().strip()
    category = request.args.get('category', 'all categories').lower().strip()
    page = int(request.args.get('page', 1))
    per_page = 20

    # Stem the keyword using Porter Stemmer
    stemmed_keyword = stemmer.stem(keyword)

    # Load all jobs
    jobs = load_jobs()
    filtered_jobs = []

    if category == 'all categories':
        # Search in the whole dataset
        for job in jobs:
            job_info = (job['Category'] + job['Title'] + job['Description']).lower()
            # Stem the job info and check for stemmed keyword
            if stemmed_keyword in stemmer.stem(job_info):
                filtered_jobs.append(job)
    else:
        # Search in a specific category
        for job in jobs:
            if job['Category'].lower() == category:
                job_info = (job['Title'] + job['Description']).lower()
                # Stem the job info and check for stemmed keyword
                if stemmed_keyword in stemmer.stem(job_info):
                    filtered_jobs.append(job)

    # Calculate total jobs and total pages for pagination
    total_jobs = len(filtered_jobs)
    total_pages = ceil(total_jobs / per_page)

    # Determine the start and end indices for the current page
    start = (page - 1) * per_page
    end = start + per_page
    paginated_jobs = filtered_jobs[start:end]

    # Render the job_list.html template with filtered jobs and pagination data
    return render_template('job_list.html', jobs=paginated_jobs, num_job=total_jobs, keyword=keyword, category=category, page=page, total_pages=total_pages)

@app.route('/job/<int:job_id>')
def job_detail(job_id):
    """
    Route for displaying details of a specific job.
    - Retrieves the job details based on the job_id from the URL.
    - Loads all jobs and searches for the job with the matching job_id.
    - Renders the job_detail.html template with the found job's details.
    """
    # Load all jobs
    jobs = load_jobs()
    
    # Find the job with the matching job_id
    job = next((job for job in jobs if job['Webindex'] == job_id), None)
    
    # Render the job_detail.html template with the found job's details
    return render_template('job_detail.html', job=job)

@app.route('/create', methods=['GET', 'POST'])
def create_job():
    """
    Route for creating a new job listing.
    - Handles both GET and POST requests.
    - On GET: Loads the existing jobs and displays the job creation form.
    - On POST: Processes the form data to create a new job listing and saves it.
    """
    # Load all jobs
    jobs = load_jobs()

    # Get unique categories from the existing jobs
    categories = list(set(job['Category'] for job in jobs))
    # Convert the list of categories to a JSON string for use in the template
    categories_json = json.dumps(categories)

    if request.method == 'POST':
        # Create a new job dictionary from the form data
        new_job = {
            "Webindex": max(job['Webindex'] for job in jobs) + 1,  # Assign a new unique Webindex
            "Category": request.form['selectedCategory'],
            "Title": request.form['title'],
            "Company": request.form['company'],
            "Description": request.form['description'],
            "Salary": f"${request.form['salary']}/year",
            "Post_Date": datetime.now().strftime('%d/%m/%Y')  # Set the current date as the post date
        }
        # Append the new job to the list of jobs
        jobs.append(new_job)
        # Save the updated job list to the CSV file
        save_jobs(jobs)

        # Access the 'Webindex' attribute from the 'new_job' dictionary
        webindex = new_job['Webindex']
        # Redirect to the job detail page for the newly created job
        return redirect(url_for('job_detail', job_id=webindex))
    
    # Render the create_job.html template with the categories data
    return render_template('create_job.html', categories=categories, categories_json=categories_json)

# Function to pre-process passed text
def preprocess(text):
    """
    Pre-process job title and description by tokenizing, stemming, and removing stopwords.
    -Returns the preprocessed text.
    """
    # Convert text to lowercase
    text = text.lower()

    # Tokenize each sentence
    pattern = r"[a-zA-Z]+(?:[-'][a-zA-Z]+)?"
    tokenizer = RegexpTokenizer(pattern) 
    
    # Merge them into a list of tokens
    tokens = tokenizer.tokenize(text) 
    
    # Load stopwords from file
    with open('static/stopwords_en.txt', 'r') as f:
        stopwords = set(f.read().splitlines())

    # Remove stopwords
    tokens = [token for token in tokens if token not in stopwords]

    # Join the tokens with space
    tokens = ' '.join(tokens)

    return tokens

# Function to recommend categories based on job title and description
def recommend_category(title, description):
    """
    Recommend categories based on job title and description.
    - Combines the title and description.
    - Preprocesses the combined text.
    - Uses the trained classifier to predict the category.
    - Returns the predicted category.
    """
    combined = title + " " + description

    combined_text =preprocess(combined)

    # Transform the new string using the loaded CountVectorizer
    new_string_count_vector = loaded_count_vectorizer.transform([combined_text])

    # Predict the category using the trained classifier
    prediction = loaded_rf_classifier.predict(new_string_count_vector)

    # Map the prediction to the appropriate category string
    if prediction == 'Accounting_Finance':
        prediction = 'Accounting & Finance'
    elif prediction == 'Healthcare_Nursing':
        prediction = 'Healthcare & Nursing'
    elif prediction == 'Sales':
        prediction = 'Sales'
    elif prediction == 'Engineering':
        prediction = 'Engineering'

    prediction = [prediction]

    return prediction

@app.route('/recommend_category', methods=['POST'])
def recommend_category_handler():
    """
    Route for handling category recommendation requests.
    - Retrieves job title and description from the request.
    - Recommends categories based on the title and description.
    - Returns the recommended categories and all available categories.
    """
    # Get the JSON data from the request
    data = request.json
    title = data.get('title')  # Extract the job title
    description = data.get('description')  # Extract the job description

    # Load all jobs
    jobs = load_jobs()
    # Get a unique list of categories from the existing jobs
    categories = list(set(job['Category'] for job in jobs))

    # Call the function to recommend categories based on the title and description
    recommended_categories = list(recommend_category(title, description))
    
    # Return the recommended categories and all available categories as JSON
    return jsonify({'recommended_categories': recommended_categories, 'categories': categories})
 
 
if __name__ == '__main__':
    # Start the Flask application.
    app.run(debug=True)