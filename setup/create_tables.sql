drop table if exists notifs;
drop table if exists moderator;
drop table if exists mod_invite;
drop table if exists bad_gosling;
drop table if exists comment_like;
drop table if exists post_like;
drop table if exists flag_post;
drop table if exists flag_comment;
drop table if exists convos;
drop table if exists comment;
drop table if exists post;
drop table if exists tag;
drop table if exists gosling;
drop table if exists gaggle;
drop table if exists picfile;
drop table if exists post_pics;
drop table if exists user;


CREATE TABLE user (
  user_id int not null auto_increment,
  email varchar(30),
  hashed_pass varchar(60),
  username varchar(20) not null,
  first_name varchar(30),
  last_name varchar(30),
  class_year varchar(4),
  bio_text varchar(200) COLLATE utf8_bin,
  strike int,
  unique(username),
  primary key (user_id)
) ENGINE = InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE picfile (
  user_id int,
  filename varchar(50),
  primary key (user_id),
  INDEX(user_id),
  foreign key (user_id) references user(user_id)
    on update no action
    on delete cascade 
) ENGINE = InnoDB;

CREATE TABLE gaggle (
  gaggle_id int not null auto_increment,
  gaggle_name varchar(20),
  author_id int,
  description varchar(100) COLLATE utf8_bin,
  primary key(gaggle_id),
  INDEX(author_id),
  foreign key (author_id) references user(user_id) 
    on update no action
    on delete cascade
)  ENGINE = InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE gosling (
  user_id int,
  gaggle_id int,
  primary key (user_id, gaggle_id),
  INDEX(user_id),
  foreign key (user_id) references user(user_id)
    on update no action
    on delete cascade,
  foreign key (gaggle_id) references gaggle(gaggle_id)  
    on update no action
    on delete cascade 
) ENGINE = InnoDB;

CREATE TABLE tag (
  tag_id int not null auto_increment,
  gaggle_id int,
  tag_name varchar(50),
  primary key(tag_id),  
  INDEX(gaggle_id),
  foreign key (gaggle_id) references gaggle(gaggle_id)  
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE TABLE post (
  post_id int not null auto_increment,
  gaggle_id int,
  poster_id int,
  content varchar(5000) COLLATE utf8_bin,
  tag_id int,
  posted_date datetime,
  likes int,
  dislikes int,
  flags int,
  replies int, 
  primary key (post_id),
  INDEX(gaggle_id),
  foreign key (tag_id) references tag(tag_id) 
    on update no action
    on delete cascade,
  foreign key (poster_id) references user(user_id)
    on update no action
    on delete cascade,
  foreign key (gaggle_id) references gaggle(gaggle_id)  
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

CREATE TABLE comment (
    comment_id int not null auto_increment,
    parent_comment_id int,
    post_id int,
    commentor_id int,
    content varchar(5000) COLLATE utf8_bin,
    posted_date datetime,
    likes int,
    dislikes int,
    flags int,
    replies int, 
    primary key (comment_id),
    INDEX (post_id),
    foreign key (post_id) references post(post_id)
      on update no action
      on delete cascade, 
    foreign key (commentor_id) references user(user_id)
      on update no action
      on delete cascade, 
    foreign key (parent_comment_id) references comment(comment_id)
      on update no action
      on delete cascade
) ENGINE = InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;

CREATE TABLE post_like (
  post_id int,
  user_id int,
  kind enum('Like','Dislike'),
  INDEX(user_id),
  foreign key (user_id) references user(user_id)
    on update no action
    on delete cascade, 
  foreign key (post_id) references post(post_id)  
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE TABLE comment_like (
  comment_id int,
  user_id int,
  kind enum('Like','Dislike'),
  INDEX(user_id),
  foreign key (user_id) references user(user_id)
    on update no action
    on delete cascade, 
  foreign key (comment_id) references comment(comment_id)  
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE TABLE moderator (
  user_id int,
  gaggle_id int,
  INDEX(user_id),
  foreign key (user_id) references user(user_id)
    on update no action
    on delete cascade, 
  foreign key (gaggle_id) references gaggle(gaggle_id)
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE TABLE mod_invite (
  gaggle_id int,
  invitee_id int,
  accepted enum('Yes', 'No', 'Pending'),
  INDEX(gaggle_id),
  foreign key (gaggle_id) references gaggle(gaggle_id)
    on update no action
    on delete cascade,
  foreign key (invitee_id) references user(user_id)  
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE TABLE bad_gosling (
  gaggle_id int,
  username varchar(30), 
  ban_status enum('Yes','No'),
  strikes int, 
  reason varchar(300),
  mod_id int, 
  violated_time datetime,
  kind enum('Post', 'Comment', 'Spam'),
  remove_id int, 
  INDEX(mod_id),
  foreign key (gaggle_id) references gaggle(gaggle_id)
    on update no action
      on delete cascade,
  foreign key (mod_id) references user(user_id)  
    on update no action
    on delete cascade
)ENGINE = InnoDB;

CREATE TABLE flag_post (
  post_id int,
  reporter_id int,
  reason varchar(200),
  flagged_date datetime,
  mod_id int,
  mod_aprroved enum('Yes', 'No', 'Pending'),
  INDEX(mod_id),
  foreign key (post_id) references post(post_id)
    on update no action
    on delete cascade, 
  foreign key (reporter_id) references user(user_id)
    on update no action
    on delete cascade, 
  foreign key (mod_id) references user(user_id)  
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE TABLE flag_comment (
  comment_id int,
  reporter_id int,
  reason varchar(200),
  flagged_date datetime,
  mod_id int,
  mod_aprroved enum('Yes', 'No', 'Pending'),
  index(mod_id),
  foreign key (comment_id) references comment(comment_id)
    on update no action
    on delete cascade, 
  foreign key (reporter_id) references user(user_id)
    on update no action
    on delete cascade,
  foreign key (mod_id) references user(user_id)  
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE TABLE group_blocked (
  gaggle_id int,
  blocked_user_id int,
  ban_time datetime, 
  unban_time datetime,
  foreign key (gaggle_id) references gaggle(gaggle_id)
    on update no action
    on delete cascade,
  foreign key (blocked_user_id) references user(user_id)  
    on update no action
    on delete cascade
) ENGINE = InnoDB;

CREATE TABLE notifs(
  notif_id int not null auto_increment,
  user_id int,
  content varchar(500),
  kind enum ('liked', 'replied'),
  source enum('post', 'comment'),
  id int, 
  noti_time datetime,
  status enum('seen', 'pending'), 
  primary key (notif_id),
  foreign key (user_id) references user(user_id)
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