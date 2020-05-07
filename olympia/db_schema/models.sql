CREATE TABLE `models` (
  `model_id` bigint(30) NOT NULL AUTO_INCREMENT, 
  `model_type` enum("sequence", "duration", "note"),
  `lstm_sequence_length` bigint(30),
  `create_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `model_settings` json DEFAULT NULL,
  `instrument` varchar(50),
  `n_training_notes` bigint(30),
  `output_diversity` double,
  PRIMARY KEY (`model_id`)
);