A few lines of code for restarting the database.
```
sudo -u postgres psql
\c rag_agent
DELETE FROM conversations;
INSERT INTO conversations (timestamp, prompt, response) VALUES (CURRENT_TIMESTAMP, 'the user name', 'The user name is Liam.');
\q
pkill -f chromadb
```