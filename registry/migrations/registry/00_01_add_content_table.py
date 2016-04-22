SQL = """

CREATE TABLE content
(
    id integer primary key autoincrement,     -- unique identifier for a file
    path varchar not null,                    -- absolute path of file. can also be a url
    size integer not null default 0,          -- size in bytes
    uploaded timestamp not null,              -- timestamp when file was uploaded
    modified timestamp not null,              -- timestamp when file contents were modified
    category varchar,                         -- used to determine type of content
    expiration timestamp,                     -- date when file is no longer relevant
    serve_path varchar not null,              -- path where file should be written to on the receiver
    aired boolean default 0,                  -- whether the file has been aired
    alive boolean not null                    -- where the entry is valid or not
);

"""


def up(db, conf):
    db.executescript(SQL)
