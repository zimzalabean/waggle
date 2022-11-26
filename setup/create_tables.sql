drop table if exists comment_like;
drop table if exists post_like;
drop table if exists comment;
drop table if exists post;
drop table if exists tag;
drop table if exists gosling;
drop table if exists gaggle;
drop table if exists user;

CREATE TABLE user (
  user_id int not null auto_increment,
  email varchar(30),
  hashed_pass varchar(60),
  username varchar(20) not null,
  first_name varchar(30),
  last_name varchar(30),
  class_year varchar(4),
  bio_text varchar(200),
  strike int,
  unique(username),
  index(username),
  primary key (user_id)
) ENGINE = InnoDB;

CREATE TABLE gaggle (
  gaggle_id int not null auto_increment,
  gaggle_name varchar(20),
  author_id int,
  description varchar(100),
  primary key(gaggle_id),
  foreign key (author_id) references user(user_id) 
)  ENGINE = InnoDB;

CREATE TABLE gosling (
  user_id int,
  gaggle_id int,
  foreign key (user_id) references user(user_id),
  foreign key (gaggle_id) references gaggle(gaggle_id)  
) ENGINE = InnoDB;

CREATE TABLE tag (
  tag_id int not null auto_increment,
  gaggle_id int,
  tag_name varchar(50),
  primary key(tag_id),  
  foreign key (gaggle_id) references gaggle(gaggle_id)  
) ENGINE = InnoDB;

CREATE TABLE post (
  post_id int not null auto_increment,
  gaggle_id int,
  poster_id int,
  content varchar(5000),
  tag_id int,
  posted_date datetime,
  likes int,
  dislikes int,
  primary key (post_id),
  foreign key (tag_id) references tag(tag_id), 
  foreign key (poster_id) references user(user_id),
  foreign key (gaggle_id) references gaggle(gaggle_id)  
) ENGINE = InnoDB;

CREATE TABLE comment (
    comment_id int not null auto_increment,
    parent_comment_id int,
    post_id int,
    commentor_id int,
    content varchar(5000),
    posted_date datetime,
    likes int,
    dislikes int,
    primary key (comment_id),
    foreign key (post_id) references post(post_id),
    foreign key (commentor_id) references user(user_id),
    foreign key (parent_comment_id) references comment(comment_id)
) ENGINE = InnoDB;

CREATE TABLE post_like (
  post_id int,
  user_id int,
  kind enum('Like','Dislike'),
  foreign key (user_id) references user(user_id),
  foreign key (post_id) references post(post_id)  
) ENGINE = InnoDB;

CREATE TABLE comment_like (
  comment_id int,
  user_id int,
  kind enum('Like','Dislike'),
  foreign key (user_id) references user(user_id),
  foreign key (comment_id) references comment(comment_id)  
) ENGINE = InnoDB;