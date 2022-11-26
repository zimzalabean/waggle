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
  posted_date,
  likes,
  dislikes)
VALUES
  (1,1,'Welcome','2022-11-11 11:11:11',0,0),
  (2,2,'Welcome','2022-11-11 11:11:11',0,0), 
  (3,3,'Welcome','2022-11-11 11:11:11',0,0), 
  (4,4,'Welcome','2022-11-11 11:11:11',0,0),
  (5,5,'Welcome','2022-11-11 11:11:11',0,0);

INSERT INTO gosling
  (user_id,
  gaggle_id)
VALUES
  (1,1),
  (2,2), 
  (3,3), 
  (4,4),
  (5,5);  

INSERT INTO comment
  ( parent_comment_id,
    post_id,
    commentor_id,
    content,
    posted_date,
    likes,
    dislikes)
VALUES
  (null,1,1,'First comment','2022-11-12 11:13:11',0,0),
  (1,1,2,'Second replying to first','2022-11-12 11:13:11',0,0),
  (2,1,3,'Third replying to 2nd','2022-11-12 11:13:11',0,0),
  (1,1,4,'Fourth replying to first','2022-11-12 11:13:11',0,0),
  (null,2,5,'Fifth standalone','2022-11-12 11:13:11',0,0);


-- INSERT INTO post_like
--   (post_id,
--   user_id,
--   kind
--   )
-- VALUES
--   (1,1,'Like'),
--   (2,2,'Like'), 
--   (3,3,'Like'), 
--   (4,4,'Like'),
--   (5,5,'Like'); 

-- INSERT INTO comment_like
--   (comment_id,
--   user_id, 
--   kind)
-- VALUES
--   (1,1,'Like'),
--   (2,2,'Like'), 
--   (3,3,'Like'), 
--   (4,4,'Like'),
--   (5,5,'Like');  


