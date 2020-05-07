CREATE TABLE `songs` (
  `song_id` bigint(30) NOT NULL AUTO_INCREMENT, 
  `duration_model_id` bigint(30),
  `sequence_model_id` bigint(30),
  `note_model_id` bigint(30), 
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `song_settings` json DEFAULT NULL,
  `key` varchar(50),
  `time_signature` varchar(50),
  `quality_score` double,
  PRIMARY KEY (`song_id`)
);