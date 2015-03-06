# google-analytics-api-wrapper
=======
The Goolge Analytics wrapper is a convenient tool to extract data from GA via API. It is especially useful when the user has many GA profiles / web properties.

### Installation
    
    pip install google-api-python-client pandas
    python setup.py install
    
### Usage
    
```python
from analytics_query import analytics_query as aq

df = aq.get_api_query(start_date='7 days ago',
                 end_date='yesterday',
                 metrics='ga:date',
                 dimensions='ga:sessions')

df.head()
```