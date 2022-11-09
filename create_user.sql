use waggle_db;

drop table if exists user;
CREATE TABLE user (
  user_id int auto_increment,
  email varchar(30),
  hashed_pass varchar(20),
  username varchar(20) not null,
  first_name varchar(30),
  last_name varchar(30),
  class_year varchar(4),
  bio_text varchar(200),
  strike int,
  unique(username),
  index(username),
  primary key (user_id)
);
describe user;