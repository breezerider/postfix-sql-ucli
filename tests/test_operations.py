import pytest
from sqlalchemy import create_engine
import unittest
import unittest.mock

# from unittest.mock import Mock
# import unittest.mock import patch

from postfix_sql_ucli import models
from postfix_sql_ucli import operations
from postfix_sql_ucli import utils


def test_reset_database(monkeypatch):

    engine = unittest.mock.Mock()
    mock_drop_all = unittest.mock.Mock()
    mock_create_all = unittest.mock.Mock()

    monkeypatch.setattr(models.Base.metadata, 'drop_all', mock_drop_all)
    monkeypatch.setattr(models.Base.metadata, 'create_all', mock_create_all)

    operations.reset_database(engine)

    mock_drop_all.assert_called_with(engine)
    mock_create_all.assert_called_with(engine)


class TestOperation(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        models.Base.metadata.create_all(self.engine)


    def tearDown(self):
        models.Base.metadata.drop_all(self.engine)


    def test_add_domain(self):
        operations.reset_database(self.engine)

        domain = "test.com"

        domains, added = operations.add_domain(self.engine, domain)

        self.assertEqual([{"id": 1, "name": domain}], domains)
        self.assertEqual(True, added)

        domains, added = operations.add_domain(self.engine, domain)

        self.assertEqual([{"id": 1, "name": domain}], domains)
        self.assertEqual(False, added)


    def test_search_domains(self):
        operations.reset_database(self.engine)

        for domain in ["test.com", "other.org"]:
            operations.add_domain(self.engine, domain)

        queries = ["test", "other", "%.com"]
        expected_results = [
            [{"id": 1, "name": "test.com"}],
            [{"id": 2, "name": "other.org"}],
            [{"id": 1, "name": "test.com"}],
        ]

        for query, expected in zip(queries, expected_results):
            domains = operations.search_domains(self.engine, query)

            self.assertEqual(expected, domains)

        queries_exact = ["test.com", "other.org", "%.com", "test"]
        expected_results_exact = [
            [{"id": 1, "name": "test.com"}],
            [{"id": 2, "name": "other.org"}],
            [],
            [],
        ]

        for query, expected in zip(queries_exact, expected_results_exact):
            domains = operations.search_domains(self.engine, query, exact=True)

            self.assertEqual(expected, domains)


    @unittest.mock.patch('postfix_sql_ucli.utils.doveadm_pw_hash')
    def test_add_user(self, mock_doveadm_pw_hash):
        operations.reset_database(self.engine)

        domain = "test.com"
        operations.add_domain(self.engine, domain)
        email = "user@" + domain
        password = "password"

        mock_doveadm_pw_hash.return_value = password

        users, added = operations.add_user(self.engine, email, password)

        self.assertEqual([{"id": 1, "domain_id": 1, "email": email, "password": password}], users)
        self.assertEqual(True, added)

        users, added = operations.add_user(self.engine, email, password)

        self.assertEqual([{"id": 1, "domain_id": 1, "email": email, "password": password}], users)
        self.assertEqual(False, added)

        users, added = operations.add_user(self.engine, "user@other.org", password)

        self.assertEqual(None, users)
        self.assertEqual(False, added)


    @unittest.mock.patch('postfix_sql_ucli.utils.doveadm_pw_hash')
    def test_search_users(self, mock_doveadm_pw_hash):
        operations.reset_database(self.engine)

        for domain in ["test.com", "other.org"]:
            operations.add_domain(self.engine, domain)

            email = "user@" + domain
            password = "password"
            mock_doveadm_pw_hash.return_value = password + "_" + domain

            operations.add_user(self.engine, email, password)

        queries = ["user", "user@test.com", "%.org"]
        expected_results = [
            [
                {"id": 1, "domain_id": 1, "email": "user@test.com", "password": "password_test.com"},
                {"id": 2, "domain_id": 2, "email": "user@other.org", "password": "password_other.org"},
            ],
            [{"id": 1, "domain_id": 1, "email": "user@test.com", "password": "password_test.com"}],
            [{"id": 2, "domain_id": 2, "email": "user@other.org", "password": "password_other.org"}],
        ]

        for query, expected in zip(queries, expected_results):
            users = operations.search_users(self.engine, query)

            self.assertEqual(expected, users)

        queries_exact = ["user@test.com", "user@other.org", "%.com", "user"]
        expected_results_exact = [
            [{"id": 1, "domain_id": 1, "email": "user@test.com", "password": "password_test.com"}],
            [{"id": 2, "domain_id": 2, "email": "user@other.org", "password": "password_other.org"}],
            [],
            [],
        ]

        for query, expected in zip(queries_exact, expected_results_exact):
            users = operations.search_users(self.engine, query, exact=True)

            self.assertEqual(expected, users)


    @unittest.mock.patch('postfix_sql_ucli.utils.doveadm_pw_hash')
    def test_delete_user(self, mock_doveadm_pw_hash):
        operations.reset_database(self.engine)

        for domain in ["test.com", "other.org"]:
            operations.add_domain(self.engine, domain)

            email = "user@" + domain
            password = "password"
            mock_doveadm_pw_hash.return_value = password + "_" + domain

            operations.add_user(self.engine, email, password)

        email = "user@test.com"
        expected = [{"id": 1, "domain_id": 1, "email": "user@test.com", "password": "password_test.com"}]
        users = operations.delete_user(self.engine, email)
        self.assertEqual(expected, users)

        email = "%@other.org"
        expected = []
        users = operations.delete_user(self.engine, email)
        self.assertEqual(expected, users)

        query = "user@other.org"
        expected = [{"id": 2, "domain_id": 2, "email": "user@other.org", "password": "password_other.org"}]
        users = operations.search_users(self.engine, query)
        self.assertEqual(expected, users)


    def test_add_alias(self):
        operations.reset_database(self.engine)

        domain = "test.com"

        operations.add_domain(self.engine, domain)

        source_email = "source@" + domain
        destination_email = "destination@other.org"

        aliases, added = operations.add_alias(self.engine, source_email, destination_email)

        self.assertEqual([{"id": 1, "domain_id": 1, "source": source_email, "destination": destination_email}], aliases)
        self.assertEqual(True, added)

        aliases, added = operations.add_alias(self.engine, source_email, destination_email)

        self.assertEqual([{"id": 1, "domain_id": 1, "source": source_email, "destination": destination_email}], aliases)
        self.assertEqual(False, added)

        aliases, added = operations.add_alias(self.engine, "source@other.org", destination_email)

        self.assertEqual(None, aliases)
        self.assertEqual(False, added)


    def test_search_aliases(self):
        operations.reset_database(self.engine)

        domain = "test.com"
        operations.add_domain(self.engine, domain)

        source_email = "source@" + domain
        operations.add_alias(self.engine, source_email, "destination1@other.org")
        operations.add_alias(self.engine, source_email, "destination2@other.org")

        aliases = operations.search_aliases(self.engine, source_email, "")

        self.assertEqual([{"id": 1, "domain_id": 1, "source": source_email, "destination": "destination1@other.org"}, {"id": 2, "domain_id": 1, "source": source_email, "destination": "destination2@other.org"}], aliases)

        aliases = operations.search_aliases(self.engine, "", "destination2@other.org")

        self.assertEqual([{"id": 2, "domain_id": 1, "source": source_email, "destination": "destination2@other.org"}], aliases)

        aliases = operations.search_aliases(self.engine, "source@other.org", "")

        self.assertEqual([], aliases)


    def test_delete_aliases(self):
        operations.reset_database(self.engine)

        domain = "test.com"
        operations.add_domain(self.engine, domain)

        source_email = "source@" + domain
        operations.add_alias(self.engine, source_email, "destination1@other.org")
        operations.add_alias(self.engine, source_email, "destination2@other.org")

        aliases = operations.delete_aliases(self.engine, source_email, "")
        self.assertEqual([{"id": 1, "domain_id": 1, "source": source_email, "destination": "destination1@other.org"}, {"id": 2, "domain_id": 1, "source": source_email, "destination": "destination2@other.org"}], aliases)

        operations.add_alias(self.engine, source_email, "destination1@other.org")
        operations.add_alias(self.engine, source_email, "destination2@other.org")
        operations.add_alias(self.engine, source_email, "destination3@another.org")

        aliases = operations.delete_aliases(self.engine, "", "%@other.org")

        self.assertEqual([{"id": 1, "domain_id": 1, "source": source_email, "destination": "destination1@other.org"}, {"id": 2, "domain_id": 1, "source": source_email, "destination": "destination2@other.org"}], aliases)

        aliases = operations.delete_aliases(self.engine, "", "destination3@other.org")

        self.assertEqual([], aliases)

        aliases = operations.delete_aliases(self.engine, "", "destination3@another.org")

        self.assertEqual([{"id": 3, "domain_id": 1, "source": source_email, "destination": "destination3@another.org"}], aliases)

        aliases = operations.search_aliases(self.engine, "", "")

        self.assertEqual([], aliases)
