drop table if exists bad_gosling;

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
  foreign key (gaggle_id) references gaggle(gaggle_id),
  foreign key (mod_id) references user(user_id)  
)  ENGINE = InnoDB;
