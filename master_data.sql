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

drop table if exists gaggle;

CREATE TABLE gaggle (
  gaggle_id int not null auto_increment,
  gaggle_name varchar(20),
  author_id int,
  description varchar(100),
  primary key(gaggle_id),
  foreign key (author_id) references user(user_id) 
)  ENGINE = InnoDB;

drop table if exists gosling;

CREATE TABLE gosling (
  user_id int,
  gaggle_id int,
  foreign key (user_id) references user(user_id),
  foreign key (gaggle_id) references gaggle(gaggle_id)  
) ENGINE = InnoDB;

drop table if exists tag;

CREATE TABLE tag (
  tag_id int not null auto_increment,
  gaggle_id int,
  tag_name varchar(50),
  primary key(tag_id),  
  foreign key (gaggle_id) references gaggle(gaggle_id)  
) ENGINE = InnoDB;


drop table if exists post;

CREATE TABLE post (
  post_id int not null auto_increment,
  gaggle_id int,
  poster_id int,
  content varchar(5000),
  tag_id int,
  posted_date datetime,
  primary key (post_id),
  foreign key (tag_id) references tag(tag_id), 
  foreign key (poster_id) references user(user_id),
  foreign key (gaggle_id) references gaggle(gaggle_id)  
) ENGINE = InnoDB;

INSERT INTO gaggle
  (gaggle_name,
  author_id,
  `description` )
VALUES
  ('anime_club', 1, 'We love anime <3'),
  ('slater_center',2,'A house for International Students at Wellesley College'), 
  ('target_employee', 3, 'Tips on how to get promoted to manager at Target'), 
  ('latinx_org', 4, 'For the Latinx community'),
  ('wellesley_in_prod', 5, 'Wellesley in Production');

INSERT INTO post
  (
  gaggle_id,
  poster_id,
  content,
  posted_date)
VALUES
  (1,1,'Welcome','2022-11-11 11:11:11'),
  (2,2,'Welcome','2022-11-11 11:11:11'), 
  (3,3,'Welcome','2022-11-11 11:11:11'), 
  (4,4,'Welcome','2022-11-11 11:11:11'),
  (5,5,'Welcome','2022-11-11 11:11:11');

INSERT INTO gosling
  (user_id,
  gaggle_id)
VALUES
  (1,1),
  (2,2), 
  (3,3), 
  (4,4),
  (5,5);  

drop table if exists comment;

CREATE TABLE comment (
    comment_id int not null auto_increment,
    parent_comment_id int,
    post_id int,
    commentor_id int,
    content varchar(5000),
    posted_date datetime,
    primary key (comment_id),
    foreign key (post_id) references post(post_id),
    foreign key (commentor_id) references user(user_id),
    foreign key (parent_comment_id) references comment(comment_id)
)
ENGINE = InnoDB;

drop table if exists post_like;

CREATE TABLE post_like (
  post_id int,
  user_id int,
  kind enum('Like','Dislike'),
  foreign key (user_id) references user(user_id),
  foreign key (post_id) references post(post_id)  
) ENGINE = InnoDB;

drop table if exists comment_like;

CREATE TABLE comment_like (
  comment_id int,
  user_id int,
  kind enum('Like','Dislike'),
  foreign key (user_id) references user(user_id),
  foreign key (comment_id) references comment(comment_id)  
) ENGINE = InnoDB;

INSERT INTO comment
  ( parent_comment_id,
    post_id,
    commentor_id,
    content,
    posted_date)
VALUES
  (null,1,1,'First comment','2022-11-12 11:13:11'),
  (1,1,2,'Second replying to first','2022-11-12 11:13:11'),
  (2,1,3,'Third replying to 2nd','2022-11-12 11:13:11'),
  (1,1,4,'Fourth replying to first','2022-11-12 11:13:11'),
  (null,2,5,'Fifth standalone','2022-11-12 11:13:11');


INSERT INTO post_like
  (post_id,
  user_id,
  kind
  )
VALUES
  (1,1,'Like'),
  (2,2,'Like'), 
  (3,3,'Like'), 
  (4,4,'Like'),
  (5,5,'Like'); 

INSERT INTO comment_like
  (comment_id,
  user_id, 
  kind)
VALUES
  (1,1,'Like'),
  (2,2,'Like'), 
  (3,3,'Like'), 
  (4,4,'Like'),
  (5,5,'Like');  

drop table if exists post_like_count;

CREATE TABLE post_like_count (
  post_id int,
  num_likes int
) ENGINE = InnoDB;

drop table if exists comment_like_count;

CREATE TABLE comment_like_count (
  comment_id int,
  num_likes int
) ENGINE = InnoDB;

INSERT INTO post_like_count
  (post_id,
  num_likes)
VALUES
  (1,1),
  (2,1), 
  (3,1), 
  (4,1),
  (5,1);  

INSERT INTO comment_like_count
  (comment_id,
  num_likes)
VALUES
  (1,1),
  (2,1), 
  (3,1), 
  (4,1),
  (5,1);

