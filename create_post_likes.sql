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
