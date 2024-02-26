import getpass
import unittest.mock as mock
import pytest


from postfix_sql_ucli import utils


@pytest.mark.parametrize("email", [
    "someone@somewhere.com",
    "anybody@elsewhere.com",
    "a@s.co",
])
def test_is_valid_email_valid(email):
    assert utils.is_valid_email(email)


@pytest.mark.parametrize("email", [
    "",
    "@somewhere.com",
    "elsewhere.com",
    "chip&dale@somewhere.com",
    "chip@somewhere",
])
def test_is_valid_email_invalid(email):
    assert not utils.is_valid_email(email)


@pytest.mark.parametrize("email", [
    "someone@somewhere.com",
    "@elsewhere.com",
    "@s.co",
])
def test_is_valid_email_valid_domain_only(email):
    assert utils.is_valid_email(email, domain_only=True)


@pytest.mark.parametrize("domain", [
    "somewhere.com",
    "elsewhere.com",
    "a.co",
])
def test_is_valid_domain_name_valid(domain):
    assert utils.is_valid_domain_name(domain)


@pytest.mark.parametrize("domain", [
    "",
    "&somewhere.com",
    "somewhere",
    "a.b",
])
def test_is_valid_domain_name_invalid(domain):
    assert not utils.is_valid_domain_name(domain)


def test_doveadm_pw_hash():

    salt = "salt"
    password = "password"
    expected = "$6$salt$IxDD3jeSOb5eB1CX5LBsqZFVkJdido3OUILO5Ifz5iwMuTS4XMS130MTSuDDl3aCI6WouIL9AjRbLCelDCy.g."
    actual = utils.doveadm_pw_hash(password, salt)
    assert actual == expected


def test_get_password(monkeypatch):

    password_output = [
        "test",
        "test",
        "test",
        "wrong",
    ]

    def mock_getpass(prompt):
        output = password_output[mock_getpass.counter]
        mock_getpass.counter += 1
        return output
    mock_getpass.counter = 0

    expected = "test"
    monkeypatch.setattr(getpass, 'getpass', mock_getpass)
    actual = utils.get_password()
    assert actual == expected

    expected = None
    actual = utils.get_password(0)
    assert actual == expected


@pytest.mark.parametrize("data", [
    "",
    "database:\n  type: postgresql\n  name: test",
])
def test_load_database_config_invalid(data):

    with mock.patch("builtins.open", mock.mock_open(read_data=data)):
        with pytest.raises(ValueError, match="required object 'database' with all required fields not found"):
            utils.load_database_config("")
