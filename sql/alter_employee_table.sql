ALTER TABLE user ADD self_intro varchar (255) NULL AFTER jobtitle;
ALTER TABLE user ADD resume varchar(255) NULL AFTER image;
ALTER TABLE user ADD certificate varchar (255) NULL AFTER resume;