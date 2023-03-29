CREATE TABLE users(id SERIAL PRIMARY KEY, username TEXT UNIQUE, password TEXT, userlevel TEXT);
CREATE TABLE conversations(id SERIAL PRIMARY KEY, username TEXT, header TEXT, content TEXT, deleted_at TIMETZ, created_at TIMETZ DEFAULT current_timestamp);
CREATE TABLE replies(id SERIAL PRIMARY KEY, username TEXT, content TEXT, thread_id INT, deleted_at TIMETZ, created_at TIMETZ DEFAULT current_timestamp, modified_at TIMETZ, FOREIGN KEY (thread_id) REFERENCES conversations(id));
