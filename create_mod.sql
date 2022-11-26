drop table if exists moderator;

CREATE TABLE moderator (
    user_id int,
    gaggle_id int,
    foreign key (user_id) references user(user_id),
    foreign key (gaggle_id) references gaggle(gaggle_id)
) ENGINE = InnoDB;

drop table if exists mod_invite;

CREATE TABLE mod_invite (
    gaggle_id int,
    invitee_id int,
    accepted enum('Yes', 'No', 'Pending'),
    foreign key (gaggle_id) references gaggle(gaggle_id),
    foreign key (invitee_id) references user(user_id)  
) ENGINE = InnoDB;

INSERT INTO moderator
  (
  user_id,
  gaggle_id)
VALUES
  (1,2), 
  (1,5), 
  (2,1),
  (4,1);

INSERT INTO mod_invite
  (
    gaggle_id,
    invitee_id,
    accepted 
    )
VALUES
  (2,4, 'Pending'),
  (4,2, 'Pending')
  ;  