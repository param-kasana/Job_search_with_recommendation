// Function to retrieve and display recommended categories
function recommendCategories() {
    // Retrieve input values
    var title = document.getElementById("title").value.trim();
    var description = document.getElementById("description").value.trim();
    // Containers for recommended and other categories
    var recommendedCategoriesContainer = document.getElementById("recommended-categories");
    var otherCategoriesContainer = document.getElementById("other-categories");
    var customCategoryInput = document.getElementById("new-category");
    
    // Clear existing category options
    recommendedCategoriesContainer.innerHTML = "";
    otherCategoriesContainer.innerHTML = "";

    // Check if both Title and Description fields are filled
    if (title !== "" && description !== "") {
        // Show the container for displaying recommendations
        document.getElementById("category-recommendations").style.display = "block";
        document.getElementById("other-categories-container").style.display = "block";
        document.getElementById("custom-category-container").style.display = "block";
        
        // Make an AJAX request to Flask to get category recommendations
        fetch('/recommend_category', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title: title, description: description }) // Send title and description as JSON
        })
        .then(response => response.json()) // Parse JSON response
        .then(data => {
            var recommendations = data.recommended_categories; // Get recommended categories
            var categoriesData = data.categories; // Get all categories
            
            // Populate recommended categories
            recommendations.forEach(function(category) {
                var listItem = document.createElement("div"); // Create a div for each recommended category
                listItem.className = "category";
                listItem.innerHTML = `<input type="radio" id="${category}" name="selectedCategory" value="${category}" class="category-radio">
                                    <label for="${category}">${category}</label>`;
                recommendedCategoriesContainer.appendChild(listItem); // Add the category to the container
            });

            // Populate other categories
            categoriesData.forEach(function(category) {
                // Check if the category is not in recommendations
                if (!recommendations.includes(category)) {
                    var listItem = document.createElement("div"); // Create a div for each other category
                    listItem.className = "category";
                    listItem.innerHTML = `<input type="radio" id="${category}" name="selectedCategory" value="${category}" class="category-radio">
                                        <label for="${category}">${category}</label>`; 
                    otherCategoriesContainer.appendChild(listItem); // Add the category to the container
                }
            });

            // Enable the custom category input
            customCategoryInput.disabled = false;
        })
        .catch(error => {
            console.error('Error:', error); // Log any errors
        });
    } else {
        // Hide the container if either Title or Description is empty
        document.getElementById("category-recommendations").style.display = "none";
        document.getElementById("other-categories-container").style.display = "none";
        document.getElementById("custom-category-container").style.display = "none";
    }
}

// Function to handle switching between radio buttons and custom input
function handleCategorySelection() {
    var customCategoryInput = document.getElementById("new-category");
    var categoryRadios = document.querySelectorAll('.category-radio');
    
    if (customCategoryInput.value.trim() !== "") {
        // Disable radio buttons
        categoryRadios.forEach(function(radio) {
            radio.disabled = true;
        });
    } else {
        // Enable radio buttons
        categoryRadios.forEach(function(radio) {
            radio.disabled = false;
        });
    }
}

// Helper function to check fields and trigger recommendation
function checkAndRecommend() {
    var title = document.getElementById("title").value.trim();
    var description = document.getElementById("description").value.trim();
    if (title !== "" && description !== "") {
        recommendCategories();
    }
}

document.addEventListener("DOMContentLoaded", function() {
    // Add event listeners for blur events
    var titleField = document.getElementById("title");
    var descriptionField = document.getElementById("description");

    titleField.addEventListener("blur", checkAndRecommend); // Trigger checkAndRecommend on title field blur
    descriptionField.addEventListener("blur", checkAndRecommend); // Trigger checkAndRecommend on description field blur

    // Add event listener for custom category input
    var customCategoryInput = document.getElementById("new-category");
    customCategoryInput.addEventListener("input", handleCategorySelection); // Trigger handleCategorySelection on custom category input
});
