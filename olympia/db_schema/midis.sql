CREATE TABLE `midis` (
  `url` varchar(250),
  `midi_id` bigint(30) NOT NULL AUTO_INCREMENT, 
  `song_title` varchar(250),
  `artist` varchar(250),
  `date_added` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `key` varchar(50),
  `time_signature` varchar(50),
  `genre` varchar(250),
  PRIMARY KEY (`midi_id`),
  UNIQUE KEY `uc_id` (`url`,`midi_id`)
);