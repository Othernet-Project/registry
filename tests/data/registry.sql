DELETE FROM content;
DELETE FROM client_keys;
DELETE FROM clients;

INSERT INTO content(path, size, uploaded, modified, category, expiration, serve_path, alive, aired) VALUES('tests/data/content/dir1/file1.txt', 100, strftime('%s', 'now'), strftime('%s', 'now'), 'core', strftime('%s', 'now') + 360000, 'dir1/file1.txt', 1, 0);
INSERT INTO content(path, size, uploaded, modified, category, expiration, serve_path, alive, aired) VALUES('tests/data/content/dir1/file2.txt', 100, strftime('%s', 'now'), strftime('%s', 'now'), 'core', strftime('%s', 'now') + 360000, 'dir1/file2.txt', 1, 0);
INSERT INTO content(path, size, uploaded, modified, category, expiration, serve_path, alive, aired) VALUES('tests/data/content/dir2/file3.txt', 100, strftime('%s', 'now'), strftime('%s', 'now'), 'core', strftime('%s', 'now') + 360000, 'dir2/file3.txt', 1, 0);
INSERT INTO content(path, size, uploaded, modified, category, expiration, serve_path, alive, aired) VALUES('tests/data/content/file4.txt', 100, strftime('%s', 'now'), strftime('%s', 'now'), 'core', strftime('%s', 'now') + 360000, 'file4.txt', 1, 0);

INSERT INTO clients(name, description, maintainer, email, created, active) VALUES ('test', 'test', 'test', 'test', strftime('%s', 'now'), 1);
INSERT INTO client_keys(client_name, cipher, key) VALUES('test', 'AES_CBC', 'This is a key123');
