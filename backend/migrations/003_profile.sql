CREATE TABLE profile (
  lock                 boolean PRIMARY KEY DEFAULT true CHECK (lock = true),
  name                 text NOT NULL DEFAULT '',
  title                text NOT NULL DEFAULT '',
  tagline              text,
  availability_status  text,
  is_open_to_work      boolean DEFAULT false,
  location             text,
  email                text,
  github_url           text,
  linkedin_url         text,
  calendly_url         text,
  social_links         jsonb,
  ethics_statement     text,
  communication_style  text,
  work_preference      text,
  fun_fact             text,
  updated_at           timestamp DEFAULT now()
);

INSERT INTO profile (lock) VALUES (true);
