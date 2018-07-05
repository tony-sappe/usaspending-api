# Stdlib imports
import datetime
import decimal

# Core Django imports

# Third-party app imports
from rest_framework import status
from model_mommy import mommy
import pytest

# Imports from your apps
from usaspending_api.common.exceptions import InvalidParameterException
from usaspending_api.common.helpers.generic_helper import generate_fiscal_year
from usaspending_api.recipient.v2.views.recipients import validate_duns, obtain_recipient_totals

# Getting relative dates as the 'latest'/default argument returns results relative to when it gets called
TODAY = datetime.datetime.now()
OUTSIDE_OF_LATEST = (TODAY - datetime.timedelta(365 + 2))
CURRENT_FISCAL_YEAR = generate_fiscal_year(TODAY)


EXPECTED_PARENT = {
    'name': 'Test Parent',
    'duns': '123456789',
    'parent_name': None,
    'parent_duns': None,
    'location': {
        'address_line1': '123 Sesame St',
        'address_line2': '',
        'address_line3': '',
        'foreign_province': '',
        'city_name': '',
        'county_name': '',
        'state_code': 'VA',
        'zip': '22102',
        'zip4': '',
        'foreign_postal_code': '',
        'country_name': '',
        'country_code': 'USA',
        'congressional_code': '05'
    },
    'business_types': [
        'Corporate Entity',
        'For Profit Organization'
    ],
    'total_prime_amount': 100000,
    'total_prime_awards': 1,
    # 'total_sub_amount': 1,
    # 'total_sub_awards': 100000,
    'recipient_level': 'P'
}
EXPECTED_CHILD = {
    'name': 'Test Child',
    'duns': '987654321',
    'parent_name': 'Test Parent',
    'parent_duns': '123456789',
    'location': {
        'address_line1': '124 Sesame St',
        'address_line2': '',
        'address_line3': '',
        'foreign_province': '',
        'city_name': '',
        'county_name': '',
        'state_code': 'VA',
        'zip': '22105',
        'zip4': '',
        'foreign_postal_code': '',
        'country_name': '',
        'country_code': 'USA',
        'congressional_code': '05'
    },
    'business_types': [
        'Corporate Entity',
        'For Profit Organization'
    ],
    'total_prime_amount': 100000,
    'total_prime_awards': 1,
    # 'total_sub_amount': 1,
    # 'total_sub_awards': 100000,
    'recipient_level': 'C'
}
EXPECTED_RECIPIENT = {
    'name': 'Test Recipient',
    'duns': '456789123',
    'parent_name': None,
    'parent_duns': None,
    'location': {
        'address_line1': '125 Sesame St',
        'address_line2': '',
        'address_line3': '',
        'foreign_province': '',
        'city_name': '',
        'county_name': '',
        'state_code': 'VA',
        'zip': '22105',
        'zip4': '',
        'foreign_postal_code': '',
        'country_name': '',
        'country_code': 'USA',
        'congressional_code': '05'
    },
    'business_types': [
        'Corporate Entity',
        'For Profit Organization'
    ],
    'total_prime_amount': 100000,
    'total_prime_awards': 1,
    # 'total_sub_amount': 1,
    # 'total_sub_awards': 100000,
    'recipient_level': 'R'
}
DUNSLESS_CHILD = {
    'name': 'Dunsless Child',
    'duns': None,
    'parent_name': 'Test Parent',
    'parent_duns': '789123456',
    'location': {
        'address_line1': '124 Sesame St',
        'address_line2': '',
        'address_line3': '',
        'foreign_province': '',
        'city_name': '',
        'county_name': '',
        'state_code': 'VA',
        'zip': '22105',
        'zip4': '',
        'foreign_postal_code': '',
        'country_name': '',
        'country_code': 'USA',
        'congressional_code': '05'
    },
    'business_types': [
        'Corporate Entity',
        'For Profit Organization'
    ],
    'total_prime_amount': 100000,
    'total_prime_awards': 1,
    # 'total_sub_amount': 1,
    # 'total_sub_awards': 100000,
    'recipient_level': 'C'
}


def list_recipients_endpoint():
    return '/api/v2/recipient/duns/'


def recipient_overview_endpoint(duns, year=None):
    url = '/api/v2/recipient/duns/{}/'.format(duns)
    if year:
        url = '{}?year={}'.format(url, year)
    return url


def recipient_childen_endpoint(duns, year=None):
    url = '/api/v2/recipient/children/{}/'.format(duns)
    if year:
        url = '{}?year={}'.format(url, year)
    return url


def test_validate_duns_success_latest():
    duns = '123456789'
    assert validate_duns(duns) == duns


def test_validate_duns_success_latest():
    duns = 'Dunsless Child'
    assert validate_duns(duns) == duns


def test_validate_duns_failure():
    duns = 'duns not found'

    with pytest.raises(InvalidParameterException):
        validate_duns(duns)


@pytest.mark.django_db
def test_obtain_state_totals(state_view_data, refresh_matviews):
    result = obtain_recipient_totals('01', str(generate_fiscal_year(OUTSIDE_OF_LATEST)), ['A'])
    expected = {'pop_state_code': 'AB', 'total': 10, 'count': 1}
    assert result == expected


@pytest.mark.django_db
def test_obtain_state_totals_none(state_view_data, refresh_matviews, monkeypatch):
    monkeypatch.setattr('usaspending_api.recipient.v2.views.states.VALID_FIPS', {'02': {'code': 'No State'}})
    result = obtain_recipient_totals('02')
    expected = {'pop_state_code': None, 'total': 0, 'count': 0}

    assert result == expected

@pytest.mark.django_db
def test_recipient_overview_success(client, state_data, refresh_matviews):
    # test small request - state
    resp = client.get(recipient_overview_endpoint('123456789'))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == EXPECTED_PARENT

    # test small request - district
    resp = client.get(recipient_overview_endpoint('987654321'))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == EXPECTED_CHILD

    # test small request - territory
    resp = client.get(recipient_overview_endpoint('456789123'))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == EXPECTED_RECIPIENT

    # test small request - territory
    resp = client.get(recipient_overview_endpoint('Dunsless Child'))
    assert resp.status_code == status.HTTP_200_OK
    assert resp.data == DUNSLESS_CHILD

@pytest.mark.django_db
def test_state_metadata_failure(client, state_data, refresh_matviews):
    """Verify error on bad autocomplete request for budget function."""

    # There is no DUNS with 999999
    resp = client.get(recipient_overview_endpoint('999999999'))
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # There is no FIPS with 03
    resp = client.get(recipient_overview_endpoint('123456789', 'break'))
    assert resp.status_code == status.HTTP_400_BAD_REQUEST

    # test
    resp = client.get(recipient_overview_endpoint('duns not found'))
    assert resp.status_code == status.HTTP_400_BAD_REQUEST
