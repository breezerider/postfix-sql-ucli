import pytest
from click.testing import CliRunner
import unittest.mock

from postfix_sql_ucli import __version__
from postfix_sql_ucli import cli
from postfix_sql_ucli import operations


@pytest.fixture
def runner():
    return CliRunner()


def test_cli(runner):
    result = runner.invoke(cli.main)
    assert result.exit_code == 2
    assert result.exception
    assert result.output.strip().startswith('Usage: ')


def test_cli_version(runner):
    result = runner.invoke(cli.main, ['--version'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == f'Version {__version__}'


def test_cli_reset(runner, monkeypatch):

    mock_create_engine = unittest.mock.Mock()
    monkeypatch.setattr(cli, 'create_engine', mock_create_engine)
    mock_create_engine.return_value = "engine"

    mock_reset_database = unittest.mock.Mock()
    monkeypatch.setattr(operations, 'reset_database', mock_reset_database)

    result = runner.invoke(cli.main, ['reset', '--force', '--config', 'tests/postfix-sql-ucli.yml'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Reset Postfix SQL database'
    mock_reset_database.assert_called_with("engine")

    result = runner.invoke(cli.main, ['reset', '--force', '--config', 'tests/postfix-sql-ucli.yml', 'unexpected'])
    assert result.exit_code == 1
    assert result.exception
    assert result.output.strip() == 'reset operation expects no arguments'


def test_cli_add_domain(runner, monkeypatch):

    mock_create_engine = unittest.mock.Mock()
    monkeypatch.setattr(cli, 'create_engine', mock_create_engine)
    mock_create_engine.return_value = "engine"

    mock_add_domain = unittest.mock.Mock()
    monkeypatch.setattr(operations, 'add_domain', mock_add_domain)

    mock_add_domain.return_value = ("domains", True)
    result = runner.invoke(cli.main, ['add-domain', '--config', 'tests/postfix-sql-ucli.yml', 'test.com'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Adding virtual domain: test.com\nCreated new virtual domain: domains'
    mock_add_domain.assert_called_with("engine", "test.com")

    mock_add_domain.return_value = ("domains", False)
    result = runner.invoke(cli.main, ['add-domain', '--config', 'tests/postfix-sql-ucli.yml', 'other.org'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Adding virtual domain: other.org\nAborted, found exisitng virtual domain(s): domains'
    mock_add_domain.assert_called_with("engine", "other.org")

    result = runner.invoke(cli.main, ['add-domain', '--config', 'tests/postfix-sql-ucli.yml'])
    assert result.exit_code == 1
    assert result.exception
    assert result.output.strip() == 'add-domain operation requires exactly one argument: domain name'

    result = runner.invoke(cli.main, ['add-domain', '--config', 'tests/postfix-sql-ucli.yml', 'invalid'])
    assert result.exit_code == 1
    assert result.exception
    assert result.output.strip() == "add-domain operation failed: invalid domain name 'invalid'"


def test_cli_search_domains(runner, monkeypatch):

    mock_create_engine = unittest.mock.Mock()
    monkeypatch.setattr(cli, 'create_engine', mock_create_engine)
    mock_create_engine.return_value = "engine"

    mock_search_domains = unittest.mock.Mock()
    monkeypatch.setattr(operations, 'search_domains', mock_search_domains)

    mock_search_domains.return_value = ["domain1", "domain2"]
    result = runner.invoke(cli.main, ['search-domains', '--config', 'tests/postfix-sql-ucli.yml'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Searching virtual domain names for \nFound virtual domain(s): domain1, domain2'
    mock_search_domains.assert_called_with("engine", "")

    mock_search_domains.return_value = ["domain3"]
    result = runner.invoke(cli.main, ['search-domains', '--config', 'tests/postfix-sql-ucli.yml', 'domain3'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Searching virtual domain names for domain3\nFound virtual domain(s): domain3'
    mock_search_domains.assert_called_with("engine", "domain3")

    mock_search_domains.return_value = []
    result = runner.invoke(cli.main, ['search-domains', '--config', 'tests/postfix-sql-ucli.yml', 'non-existent'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Searching virtual domain names for non-existent\nNo virtual domains found'
    mock_search_domains.assert_called_with("engine", "non-existent")

    result = runner.invoke(cli.main, ['search-domains', '--config', 'tests/postfix-sql-ucli.yml', 'domain1', 'domain2'])
    assert result.exit_code == 1
    assert result.exception
    assert result.output.strip() == 'search-domains operation expects at most one argument: domain name pattern'


def test_cli_add_user(runner, monkeypatch):

    mock_create_engine = unittest.mock.Mock()
    monkeypatch.setattr(cli, 'create_engine', mock_create_engine)
    mock_create_engine.return_value = "engine"

    mock_add_user = unittest.mock.Mock()
    monkeypatch.setattr(operations, 'add_user', mock_add_user)

    mock_add_user.return_value = ("user@test.com", True)
    result = runner.invoke(cli.main, ['add-user', '--config', 'tests/postfix-sql-ucli.yml', 'user@test.com'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Adding virtual user: user@test.com\nCreated new virtual user: user@test.com'
    mock_add_user.assert_called_with("engine", "user@test.com", "")

    mock_add_user.return_value = ("user@other.org", False)
    result = runner.invoke(cli.main, ['add-user', '--config', 'tests/postfix-sql-ucli.yml', 'user@other.org'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Adding virtual user: user@other.org\nAborted, found exisitng virtual user(s): user@other.org'
    mock_add_user.assert_called_with("engine", "user@other.org", "")

    mock_add_user.return_value = (None, False)
    result = runner.invoke(cli.main, ['add-user', '--config', 'tests/postfix-sql-ucli.yml', 'user@unknown.org'])
    assert result.exit_code == 1
    assert result.exception
    assert result.output.strip() == 'Adding virtual user: user@unknown.org\nadd-user operation failed: domain unknown.org can not be used'
    mock_add_user.assert_called_with("engine", "user@unknown.org", "")

    result = runner.invoke(cli.main, ['add-user', '--config', 'tests/postfix-sql-ucli.yml'])
    assert result.exit_code == 1
    assert result.exception
    assert result.output.strip() == 'add-user operation requires exactly one argument: user email'

    result = runner.invoke(cli.main, ['add-user', '--config', 'tests/postfix-sql-ucli.yml', 'invalid'])
    assert result.exit_code == 1
    assert result.exception
    assert result.output.strip() == "add-user operation failed: invalid email address 'invalid'"


def test_cli_search_users(runner, monkeypatch):

    mock_create_engine = unittest.mock.Mock()
    monkeypatch.setattr(cli, 'create_engine', mock_create_engine)
    mock_create_engine.return_value = "engine"

    mock_search_users = unittest.mock.Mock()
    monkeypatch.setattr(operations, 'search_users', mock_search_users)

    mock_search_users.return_value = ["user1", "user2"]
    result = runner.invoke(cli.main, ['search-users', '--config', 'tests/postfix-sql-ucli.yml'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Searching virtual user accounts for \nFound virtual user account(s): user1, user2'
    mock_search_users.assert_called_with("engine", "")

    mock_search_users.return_value = ["user3"]
    result = runner.invoke(cli.main, ['search-users', '--config', 'tests/postfix-sql-ucli.yml', 'user3'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Searching virtual user accounts for user3\nFound virtual user account(s): user3'
    mock_search_users.assert_called_with("engine", "user3")

    mock_search_users.return_value = []
    result = runner.invoke(cli.main, ['search-users', '--config', 'tests/postfix-sql-ucli.yml', 'non-existent'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Searching virtual user accounts for non-existent\nNo virtual user accounts found'
    mock_search_users.assert_called_with("engine", "non-existent")

    result = runner.invoke(cli.main, ['search-users', '--config', 'tests/postfix-sql-ucli.yml', 'user1', 'user2'])
    assert result.exit_code == 1
    assert result.exception
    assert result.output.strip() == 'search-users operation expects at most one argument: user email pattern'


def test_cli_delete_user(runner, monkeypatch):

    mock_create_engine = unittest.mock.Mock()
    monkeypatch.setattr(cli, 'create_engine', mock_create_engine)
    mock_create_engine.return_value = "engine"

    mock_delete_user = unittest.mock.Mock()
    monkeypatch.setattr(operations, 'delete_user', mock_delete_user)

    mock_delete_user.return_value = ["user@test.com"]
    result = runner.invoke(cli.main, ['delete-user', '--config', 'tests/postfix-sql-ucli.yml', 'user@test.com'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Deleting virtual user account: user@test.com\nDeleted virtual user account(s): user@test.com'
    mock_delete_user.assert_called_with("engine", "user@test.com")

    mock_delete_user.return_value = []
    result = runner.invoke(cli.main, ['delete-user', '--config', 'tests/postfix-sql-ucli.yml', 'user@other.org'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Deleting virtual user account: user@other.org\nNo virtual user accounts deleted'
    mock_delete_user.assert_called_with("engine", "user@other.org")

    result = runner.invoke(cli.main, ['delete-user', '--config', 'tests/postfix-sql-ucli.yml'])
    assert result.exit_code == 1
    assert result.exception
    assert result.output.strip() == 'delete-user operation requires exactly one argument: user email'

    result = runner.invoke(cli.main, ['delete-user', '--config', 'tests/postfix-sql-ucli.yml', 'invalid'])
    assert result.exit_code == 1
    assert result.exception
    assert result.output.strip() == "delete-user operation failed: invalid email address 'invalid'"


def test_cli_add_alias(runner, monkeypatch):

    mock_create_engine = unittest.mock.Mock()
    monkeypatch.setattr(cli, 'create_engine', mock_create_engine)
    mock_create_engine.return_value = "engine"

    mock_add_alias = unittest.mock.Mock()
    monkeypatch.setattr(operations, 'add_alias', mock_add_alias)

    mock_add_alias.return_value = ("aliases", True)
    result = runner.invoke(cli.main, ['add-alias', '--config', 'tests/postfix-sql-ucli.yml', '@test.com', '@other.org'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Adding virtual alias: @test.com -> @other.org\nCreated new virtual alias: aliases'
    mock_add_alias.assert_called_with("engine", '@test.com', '@other.org')

    mock_add_alias.return_value = ("aliases", False)
    result = runner.invoke(cli.main, ['add-alias', '--config', 'tests/postfix-sql-ucli.yml', '@other.org', '@test.com'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Adding virtual alias: @other.org -> @test.com\nAborted, found exisitng virtual alias(es): aliases'
    mock_add_alias.assert_called_with("engine", '@other.org', '@test.com')

    mock_add_alias.return_value = (None, False)
    result = runner.invoke(cli.main, ['add-alias', '--config', 'tests/postfix-sql-ucli.yml', '@unknown.org', '@anywhere.org'])
    assert result.exit_code == 1
    assert result.exception
    assert result.output.strip() == 'Adding virtual alias: @unknown.org -> @anywhere.org\nadd-alias operation failed: domain unknown.org can not be used'
    mock_add_alias.assert_called_with("engine", '@unknown.org', '@anywhere.org')

    for args in [[], ['@test.com']]:
        result = runner.invoke(cli.main, ['add-alias', '--config', 'tests/postfix-sql-ucli.yml', *args])
        assert result.exit_code == 1
        assert result.exception
        assert result.output.strip() == 'add-alias operation requires exactly two arguments: source and destination email addresses'

    result = runner.invoke(cli.main, ['add-alias', '--config', 'tests/postfix-sql-ucli.yml', 'invalid', 'elsewhere'])
    assert result.exit_code == 1
    assert result.exception
    assert result.output.strip() == "add-alias operation failed: invalid email address in alias 'invalid' -> 'elsewhere'"


def test_cli_search_aliases(runner, monkeypatch):

    mock_create_engine = unittest.mock.Mock()
    monkeypatch.setattr(cli, 'create_engine', mock_create_engine)
    mock_create_engine.return_value = "engine"

    mock_search_aliases = unittest.mock.Mock()
    monkeypatch.setattr(operations, 'search_aliases', mock_search_aliases)

    mock_search_aliases.return_value = ["alias1", "alias2"]
    result = runner.invoke(cli.main, ['search-aliases', '--config', 'tests/postfix-sql-ucli.yml'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Searching virtual aliases for  -> \nFound virtual alias(es): alias1, alias2'
    mock_search_aliases.assert_called_with("engine", "", "")

    mock_search_aliases.return_value = ["source3 -> destination3"]
    result = runner.invoke(cli.main, ['search-aliases', '--config', 'tests/postfix-sql-ucli.yml', 'source3'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Searching virtual aliases for source3 -> \nFound virtual alias(es): source3 -> destination3'
    mock_search_aliases.assert_called_with("engine", "source3", "")

    mock_search_aliases.return_value = ["source3 -> destination3"]
    result = runner.invoke(cli.main, ['search-aliases', '--config', 'tests/postfix-sql-ucli.yml', '', 'destination3'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Searching virtual aliases for  -> destination3\nFound virtual alias(es): source3 -> destination3'
    mock_search_aliases.assert_called_with("engine", "", "destination3")

    mock_search_aliases.return_value = []
    result = runner.invoke(cli.main, ['search-aliases', '--config', 'tests/postfix-sql-ucli.yml', 'non-existent', ''])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Searching virtual aliases for non-existent -> \nNo virtual aliases found'
    mock_search_aliases.assert_called_with("engine", "non-existent", "")

    result = runner.invoke(cli.main, ['search-aliases', '--config', 'tests/postfix-sql-ucli.yml', 'too', 'many','args'])
    assert result.exit_code == 1
    assert result.exception
    assert result.output.strip() == 'search-aliases operation expects at most two arguments: source and destination email patterns'


def test_cli_delete_aliases(runner, monkeypatch):

    mock_create_engine = unittest.mock.Mock()
    monkeypatch.setattr(cli, 'create_engine', mock_create_engine)
    mock_create_engine.return_value = "engine"

    mock_delete_alias = unittest.mock.Mock()
    monkeypatch.setattr(operations, 'delete_aliases', mock_delete_alias)

    mock_delete_alias.return_value = ["aliases"]
    result = runner.invoke(cli.main, ['delete-aliases', '--config', 'tests/postfix-sql-ucli.yml', '@test.com', '@other.org'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Deleting virtual alias(es): @test.com -> @other.org\nDeleted virtual alias(es): aliases'
    mock_delete_alias.assert_called_with("engine", '@test.com', '@other.org')


    mock_delete_alias.return_value = []
    result = runner.invoke(cli.main, ['delete-aliases', '--config', 'tests/postfix-sql-ucli.yml', '@unknown.org', '@anywhere.org'])
    assert result.exit_code == 0
    assert not result.exception
    assert result.output.strip() == 'Deleting virtual alias(es): @unknown.org -> @anywhere.org\nNo virtual aliases deleted'
    mock_delete_alias.assert_called_with("engine", '@unknown.org', '@anywhere.org')


    result = runner.invoke(cli.main, ['delete-aliases', '--config', 'tests/postfix-sql-ucli.yml', 'too', 'many','args'])
    assert result.exit_code == 1
    assert result.exception
    assert result.output.strip() == 'delete-aliases operation expects at most two arguments: source and destination email patterns'

    for args in [[], ['@test.com'], ['', '@other.org']]:
        if len(args) == 0:
            source, destination = '', ''
        elif len(args) > 1:
            source, destination = args
        else:
            source, destination = *args, ''

        result = runner.invoke(cli.main, ['delete-aliases', '--config', 'tests/postfix-sql-ucli.yml', source, destination])
        mock_delete_alias.return_value = []
        assert result.exit_code == 0
        assert not result.exception
        assert result.output.strip() == f'Deleting virtual alias(es): {source} -> {destination}\nNo virtual aliases deleted'
