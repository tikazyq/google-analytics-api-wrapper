#!/usr/bin/env python

import os
import argparse
from time import sleep
from pandas import DataFrame, merge, read_csv, to_datetime
import sample_tools

basedir = os.path.abspath(os.curdir)

# set sleep duration after every api request
SLEEP_DURATION = 0.1

# paths that store the webproperties.csv and profiles.sv
WEBPROPERTIES_PATH = os.path.join(basedir, 'webproperties.csv')
PROFILES_PATH = os.path.join(basedir, 'profiles.csv')


def get_service():
    if 'service' not in globals():
        global service
        # Authenticate and construct service.
        service, flags = sample_tools.init(
            '', 'analytics', 'v3', __doc__, basedir,
            scope='https://www.googleapis.com/auth/analytics.readonly')
    return service


def get_account_ids():
    get_service()

    accounts = service.management().accounts().list().execute()
    sleep(SLEEP_DURATION)
    return [account.get('id') for account in accounts.get('items', [])]


def get_webproperties():
    get_service()

    webproperties_list = []
    if os.path.exists(WEBPROPERTIES_PATH):
        return read_csv(WEBPROPERTIES_PATH)
    headers = ['kind', 'accountId', 'webpropertyId', 'websiteUrl', 'created', 'updated']
    accountIds = get_account_ids()
    for accountId in accountIds:
        webproperties = service.management().webproperties().list(accountId=accountId).execute()
        sleep(SLEEP_DURATION)
        for webproperty in webproperties.get('items', []):
            row = (
                webproperty.get('kind'),
                webproperty.get('accountId'),
                webproperty.get('id'),
                webproperty.get('websiteUrl'),
                webproperty.get('created'),
                webproperty.get('updated')
            )
            webproperties_list.append(row)
    df = DataFrame(webproperties_list, columns=headers)
    df.to_csv(WEBPROPERTIES_PATH, index=0, encoding='utf-8')
    return df


def cache_profiles():
    get_service()

    webproperties = get_webproperties()
    accountIds = webproperties.accountId.tolist()
    profile_list = []
    headers = ['kind', 'accountId', 'webpropertyId', 'profileId', 'profileName', 'websiteUrl', 'created', 'updated']
    print 'processing profiles.csv'
    for i, webpropertyId in enumerate(webproperties.webpropertyId.tolist()):
        profiles = service.management().profiles().list(accountId=accountIds[i],
                                                        webPropertyId=webpropertyId).execute()
        sleep(SLEEP_DURATION)  # avoid quota limit error
        for profile in profiles.get('items', []):
            row = (
                profile.get('kind'),
                profile.get('accountId'),
                profile.get('webPropertyId'),
                profile.get('id'),
                profile.get('name'),
                profile.get('websiteUrl'),
                profile.get('created'),
                profile.get('updated')
            )
            profile_list.append(row)
    df = DataFrame(profile_list, columns=headers)
    df['profileId'] = df.profileId.astype('int')
    df.to_csv(PROFILES_PATH, index=0, encoding='utf-8')


def get_profiles(webproperty_id=None):
    if webproperty_id is None:
        if not os.path.exists(PROFILES_PATH):
            cache_profiles()
        return read_csv(PROFILES_PATH)
    else:
        if not os.path.exists(PROFILES_PATH):
            cache_profiles()
        df = read_csv(PROFILES_PATH)

        if isinstance(webproperty_id, list):
            wids = webproperty_id
        elif isinstance(webproperty_id, str):
            wids = [webproperty_id]
        else:
            raise TypeError('webproperty_id should only be list or str')
        return df[df.webpropertyId.isin(wids)]


def _cleanup():
    """Remove the temp webproperties/profiles lookup files
    """
    if os.path.exists(WEBPROPERTIES_PATH):
        os.remove(WEBPROPERTIES_PATH)
    if os.path.exists(PROFILES_PATH):
        os.remove(PROFILES_PATH)


def authorize():
    get_service()


