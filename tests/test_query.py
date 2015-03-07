#!/usr/bin/python
# -*- coding: utf-8 -*-
import unittest
from datetime import datetime, timedelta

from analytics_query import analytics_query as aq

START_DATE = (datetime.now() - timedelta(7)).strftime('%Y-%m-%d')
END_DATE = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')


class TestBasicQuery(unittest.TestCase):
    def setUp(self):
        self.df = aq.get_api_query(
            start_date=START_DATE,
            end_date=END_DATE,
            dimensions='date,dateHour',
            metrics='sessions',
        )

    def test_query(self):
        for col in ['date', 'dateHour', 'sessions']:
            self.assertIn(col, self.df.columns)


class TestUtils(unittest.TestCase):
    def test_unify(self):
        dim = 'date'
        self.assertEqual('ga:date', aq.unify(dim))

        dim = ['date', 'ga:dateHour']
        self.assertEqual('ga:date,ga:dateHour', aq.unify(dim))


if __name__ == '__main__':
    unittest.main()