SQL = """
CREATE TABLE history
(
    file_id integer not null,
    client_name varchar not null,
    action varchar not null,
    action_params varchar,
    timestamp timestamp not null,

    foreign key(file_id) references content(id)
    foreign key(client_name) references clients(name)
);
"""


def up(db, conf):
    db.executescript(SQL)
