#!/usr/bin/env python3

import sys

import click
from sqlalchemy import create_engine

from . import __version__, operations, utils


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(f'Version {__version__}')
    ctx.exit(0)


@click.command()
@click.argument(
    "operation",
    type=click.Choice([
        "reset",
        "add-domain",
        "search-domains",
        "delete-domain",
        "add-user",
        "search-users",
        "delete-user",
        "add-alias",
        "search-aliases",
        "delete-aliases",
    ]),
)
@click.option("--force", is_flag=True, help="Force reset without confirmation")
@click.option(
    "--config", type=click.Path(exists=True), help="Path to configuration file", default='postfix-sql-ucli.yml'
)
@click.option(
    '--version',
    is_flag=True,
    help="Print tool version and exit",
    callback=print_version,
    expose_value=False,
    is_eager=True,
)
@click.option("--verbose", is_flag=True, help="Verbose output")
@click.argument("arguments", nargs=-1)
def main(operation, force, config, verbose, arguments):
    """Perform one of the following operations on Postfix SQL database:

    * `reset` operation: resets Postfix SQL database, i.e. drop and create following tables:

    .. code-block:: sql

       DROP TABLE IF EXISTS "virtual_users";
       DROP TABLE IF EXISTS "virtual_aliases";
       DROP TABLE IF EXISTS "virtual_domains";

       CREATE TABLE IF NOT EXISTS "virtual_domains" (
               "id" SERIAL,
               "name" TEXT NOT NULL,
               PRIMARY KEY ("id")
       );

       CREATE UNIQUE INDEX name_idx ON virtual_domains (name);

       CREATE TABLE IF NOT EXISTS "virtual_users" (
               "id" SERIAL,
               "domain_id" int NOT NULL,
               "password" TEXT NOT NULL,
               "email" TEXT NOT NULL UNIQUE,
               PRIMARY KEY ("id"),
               FOREIGN KEY (domain_id) REFERENCES virtual_domains(id) ON DELETE CASCADE
       );


       CREATE UNIQUE INDEX email_idx ON virtual_users (email);

       CREATE TABLE IF NOT EXISTS "virtual_aliases" (
               "id" SERIAL,
               "domain_id" int NOT NULL,
               "source" TEXT NOT NULL,
               "destination" TEXT NOT NULL,
               PRIMARY KEY ("id"),
               FOREIGN KEY (domain_id) REFERENCES virtual_domains(id) ON DELETE CASCADE
       );

       CREATE INDEX source_idx ON virtual_aliases (source);

    * `add-domain` operation requires exactly one argument: domain name, adds a virtual domain entry to ``virtual_domains`` table and prints out the new entry to standard output.

    * `search-domains` operation expects at most one argument: domain name pattern, and prints out virtual domains with names following the pattern (or all entries in case no pattern is provided) from ``virtual_domains`` table to standard output.

    * `add-user` operation requires exactly one argument: user email, adds a virtual user account entry to ``virtual_users`` table and prints out the new entry to standard output.

    * `search-users` operation expects at most one argument: user email pattern, prints out virtual users with emails following the pattern (or all entries in case no pattern is provided) from ``virtual_users`` table to standard output.

    * `delete-user` operation requires exactly one argument: user email, and deletes a virtual user account entry with emails that matches exactly from ``virtual_users`` table and prints out ghe deleted virtual users entries to standard output.

    * `add-alias` operation requires exactly exactly two arguments: source and destination email addresses, adds a virtual alias entry to ``virtual_aliases`` table and prints out the new entry to standard output.

    * `search-aliases` operation expects at most two arguments: source and destination email patterns, prints out virtual aliases with emails following the pattern (or all entries in case no pattern is provided) from ``virtual_aliases`` table to standard output.

    * `delete-aliases` operation expects at most two arguments: source and destination email patterns, and deletes virtual alias entries with emails following the pattern (or all entries in case no pattern is provided) from ``virtual_aliases`` table and prints out the deleted virtual alias entries to standard output.
    """  # noqa: E501, B950

    # Load database configuration from YAML file
    try:
        db_config = utils.load_database_config(config)
    except Exception as e:
        click.echo(f"Error opening configuration file '{config}': {str(e)}")
        sys.exit(1)

    # Construct the database URL
    db_type = db_config['type']
    if not db_type.startswith('sqlite'):
        db_user = db_config['user']
        db_password = db_config['password']
        db_host = db_config['host']
        db_port = db_config['port']
        db_server = f'{db_user}:{db_password}@{db_host}:{db_port}'
    else:
        db_server = ''

    db_name = db_config['name']

    db_url = f'{db_type}://{db_server}/{db_name}'

    # Create an engine
    engine = create_engine(db_url, echo=verbose)

    # Perform the operation
    if operation == "reset":
        if len(arguments):
            click.echo("reset operation expects no arguments")
            sys.exit(1)
        if not force:
            confirm = input("Are you sure you want to reset the database? This will delete all data. (yes/no): ")
            if confirm.lower() != 'yes':
                print("Reset operation aborted.")
                return
        click.echo("Reset Postfix SQL database")
        operations.reset_database(engine)
    elif operation in ["add-domain", "delete-domain"]:
        if len(arguments) != 1:
            click.echo(f"{operation} operation requires exactly one argument: domain name")
            sys.exit(1)
        (domain_name,) = arguments
        if not utils.is_valid_domain_name(domain_name):
            click.echo(f"{operation} operation failed: invalid domain name '{domain_name}'")
            sys.exit(1)
        if operation == "add-domain":
            click.echo(f"Adding virtual domain: {domain_name}")
            domains, added = operations.add_domain(engine, domain_name)
            if added:
                click.echo(f"Created new virtual domain: {domains}")
            else:
                click.echo(f"Aborted, found exisitng virtual domain(s): {domains}")
        else:
            # delete_domain(engine, domain_name)
            click.echo("delete_domain operation is not implemented")
            pass
    elif operation == "search-domains":
        if len(arguments) > 1:
            click.echo("search-domains operation expects at most one argument: domain name pattern")
            sys.exit(1)
        elif len(arguments) == 1:
            (domain_name_pattern,) = arguments
        else:
            domain_name_pattern = ''
        click.echo(f"Searching virtual domain names for {domain_name_pattern}")
        results = operations.search_domains(engine, domain_name_pattern)
        if len(results):
            click.echo("Found virtual domain(s): " + ', '.join([str(x) for x in results]))
        else:
            click.echo("No virtual domains found")
    elif operation in ["add-user", "delete-user"]:
        if len(arguments) != 1:
            click.echo(f"{operation} operation requires exactly one argument: user email")
            sys.exit(1)
        (user_email,) = arguments
        if not utils.is_valid_email(user_email):
            click.echo(f"{operation} operation failed: invalid email address '{user_email}'")
            sys.exit(1)
        if operation == "add-user":
            # get user password
            if sys.stdin.isatty():
                # interactive shell, prompt user for a password
                user_password = utils.get_password()
            else:
                # read password from stdin
                user_password = sys.stdin.readline()
            click.echo(f"Adding virtual user: {user_email}")
            users, added = operations.add_user(engine, user_email, user_password)
            if users is None:
                _, email_domain = user_email.split('@', 1)
                click.echo(f"add-user operation failed: domain {email_domain} can not be used")
                sys.exit(1)
            if added:
                click.echo(f"Created new virtual user: {users}")
            else:
                click.echo(f"Aborted, found exisitng virtual user(s): {users}")
        else:
            click.echo(f"Deleting virtual user account: {user_email}")
            results = operations.delete_user(engine, user_email)
            if len(results):
                click.echo("Deleted virtual user account(s): " + ', '.join([str(x) for x in results]))
            else:
                click.echo("No virtual user accounts deleted")
    elif operation == "search-users":
        if len(arguments) > 1:
            click.echo("search-users operation expects at most one argument: user email pattern")
            sys.exit(1)
        elif len(arguments) == 1:
            (user_email_pattern,) = arguments
        else:
            user_email_pattern = ''
        click.echo(f"Searching virtual user accounts for {user_email_pattern}")
        results = operations.search_users(engine, user_email_pattern)
        if len(results):
            click.echo("Found virtual user account(s): " + ', '.join([str(x) for x in results]))
        else:
            click.echo("No virtual user accounts found")
    elif operation == "add-alias":
        if len(arguments) != 2:
            click.echo("add-alias operation requires exactly two arguments: source and destination email addresses")
            sys.exit(1)
        source, destination = arguments
        if not (utils.is_valid_email(source, True) and utils.is_valid_email(destination, True)):
            click.echo(f"add-alias operation failed: invalid email address in alias '{source}' -> '{destination}'")
            sys.exit(1)

        click.echo(f"Adding virtual alias: {source} -> {destination}")

        aliases, added = operations.add_alias(engine, source, destination)
        if aliases is None:
            _, email_domain = source.split('@', 1)
            click.echo(f"add-alias operation failed: domain {email_domain} can not be used")
            sys.exit(1)
        if added:
            click.echo(f"Created new virtual alias: {aliases}")
        else:
            click.echo(f"Aborted, found exisitng virtual alias(es): {aliases}")
    elif operation in ["delete-aliases", "search-aliases"]:
        if len(arguments) > 2:
            click.echo(f"{operation} operation expects at most two arguments: source and destination email patterns")
            sys.exit(1)
        elif len(arguments) == 1:
            source_email_pattern, destination_email_pattern = *arguments, ''
        elif len(arguments) == 2:
            source_email_pattern, destination_email_pattern = arguments
        else:
            source_email_pattern, destination_email_pattern = '', ''

        if operation == "delete-aliases":
            click.echo(f"Deleting virtual alias(es): {source_email_pattern} -> {destination_email_pattern}")
            results = operations.delete_aliases(engine, source_email_pattern, destination_email_pattern)
            if len(results):
                click.echo("Deleted virtual alias(es): " + ', '.join([str(x) for x in results]))
            else:
                click.echo("No virtual aliases deleted")
        else:
            click.echo(f"Searching virtual aliases for {source_email_pattern} -> {destination_email_pattern}")
            results = operations.search_aliases(engine, source_email_pattern, destination_email_pattern)
            if len(results):
                click.echo("Found virtual alias(es): " + ', '.join([str(x) for x in results]))
            else:
                click.echo("No virtual aliases found")
    else:
        # if an operation is in click.Choice above but is not implemented here
        click.echo("unexpected operation, this should never happen")
        sys.exit(1)


if __name__ == "__main__":
    main()
