-- Ensure user exists
DO
$$
BEGIN
   IF NOT EXISTS (
      SELECT FROM pg_catalog.pg_roles WHERE rolname = 'sentiment_user'
   ) THEN
      CREATE ROLE sentiment_user LOGIN PASSWORD 'postgres123';
   END IF;
END
$$;

-- Grant privileges on existing database
GRANT ALL PRIVILEGES ON DATABASE sentiment_db TO sentiment_user;