def get_api_query(start_date='yesterday', end_date='yesterday', metrics='', dimensions='', sort=None, filters=None,
                  output=None, webproperty_id=None, profile_id=None, **kwargs):
    """
    Execute GA API queries given selected parameters.
    Parameters of start_date, end_date, metrics, dimensions, sort, filters are the parameters to be passed to
    GA API. Please refer to https://developers.google.com/analytics/devguides/reporting/core/v3/reference#q_summary
    for details.

    :param start_date: Start date for fetching Analytics data. Requests can specify a start date formatted as YYYY-MM-DD, or as a relative date (e.g., today, yesterday, or NdaysAgo where N is a positive integer).
    :param end_date: End date for fetching Analytics data. Request can specify an end date formatted as YYYY-MM-DD, or as a relative date (e.g., today, yesterday, or NdaysAgo where N is a positive integer).
    :param metrics: A list of comma-separated metrics, such as ga:sessions,ga:bounces.
    :param dimensions: A list of comma-separated dimensions for your Analytics data, such as ga:browser,ga:city.
    :param sort: A list of comma-separated dimensions and metrics indicating the sorting order and sorting direction for the returned data.
    :param filters: Dimension or metric filters that restrict the data returned for your request.
    :param output: If set, the output DataFrame will be output as a CSV to a path where the output specifies.
    :param webproperty_id: webproperty_id(s) to be fetched. If not set, will output all available profiles for all webproperties.
    :param profile_id: profile_id(s) to be fetched. If not set, will output all available profiles under specified webproperties.
    :param kwargs: Other parameters including cleanup.
    :return: DataFrame
    """

    # get service
    if 'service' not in globals():
        global service
        service = get_service()

    # cleanup
    if kwargs.get('cleanup') or kwargs.get('refresh'):
        _cleanup()

    # debug
    debug = kwargs.get('debug')

    df = []
    headers = []

    if webproperty_id is not None:
        pids_wp = get_profiles(webproperty_id).profileId.astype(str).tolist()
        if profile_id is not None:
            if isinstance(profile_id, list):
                pids = [p for p in profile_id if p in pids_wp]
            elif isinstance(profile_id, str) or isinstance(profile_id, int):
                if profile_id in pids_wp:
                    pids = [profile_id]
                else:
                    pids = []
        else:
            pids = pids_wp
    else:
        if profile_id is not None:
            if isinstance(profile_id, list):
                pids = profile_id
            elif isinstance(profile_id, str):
                pids = [profile_id]
            else:
                raise TypeError('profile_id can only be str or list')
        else:
            pids = get_profiles(webproperty_id).profileId.astype(str).tolist()
    df_profile = get_profiles(webproperty_id).ix[:,
                 ['accountId', 'webpropertyId', 'profileId', 'profileName', 'websiteUrl']]

    # iterate through each profile_id
    for profileId in pids:
        counter = 0
        total_results = 0
        while True:
            if counter >= total_results and counter != 0:
                break
            try:
                results = service.data().ga().get(
                    ids="ga:" + str(profileId),
                    start_date=start_date,
                    end_date=end_date,
                    metrics=metrics,
                    dimensions=dimensions,
                    sort=sort,
                    filters=filters,
                    start_index=str(counter + 1),
                    max_results='10000',
                    samplingLevel='HIGHER_PRECISION'
                ).execute()

                # get total results
                total_results = results.get('totalResults')

                # if not results for the query, break the loop
                if total_results == 0:
                    break

                # get sample size
                contains_sampled_data = results.get('containsSampledData')
                if contains_sampled_data:
                    sample_space = float(results.get('sampleSpace'))
                    sample_size = float(results.get('sampleSize'))
                    sample_ratio = sample_size / sample_space
                else:
                    sample_ratio = 1.0

                # avoid quota limit error
                sleep(SLEEP_DURATION)

                # parsing data
                headers = [x['name'].replace('ga:', '') for x in results.get('columnHeaders')]
                rows = results.get('rows', [])
                if rows:
                    for row in rows:
                        row.append(profileId)
                        df.append(row)
                counter += len(rows)

                # printing
                if debug:
                    print 'processing profile %s (%s / %s results fetched, sample ratio: %.2f%%)' % (profileId,
                                                                                                     counter,
                                                                                                     total_results,
                                                                                                     sample_ratio * 100)

            except Exception, err:
                print(err)
                break

    # if no results, return empty DataFrame
    if len(df) == 0:
        return DataFrame([])
    else:
        df = DataFrame(df, columns=headers + ['profileId'])

    # convert ga:date to datetime dtype
    if 'ga:date' in headers:
        df['ga:date'] = to_datetime(df['ga:date'])

    # add profileId
    df['profileId'] = df.profileId.astype('int')

    # add profile info
    df = merge(left=df, right=df_profile, left_on='profileId', right_on='profileId', how='left')

    # output to csv if output param is set
    if output is not None:
        df.to_csv(output, index=False, encoding='utf-8')

    return df


