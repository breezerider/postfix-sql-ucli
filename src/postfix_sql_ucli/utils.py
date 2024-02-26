import getpass
import passlib.hash
import re
import yaml

email_account_regexp = re.compile(r'^[a-zA-Z0-9._%+-]+$')
domain_regexp = re.compile(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

def is_valid_email(email, domain_only=False):
    """Check if a string constitutes a valid email address

    :param email: string containing an email address
    :type email: str
    :returns: True if string matches the valid email address regexp, False otherwise. If domain_only is set, then only the domain name is checked against the valid domain name regexp
    :rtype: bool"""

    if '@' not in email:
        return False

    email_account, domain_name = email.split('@', 1)

    if domain_only:
        return is_valid_domain_name(domain_name)
    else:
        return (email_account_regexp.match(email_account) is not None) and is_valid_domain_name(domain_name)

def is_valid_domain_name(domain_name):
    """Check if a string constitutes a valid domain name

    :param domain_name: string containing the domain name
    :type domain_name: str
    :returns: True if string matches the valid domain name regexp, False otherwise
    :rtype: bool"""
    return domain_regexp.match(domain_name) is not None

def doveadm_pw_hash(password, salt=None):
    """Encrypt a clear-text password string as doveadm password hash

    :param password: string containing the clear-text password
    :type password: str
    :returns: string containg the corresponding password hash
    :rtype: str"""
    return passlib.hash.sha512_crypt.using(salt=salt, rounds=5000).hash(password)

def get_password(max_count=-1):
    """New password prompt with confirmation

    :param max_count: maximum number of input attempts
    :type password: int
    :returns: string containg the input password or None if number of input attempts have been exceeded
    :rtype: str"""
    count = 0
    password_input = None
    confirmation_input = None

    while password_input != confirmation_input or password_input is None:
        if password_input is not None:
            print('Input did not match, please try again')

        if max_count > -1 and (count > max_count):
            print('Exceeded maximum number of input attempts')
            return None

        password_input = getpass.getpass(prompt="Enter user password: ")
        confirmation_input = getpass.getpass(prompt="Repeat user password: ")

        count += 1

    return password_input

def load_database_config(config_file_path):
    """Load database configuration from a YAML file with following format:

    :: code_block::yaml
       database:
         name: str # database name or file path
         type: str # database type, see https://docs.sqlalchemy.org/en/20/dialects/index.html
         host: str # database host
         port: str # database port
         user: str # database user
         password: str # database password

    :param config_file_path: path to configuration file
    :type config_file_path: str
    :returns: dictionary with databse configuration
    :rtype: dict"""

    # Load the YAML configuration file
    with open(config_file_path, 'r', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)

    if config is None or ('database' not in config) or any(x not in config["database"] for x in ['name', 'type']) or \
       (not config["database"]["type"].startswith('sqlite') and any(x not in config["database"] for x in ['user', 'password', 'host', 'port'])):
        raise ValueError("required object 'database' with all required fields not found")

    return config["database"]

