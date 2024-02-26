from sqlalchemy import and_, delete, insert, select
from sqlalchemy.orm import Session

from . import models, utils


def _asdicts(results):
    return [dict(entry) for entry in results]


def reset_database(engine):
    """Reset the exisitng Postfix database

    :param engine: SQLAlchemy Engine object
    :type engine: object"""

    models.Base.metadata.drop_all(engine)
    models.Base.metadata.create_all(engine)


def add_domain(engine, domain_name):
    """Add a new virtual domain

    :param engine: SQLAlchemy Engine object
    :type engine: object
    :param domain_name: string containing the new domain name
    :type domain_name: str
    :returns: A tuple: list of entries in the database, a flag (True if a new entry was added, False otherwise)
    :rtype: tuple(list, bool)"""

    # check if domain exists
    domains = search_domains(engine, domain_name, True)

    if len(domains):
        return domains, False

    # add virtual domain
    with Session(engine) as session:
        domains = session.scalars(
            insert(models.VirtualDomain).returning(models.VirtualDomain),
            [
                {"name": domain_name},
            ],
        ).all()

        session.commit()  # write changes to the database

        return _asdicts(domains), True


def search_domains(engine, domain_name_pattern, exact=False):
    """Search virtual domains

    :param engine: SQLAlchemy Engine object
    :type engine: object
    :param domain_name_pattern: string containing the sought-for domain name pattern
    :type domain_name_pattern: str
    :param exact: If True pattern value must match exactly, otherwise match pattern
                  from beginning of the string
    :type exact: bool
    :returns: list of entries in the database
    :rtype: list"""

    # search domains
    with Session(engine) as session:
        if exact:
            results = session.scalars(
                select(models.VirtualDomain).where(models.VirtualDomain.name == domain_name_pattern)
            ).all()
        else:
            results = session.scalars(
                select(models.VirtualDomain).where(models.VirtualDomain.name.startswith(domain_name_pattern))
            ).all()

        return _asdicts(results)


def add_user(engine, user_email, user_password):
    """Add a new virtual user

    :param engine: SQLAlchemy Engine object
    :type engine: object
    :param user_email: string containing the new user email account address
    :type user_email: str
    :param user_password: string containing the new user email account password
    :type user_password: str
    :returns: A tuple: list of entries in the database, a flag (True if a new entry was added, False otherwise)
    :rtype: tuple(list, bool)"""

    # check if user email domain is present in the database
    _, email_domain = user_email.split('@', 1)

    domains = search_domains(engine, email_domain, True)

    if len(domains) != 1:
        return None, False

    # check if user exists
    users = search_users(engine, user_email, True)

    if len(users):
        return users, False

    # hash user passowrd
    user_password_hash = utils.doveadm_pw_hash(user_password)

    # add virtual user
    with Session(engine) as session:
        users = session.scalars(
            insert(models.VirtualUser).returning(models.VirtualUser),
            [
                {"domain_id": domains[0]["id"], "email": user_email, "password": user_password_hash},
            ],
        )

        session.commit()  # write changes to the database

        return _asdicts(users), True


def search_users(engine, user_email_pattern, exact=False):
    """Search virtual users

    :param engine: SQLAlchemy Engine object
    :type engine: object
    :param user_email_pattern: string containing the sought-for user email address pattern
    :type user_email_pattern: str
    :param exact: If True pattern value must match exactly, otherwise match pattern
                  from beginning of the string
    :type exact: bool
    :returns: list of entries in the database
    :rtype: list"""

    # search users
    with Session(engine) as session:
        if exact:
            results = session.scalars(
                select(models.VirtualUser).where(models.VirtualUser.email == user_email_pattern)
            ).all()
        else:
            results = session.scalars(
                select(models.VirtualUser).where(models.VirtualUser.email.startswith(user_email_pattern))
            ).all()

        return _asdicts(results)


def delete_user(engine, user_email_pattern):
    """Delete virtual user

    :param engine: SQLAlchemy Engine object
    :type engine: object
    :param user_email_pattern: string containing user email account address
    :type user_email_pattern: str
    :returns: list of entries in the database
    :rtype: list"""

    # delete virtual user
    with Session(engine) as session:
        results = session.scalars(
            delete(models.VirtualUser)
            .where(models.VirtualUser.email == user_email_pattern)
            .returning(models.VirtualUser)
        ).all()

        results = _asdicts(results)

        session.commit()  # write changes to the database

        return results


def add_alias(engine, source_email, destination_email):
    """Add a new virtual alias

    :param engine: SQLAlchemy Engine object
    :type engine: object
    :param source_email: string containing source email address
    :type source_email: str
    :param destination_email: string containing destination email address
    :type destination_email: str
    :returns: A tuple: list of entries in the database, a flag (True if a new entry was added, False otherwise)
    :rtype: tuple(list, bool)"""

    # check email domain
    _, source_email_domain = source_email.split('@', 1)

    domains = search_domains(engine, source_email_domain, True)

    if len(domains) != 1:
        return None, False

    # check if user exists
    aliases = search_aliases(engine, source_email, destination_email, True)

    if len(aliases):
        return aliases, False

    # add virtual alias
    with Session(engine) as session:
        aliases = session.scalars(
            insert(models.VirtualAlias).returning(models.VirtualAlias),
            [
                {"domain_id": domains[0]["id"], "source": source_email, "destination": destination_email},
            ],
        )

        session.commit()  # write changes to the database

        return _asdicts(aliases), True


def search_aliases(engine, source_email_pattern, destination_email_pattern, exact=False):
    """Search virtual users

    :param engine: SQLAlchemy Engine object
    :type engine: object
    :param source_email_pattern: string containing the source email address pattern
    :type source_email_pattern: str
    :param destination_email_pattern: string containing the destination email address pattern
    :type destination_email_pattern: str
    :param exact: If True pattern value must match exactly, otherwise match pattern
                  from beginning of the string
    :type exact: bool
    :returns: list of entries in the database
    :rtype: list"""

    # search aliases
    with Session(engine) as session:
        if exact:
            results = session.scalars(
                select(models.VirtualAlias).where(
                    and_(
                        models.VirtualAlias.source == source_email_pattern,
                        models.VirtualAlias.destination == destination_email_pattern,
                    )
                )
            ).all()
        else:
            results = session.scalars(
                select(models.VirtualAlias).where(
                    and_(
                        models.VirtualAlias.source.startswith(source_email_pattern),
                        models.VirtualAlias.destination.startswith(destination_email_pattern),
                    )
                )
            ).all()

        return _asdicts(results)


def delete_aliases(engine, source_email_pattern, destination_email_pattern):
    """Delete virtual aliases

    :param engine: SQLAlchemy Engine object
    :type engine: object
    :param source_email_pattern: string containing the source email address pattern
    :type source_email_pattern: str
    :param destination_email_pattern: string containing the destination email address pattern
    :type destination_email_pattern: str
    :returns: list of entries in the database
    :rtype: list"""

    # delete aliases
    with Session(engine) as session:
        results = session.scalars(
            delete(models.VirtualAlias)
            .where(
                and_(
                    models.VirtualAlias.source.startswith(source_email_pattern),
                    models.VirtualAlias.destination.startswith(destination_email_pattern),
                )
            )
            .returning(models.VirtualAlias)
        ).all()

        results = _asdicts(results)

        session.commit()  # write changes to the database

        return results