def main():
    parser = argparse.ArgumentParser(description='The Goolge Analytics wrapper is a convenient tool to extract data '
                                                 'from GA via API. It is especially useful when the user has many '
                                                 'GA profiles / web properties.')
    parser.add_argument('-s', '--start_date', help='Start date for fetching Analytics data. Requests can specify a '
                                                   'start date formatted as YYYY-MM-DD, or as a relative date (e.g., '
                                                   'today, yesterday, or NdaysAgo where N is a positive integer).')
    parser.add_argument('-e', '--end_date', help='End date for fetching Analytics data. Request can specify an end '
                                                 'date formatted as YYYY-MM-DD, or as a relative date (e.g., today, '
                                                 'yesterday, or NdaysAgo where N is a positive integer).')
    parser.add_argument('-m', '--metrics', help='A list of comma-separated metrics, such as ga:sessions,ga:bounces.')
    parser.add_argument('-d', '--dimensions', help='A list of comma-separated dimensions for your Analytics data, '
                                                   'such as ga:browser,ga:city.')
    parser.add_argument('-S', '--sort', help='A list of comma-separated dimensions and metrics indicating the sorting '
                                             'order and sorting direction for the returned data.')
    parser.add_argument('-f', '--filters', help='Dimension or metric filters that restrict the data returned for your '
                                                'request.')
    parser.add_argument('-o', '--output', help='If set, the output DataFrame will be output as a CSV to a path where '
                                               'the output specifies.')
    parser.add_argument('-w', '--webproperty_id', help='webproperty_id(s) to be fetched. If not set, will output all '
                                                       'available profiles for all webproperties.')
    parser.add_argument('-p', '--profile_id', help='profile_id(s) to be fetched. If not set, will output all available '
                                                   'profiles under specified webproperties.')
    parser.add_argument('-c', '--cleanup', help='If set true, temp files profiles.csv and webproperties.csv will be '
                                                'removed.')
    parser.add_argument('-D', '--debug', help='If set true, will echo debug info to stdout.')

    args = parser.parse_args()

    start_date = ''
    end_date = ''
    metrics = ''
    dimensions = ''
    sort_ = None
    filters = None
    output = None
    webproperty_id = None
    profile_id = None
    cleanup = False
    debug = False

    try:

        if args['start_date'] is not None:
            start_date = args['start_date']
        if args['end_date'] is not None:
            end_date = args['end_date']
        if args['metrics'] is not None:
            metrics = args['metrics']
        if args['dimensions'] is not None:
            dimensions = args['dimensions']
        if args['sort'] is not None:
            sort_ = args['sort']
        if args['filters'] is not None:
            filters = args['filters']
        if args['output'] is not None:
            output = args['output']
        if args['webproperty_id'] is not None:
            webproperty_id = args['webproperty_id']
        if args['profile_id'] is not None:
            profile_id = args['profile_id']
        if args['cleanup'] is not None:
            cleanup = bool(cleanup)
        if args['debug'] is not None:
            debug = bool(debug)

    except Exception:
        parser.print_help()

    get_api_query(start_date=start_date,
                  end_date=end_date,
                  metrics=metrics,
                  dimensions=dimensions,
                  sort=sort_,
                  filters=filters,
                  output=output,
                  webproperty_id=webproperty_id,
                  profile_id=profile_id,
                  cleanup=cleanup,
                  debug=debug)


if __name__ == '__main__':
    main()
