from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class VirtualDomain(Base):
    """Table containing virtual domains"""

    __tablename__ = 'virtual_domains'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True, unique=True)

    users = relationship('VirtualUser', back_populates='domain')
    aliases = relationship('VirtualAlias', back_populates='domain')

    def __repr__(self) -> str:
        return f"VirtualDomain(id={self.id!r}, name={self.name!r})"

    def __iter__(self):
        iters = {
            "id": self.id,
            "name": self.name,
        }

        for key, value in iters.items():
            yield key, value


class VirtualUser(Base):
    """Table containing virtual users per domain"""

    __tablename__ = 'virtual_users'

    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey('virtual_domains.id', ondelete='CASCADE'), nullable=False)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True, unique=True)

    domain = relationship('VirtualDomain', back_populates='users')

    def __repr__(self) -> str:
        return (
            f"VirtualUser(id={self.id!r}, domain_id={self.domain_id!r}, "
            f"email={self.email!r}, password={self.password!r})"
        )

    def __iter__(self):
        iters = {
            "id": self.id,
            "domain_id": self.domain_id,
            "email": self.email,
            "password": self.password,
        }

        for key, value in iters.items():
            yield key, value


class VirtualAlias(Base):
    """Table containing virtual aliases per domain"""

    __tablename__ = 'virtual_aliases'

    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey('virtual_domains.id', ondelete='CASCADE'), nullable=False)
    source = Column(String, nullable=False, index=True)
    destination = Column(String, nullable=False)

    domain = relationship('VirtualDomain', back_populates='aliases')

    def __repr__(self) -> str:
        return (
            f"VirtualAlias(id={self.id!r}, domain_id={self.domain_id!r}, "
            f"source={self.source!r}, destination={self.destination!r})"
        )

    def __iter__(self):
        iters = {
            "id": self.id,
            "domain_id": self.domain_id,
            "source": self.source,
            "destination": self.destination,
        }

        for key, value in iters.items():
            yield key, value
