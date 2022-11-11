drop table if exists comment;

CREATE TABLE comment {
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
}
ENGINE = InnoDB;