Start a postgres shell with:
```
psql -U postgres
```
if that fails, try
```
sudo -u postgres psql
```

Then run:
```
CREATE USER example_user WITH PASSWORD '123456' SUPERUSER;
```

Followed by the following command to create the database:
```
CREATE DATABASE rag_agent;
```

Then we need allow all privileges to for the user we created with:
```
GRANT ALL PRIVILEGES ON SCHEMA public TO example_user;
```

And for the database:
```
GRANT ALL PRIVILEGES ON DATABASE rag_agent TO example_user;
```

Now we want to connect to the database using:
```
\c rag_agent
```

Now we want to structure the database to store conversations:
```
CREATE TABLE conversations (id SERIAL PRIMARY KEY, timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, prompt TEXT NOT NULL, response TEXT NOT NULL);
```

Lets put a entry into our database:
```
INSERT INTO conversations (timestamp, prompt, response) VALUES (CURRENT_TIMESTAMP, 'the user name', 'The user name is Liam.');
```

To see what is in our database, we can print it by doing the following:
```
SELECT * FROM conversations;
```


If you want to delete everything from the database:
```
DELETE FROM conversations;
```

Now to exit the database
```
\q
```


Lastly, if you get a segmentation fault error, it's likely due to poor memory clean up of the chromadb library. To fix it, run:
```
pkill -f chromadb
```