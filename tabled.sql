CREATE TABLE `data_table` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `pi_id` int(11) NOT NULL,
  `data` double NOT NULL,
  `data_type` varchar(45) NOT NULL,
  `date_time` datetime NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3338 DEFAULT CHARSET=latin1;


CREATE TABLE `token_table` (
  `user_id` varchar(16) NOT NULL,
  `user_type` varchar(45) NOT NULL,
  `issued_at` datetime NOT NULL,
  `expires_at` datetime NOT NULL,
  `token` varchar(100) NOT NULL,
  PRIMARY KEY (`token`)
) /*!50100 TABLESPACE `innodb_system` */ ENGINE=InnoDB DEFAULT CHARSET=latin1;


CREATE TABLE `user_table` (
  `user_name` varchar(45) NOT NULL,
  `password` varchar(100) NOT NULL,
  `user_type` varchar(16) NOT NULL,
  PRIMARY KEY (`user_name`)
) /*!50100 TABLESPACE `innodb_system` */ ENGINE=InnoDB DEFAULT CHARSET=latin1;
