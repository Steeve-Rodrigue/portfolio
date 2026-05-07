CREATE TABLE projects (
    id                uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    slug              text UNIQUE NOT NULL,
    title             text NOT NULL,
    problem_statement text,
    methodology       text,
    results_impact    text,
    metrics           jsonb,
    tech_stack        text[] DEFAULT '{}',
    categories        text[] DEFAULT '{}',
    github_url        text,
    demo_url          text,
    notebook_url      text,
    thumbnail_url     text,
    has_ml_demo       boolean DEFAULT false,
    ml_endpoint       text,
    featured          boolean DEFAULT false,
    display_order     int DEFAULT 0,
    created_at        timestamp DEFAULT now()
);

CREATE INDEX idx_projects_featured      ON projects(featured);
CREATE INDEX idx_projects_display_order ON projects(display_order);
