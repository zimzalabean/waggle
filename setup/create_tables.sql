drop table if exists notifs;
drop table if exists group_blocked;
drop table if exists flag_comment;
drop table if exists flag_post;
drop table if exists bad_gosling;
drop table if exists mod_invite;
drop table if exists moderator;
drop table if exists comment_like;
drop table if exists post_like;
drop table if exists convos;
drop table if exists comment;
drop table if exists post_pics;
drop table if exists post;
drop table if exists tag;
drop table if exists gosling;
drop table if exists gaggle;
drop table if exists picfile;
drop table if exists user;


CREATE TABLE user (
  username varchar(20) not null,
  email varchar(30),
  hashed_pass varchar(60),
  first_name varchar(30),
  last_name varchar(30),
  class_year varchar(4),
  bio_text varchar(200) COLLATE utf8_bin,
  strike int,
  primary key (username)
) ENGINE = InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE picfile (
  username varchar(20),
  filename varchar(50),
  primary key (username),
  INDEX(username),
  foreign key (username) references user(username)
    on update no action
    on delete cascade 
) ENGINE = InnoDB;

CREATE TABLE gaggle (
  gaggle_name varchar(20) not null,
  name varchar(50), 
  author varchar(20),
  description varchar(100) COLLATE utf8_bin,
  guidelines varchar(100) COLLATE utf8_bin,
  primary key(gaggle_name),
  INDEX(gaggle_name),
  foreign key (author) references user(username) 
    on update no action
    on delete cascade
)  ENGINE = InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE guidelines (
  gaggle_name varchar(20), 
  position int auto_increment, 
  content varchar(500), 
  primary key(gaggle_name, position),
  index (gaggle_name),
  foreign key (gaggle_name) references gaggle(gaggle_name)  
    on update no action
    on delete cascade 
) ENGINE = InnoDB;

CREATE TABLE gosling (
  username varchar(20),
  gaggle_name varchar(20),
  primary key (username, gaggle_name),
  INDEX(username, gaggle_name),
  foreign key (username) references user(username)
    on update no action
    on delete cascade,
  foreign key (gaggle_name) references gaggle(gaggle_name)  
    on update no action
    on delete cascade 
) ENGINE = InnoDB;

CREATE TABLE post (
  post_id int not null auto_increment,
  gaggle_name varchar(20),
  username varchar(20),
  content varchar(5000) COLLATE utf8_bin,
  posted_date datetime,
  isHidden enum('Yes', 'No') DEFAULT 'No',
  likes int DEFAULT 0,
  dislikes int DEFAULT 0,
  flags int DEFAULT 0,
  replies int DEFAULT 0,
  primary key (post_id),
  INDEX(gaggle_name),
  foreign key (author) references user(username)
    on update no action
    on delete cascade,
  foreign key (gaggle_name) references gaggle(gaggle_name)  
    on update no action
    on delete cascade
) ENGINE = InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE post_pics (
  post_id int,
  filename varchar(50),
  primary key (post_id),
  INDEX(post_id),
  foreign key (post_id) references post(post_id)
    on update no action
    on delete cascade 
) ENGINE = InnoDB;

CREATE TABLE gaggle_pics (
  gaggle_name varchar(20),
  filename varchar(50),
  primary key (gaggle_name),
  INDEX(gaggle_name),
  foreign key (gaggle_name) references gaggle(gaggle_name)
    on update no action
    on delete cascade 
) ENGINE = InnoDB;

CREATE TABLE comment (
    comment_id int not null auto_increment,
    parent_comment_id int DEFAULT null,
    post_id int,
    gaggle_name varchar(20),
    username varchar(20),
    content varchar(5000) COLLATE utf8_bin,
    posted_date datetime,
    isHidden enum('Yes', 'No') DEFAULT 'No',
    likes int DEFAULT 0,
    dislikes int DEFAULT 0,
    flags int DEFAULT 0,
    replies int DEFAULT 0,
    primary key (comment_id),
    INDEX (post_id),
    foreign key (post_id) references post(post_id)
      on update no action
      on delete cascade, 
    foreign key (author) references user(username)
      on update no action
      on delete cascade, 
    foreign key (gaggle_name) references gaggle(gaggle_name)
      on update no action
      on delete cascade, 
    foreign key (parent_comment_id) references comment(comment_id)
      on update no action
      on delete cascade
) ENGINE = InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE post_like (
  post_id int,
  username varchar(20),
  foreign key (username) references user(username)
    on update no action
    on delete cascade, 
  foreign key (post_id) references post(post_id)  
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE TABLE comment_like (
  comment_id int,
  username varchar(20),
  foreign key (username) references user(username)
    on update no action
    on delete cascade, 
  foreign key (comment_id) references comment(comment_id)  
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE TABLE moderator (
  username varchar(20),
  gaggle_name varchar(20),
  primary key (username, gaggle_name),
  foreign key (username) references user(username)
    on update no action
    on delete cascade, 
  foreign key (gaggle_name) references gaggle(gaggle_name)
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE TABLE mod_invite (
  gaggle_name varchar(20),
  invitee varchar(20),
  posted_date datetime,
  status enum('Yes', 'No', 'Pending') DEFAULT 'Pending',
  primary key(gaggle_name, invitee),
  foreign key (gaggle_name) references gaggle(gaggle_name)
    on update no action
    on delete cascade,
  foreign key (invitee) references user(username)  
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE TABLE bad_gosling (
  gaggle_name varchar(20),
  username varchar(20), 
  unban_time datetime,
  reason varchar(255),
  primary key (gaggle_name, username),
  foreign key (gaggle_name) references gaggle(gaggle_name)
    on update no action
      on delete cascade,
  foreign key (username) references user(username)  
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE TABLE flag (
  report_id int not null auto_increment,  
  post_id int,
  comment_id int, 
  reporter varchar(20), 
  reason varchar(200),
  flagged_date datetime,
  mod varchar(20),
  mod_approved enum('Yes', 'No', 'Pending'),
  primary key (report_id),
  foreign key (post_id) references post(post_id)
    on update no action
    on delete cascade, 
  foreign key (comment_id) references comment(comment_id)
    on update no action
    on delete cascade,     
  foreign key (reporter) references user(username)
    on update no action
    on delete cascade, 
  foreign key (mod) references user(username)  
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE TABLE blocked (
  username varchar(20), 
  blocked_username varchar(20), 
  primary key(username, blocked_username),
  foreign key (blocked_username) references user(username)  
    on update no action
    on delete cascade, 
  foreign key (username) references user(username)  
    on update no action
    on delete cascade     
) ENGINE = InnoDB;

CREATE TABLE notifs(
  notif_id int not null auto_increment,
  username int,
  content varchar(500),
  kind enum ('liked', 'replied'),
  source enum('post', 'comment'),
  id int, 
  noti_time datetime,
  status enum('seen', 'pending'), 
  primary key (notif_id),
  foreign key (username) references user(username)
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE table convos(
  anc_id int,
  des_id int,
  foreign key (anc_id) references comment(comment_id)
    on update no action
    on delete cascade,
  foreign key (des_id) references comment(comment_id)
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE TABLE bookmark (
  username int, 
  post_id int,
  primary key(username, post_id),
  foreign key (username) references user(username)  
    on update no action
    on delete cascade, 
  foreign key (post_id) references post(post_id)  
    on update no action
    on delete cascade     
) ENGINE = InnoDB;