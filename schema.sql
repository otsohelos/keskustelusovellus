CREATE TABLE users(id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT, userlevel TEXT);
CREATE TABLE conversations(id SERIAL PRIMARY KEY, username TEXT, header TEXT, content TEXT);
CREATE TABLE replies(id SERIAL PRIMARY KEY, username TEXT, content TEXT, thread_id INT, FOREIGN KEY (thread_id) REFERENCES conversations(id));
