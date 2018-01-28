--drop table if exists entries;
--drop table if exists users;
--

CREATE TABLE IF NOT EXISTS "ristoranti" (
	`ristid`	integer NOT NULL PRIMARY KEY AUTOINCREMENT,
	`nome`	text NOT NULL
);
CREATE TABLE IF NOT EXISTS "users" (
	`userid`	text NOT NULL,
	`nome`	text NOT NULL,
	PRIMARY KEY(`userid`)
);
CREATE TABLE IF NOT EXISTS "entries_rist" (
	`month`	TEXT NOT NULL,
	`userid`	TEXT NOT NULL,
	`ristid`	INTEGER NOT NULL,
	FOREIGN KEY(`userid`) REFERENCES `users`(`userid`),
	PRIMARY KEY(`ristid`,`userid`,`month`),
	FOREIGN KEY(`ristid`) REFERENCES `ristoranti`(`ristid`)
);
CREATE TABLE IF NOT EXISTS "entries_days" (
	`month`	TEXT NOT NULL,
	`userid`	TEXT NOT NULL,
	`day`	INTEGER NOT NULL,
	PRIMARY KEY(`month`,`userid`,`day`),
	FOREIGN KEY(`userid`) REFERENCES `users`(`userid`)
);
