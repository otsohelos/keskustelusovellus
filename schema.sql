CREATE TABLE users(id SERIAL PRIMARY KEY, username TEXT, password TEXT, userlevel TEXT UNIQUE);
CREATE TABLE conversations(id SERIAL PRIMARY KEY, username TEXT, header TEXT, content TEXT);