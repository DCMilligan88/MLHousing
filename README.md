# Portland Housing Cost Estimator

## How much is too much?
Buying a house is a huge investment in time, money, and energy. Consumer needs and desires for their property vary widely, as do their budgets. But even if one can find a home that fits ones needs, how can one know they are getting a good deal? We attempt a programmatic approach to this problem. Our final product is an interactive application that allows a user to input desired specifications for a Portland home. Using a machine learning model, a price range for such a property is returned.

## Step 1: Web Scraping
Data on individual housing listings was scraped from [Portland MLS Search](https://www.portlandmlsdirect.com/). Information scraped includes the address of property, the price of the listing, the classification of the type of home, the number of bedrooms, the number of bathrooms, square footage of the home, the year the home was built, the size of the lot the home occupies, the neighborhood the home is located in, the county the home is located in, the city the home is located in, the zipcode the home is located in, the local elementary school, the local middle school, and the local high school. Not every listing contains all of this information, so a number of listings have blank or unknown entries following the scraping. The scraping was also limited to the Portland area to ensure a somewhat homogeneous data set. The scraped data was then saved as a .csv file for further processing.

## Step 2: Data Storage
Using the .csv of scraped data, a sqlite database was created and the. .csv imported as a single table. This data can be accessed in json format using an [API route]("<home url>/housingDataAPI/v1.0/listings"). Currently there is only one API route available that allows users to pull in all the information in the database as a single return that can then be processed as the user sees fit. This API is then accessed to build and train a machine learning model.

## Step 3: Data Preprocessing
After some trial and error it was decided the variables that would be used to train the predictive model would be number of bathrooms, number of bedrooms, year built, lot size, square footage, school district, and zipcode. Many properties, specifically condominiums and floating homes, lacked a lot size entry. For properties such as these a lot size of 0 was input. School district is not specifically listed on the web pages scraped. Using the local high school for each listing a list of districts present in the database was generated and this information added to the data frame used to train the predictive model. The price for each listing was put into one of five equally sized bins (that is, each bin contains roughly the same number of listings).

## Step 4: Model Creation and Training
The original aim was to create a predictive model that would return a price for a property given user input that would approximate the price offered for similar properties in the database. Different types of linear regression were used as proof of concept for this, and to identify those variables in the data set that had the most impact on the price of a given listing. These linear models generally performed quite poorly when tested, so a more complex MLP regression was tried. Though a noticable improvement over linear regression, generally poor performance metrics led to a fundamental change in approach. Rather than return a single predicted price, we would seek to construct a classification model that would place a hypothetical listing with user input values into a price range.

After some initial experiments, it was decided to use five bins of approximately equal size in number of listings. Five bins was a compromise between detail of the returned prediction and accuracy of the model. Bins of approximately equal number of listings were used to prevent the majority of listings from being conentrated in a single bin biasing the model toward predicting inputs would be placed in more populated bins. The drawback of this approach is that the model provides far greater detail for properties predicted to be in lower price ranges, as the intervals of these bins are considerably smaller than at higher price ranges.

All input data for the model was scaled and a random forest classifier was used to help determine what variables to use as inputs. For categorical variables such as school district and zip code it was found that rather than creating dummy 0 - 1 variables for different possible values, a numerical ranking in terms of mean price of listings in that category significantly simplified data input with minimal loss in performance. Experimentation found that using a sequential deep learning model, an accuracy of approximately 70% was achievable.

## Step 5: User Interface
A web page was created to be rendered by a Flask app that would accept user input in various fields, load the model, and return the predicted price range. Default values are used in place of user input if the values input by the user are not usable by the model. To assist users in input, a list of possible categories for zip code and school district are provided, and the input used by the model is displayed. It was decided to take this approach rather than used dropdown menus for inputs for ease of Flask reading the data from the web page.

## Going Further
Some possible future directions to take the project include:

* Reformatting scraping scripts to input information directly into the sqlite database, bypassing the .csv file step.

* Reorganizing the information in the database for more efficient storage.

* Adding additional API routes to allow users to pull more specific data.

* Aquiring additional data that may improve the accuracy of the model.

* Adjusting the user interface to make the application easier to use.

## If you would like to know more about our process please take a look at our power point.
(Machine Learning In the Housing Market.pptx)

### Tristan Holmes, Daniel Love, and Devin Milligan
