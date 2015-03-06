from distutils.core import setup

setup(
    name='google-analytics-api-wrapper',
    version='0.1.0',
    dependencies=['google-api-python-client', 'pandas'],
    url='https://github.com/tikazyq/google-analytics-api-wrapper',
    license='MIT',
    author='Yeqing.Zhang',
    author_email='tikazyq@gmail.com',
    description='The Goolge Analytics wrapper is a convenient tool to extract data from GA via API. It is especially '
                'useful when the user has many GA profiles / web properties.'
)
