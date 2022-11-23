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
  ('animeclub', 1, 'We love anime <3'),
  ('slatercenter',2,'A house for International Students at Wellesley College'), 
  ('target', 3, 'Tips on how to get promoted to manager at Target'), 
  ('latinxorg', 4, 'For the Latinx community'),
  ('wellesleyinprod', 5, 'Wellesley in Production');

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

