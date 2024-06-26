# JobQuest - The Job Search Website

This repository contains the code for a job search website developed using the Flask web framework. The website allows job seekers to browse existing job adverts and enables employers to create new job adverts. The key feature of this website is the recommendation of job categories for newly created job adverts, based on pre-trained machine learning models.

### How to Run the Application
1. Install the required dependencies from `requirements.txt` using pip.
2. Run the `app.py` Flask application.
3. Open your web browser and go to `http://localhost:5000` to access the job search website.

Note: Use Chrome for the best experience.

Additionally, ensure that the `jobs.csv` file containing job data in the appropriate format is present inside "data" folder for the application to load and display job listings.

## Functionality

### For Job Seekers

#### Job Search
- Users can effectively search for job listings based on keywords.
- The search algorithm supports searching keyword strings in similar forms to ensure comprehensive results.
- Job seekers receive a message indicating the number of matched job advertisements and a list of relevant job advert previews.
- Clicking on a job advert preview displays the full description of the job.

### For Employers

#### Create New Job Listing
- Employers can create new job listings by entering information such as title, description, salary, etc.
- Upon creating a new job advert, the website recommends a list of categories based on the job description (and/or job title).
- Employers have the flexibility to select other categories if the recommendation does not suit their preferences.
- The created job advert is included in the job data and is accessible via URL and relevant searches.

## Implementation Details

The main components of the website are explained below:

### `app.py`
- This file contains the main Flask application code.
- It defines routes for different functionalities such as displaying job listings, searching for jobs, creating new job listings, and recommending job categories.
- The `load_jobs()` function loads job data from a CSV file, preprocesses it, and returns a dictionary of job records.
- The `save_jobs()` function saves job data to the CSV file.
- `index()` route serves as the home page of the website and is mapped to the `/` URL endpoint. It also displays the top 10 highest paying jobs and the top 10 most recent jobs on the main page. This provides users with a quick view of the most lucrative and the latest job opportunities.
- Routes like `/search` handle job search functionalities, while routes like `/create` handle job creation functionalities.
- The `recommend_category()` function utilizes a pre-trained machine learning model trained on job data to recommend job categories based on job title and description.
  - For category recommendation, a trained classifier model `random_forest_classifier.pkl` and a CountVectorizer `count_vectorizer_model.pkl` are used.
  - AJAX requests are used to fetch category recommendations and update the user interface dynamically.
  - The job title and description are fetched from user side and are combined and pre-processed.
  - Pre-processing is done with the help of  `preprocess()` function which handles tokenizing, stemming, and removing stopwords.
  - The CountVectorizer transforms the processed text into numerical features.
  - The classifier model then predicts the job category based on these features.

### `base.html`,`index.html`, `job_list.html`, `job_detail.html`, `create_job.html`
- These HTML templates are used to render the user interface for different pages of the website.
- They utilize `Jinja2` templating to dynamically generate content based on the data received from the Flask routes.
- Pagination has been implemented for job listings, allowing users to navigate through the listings page by page.

### `recommendations.js`
This JavaScript file, `recommendations.js`, is used in `create_job.html` to handle category recommendation functionalities. It retrieves and displays recommended job categories based on user input (job title and description) through AJAX requests to the Flask server with the help of  `/recommend_category` route. It dynamically updates the user interface with recommendations and allows for custom category input.

### `style.css`
This file contains the styling rules for the job search website, ensuring a cohesive and responsive design. It includes styles for layout, typography, buttons, and navigation elements to enhance the user experience.

## Testing and Demonstration
To test and demonstrate the functionality of the website, job data including job information and descriptions from `jobs.csv` is utilized. The website facilitates efficient job searching and creation processes, ultimately enhancing the user experience for both job seekers and employers.

## Next Steps
Implementing a proper database can significantly improve the website's efficiency by managing and scaling job listings and user data more effectively, ensuring faster query processing and improved data integrity. Further improvements and enhancements can be made to the website, such as adding more details for the job, such as job requirements, qualifications, benefits, location, and application deadlines. Enhancing the search algorithm, adding filters while searching for jobs, refining the recommendation system, and optimizing the user interface for better usability and accessibility are also important steps. Additionally, integrating additional features such as user authentication, personalized job recommendations, and real-time notifications for job postings could enhance the overall user experience. Incorporating advanced analytics to track user behavior and preferences could also provide valuable insights for continuous improvement.
