# google-analytics-api-wrapper
=======
The Goolge Analytics wrapper is a convenient tool to extract data from GA via API. It is especially useful when the user has many GA profiles / web properties.

### Installation

```
$ pip install google-api-python-client pandas
$ python setup.py install
```
    
### Usage

##### Authorize

Please go to https://console.developers.google.com to start an API project. Make sure you have enabled analytics API. 

Create a new OAuth client ID and download it to your working directory. 

Authorize your access to the API.
 
```python
from analytics_query import analytics_query as aq

aq.authorize()
```

Then authorize the app with your Google account that can access your GA account. 

The console will then store your refresh token and access token in the file called "analytics.dat" in the working directory. 

Now you can make the API call.
 
##### Query GA

The get_api_query method will take the parameters to fetch data from GA API and return as a pandas DataFrame. 

```python
from analytics_query import analytics_query as aq

df = aq.get_api_query(start_date='7 days ago',
                 end_date='yesterday',
                 metrics='ga:date',
                 dimensions='ga:sessions')

df.head()
```