#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from datetime import datetime, timedelta

from analytics_query import analytics_query as aq

START_DATE = (datetime.now() - timedelta(7)).strftime('%Y-%m-%d')
END_DATE = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

start_date = '2015-03-03'
end_date = '2015-03-05'


def main():
    df = aq.get_api_query(
        start_date=start_date,
        end_date=end_date,
        dimensions='ga:transactionId,ga:date,ga:dateHour,ga:campaign,ga:source,ga:hostname',
        metrics='ga:transactionRevenue,ga:itemRevenue,ga:itemQuantity,ga:transactions',
        oldest_prf=True,
    )

    print df.head()


if __name__ == '__main__':
    main()
