-- SQLite
CREATE TABLE session(
    session_id INTEGER PRIMARY KEY NOT NULL,
    username TEXT
);

CREATE TABLE users(
    username TEXT,
    chats_id INTEGER
);

CREATE TABLE chats(
    chats_id INTEGER,
    chat_id INTEGER
);

CREATE TABLE chat(
    chat_id INTEGER,
    username_1 TEXT,
    username_2 TEXT,
    storage_id INTEGER,
    msg_storage_id INTEGER
);

CREATE TABLE file_storage(
    storage_id INTEGER,
    file_id INTEGER
);

CREATE TABLE file(
    file_id INTEGER,
    filename TEXT,
    file BLOB
);

CREATE TABLE msg_storage(
    msg_storage_id INTEGER,
    msg_id INTEGER
);

CREATE TABLE message(
    msg_id INTEGER,
    src_usr_name TEXT,
    dst_usr_name TEXT,
    msg blob
);