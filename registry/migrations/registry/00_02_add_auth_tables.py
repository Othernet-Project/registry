SQL = """

CREATE TABLE clients
(
    name varchar primary key not null,        -- unique name of the client
    description varchar not null,             -- description of the client
    maintainer  varchar  not null,            -- client maintainer name
    email varchar,                            -- email to be used for communication
    created timestamp not null,               -- timestamp when client was created
    active boolean not null default 1         -- where the client is active
);


CREATE TABLE client_keys
(
    client_name varchar not null,
    cipher varchar not null,
    key blob not null,

    unique(client_name, cipher),
    foreign key(client_name) references clients(name)
);
"""


def up(db, conf):
    db.executescript(SQL)
