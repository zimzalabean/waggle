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


