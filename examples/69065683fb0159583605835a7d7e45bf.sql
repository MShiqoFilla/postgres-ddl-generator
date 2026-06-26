CREATE SCHEMA IF NOT EXISTS test;

CREATE SEQUENCE test.customers_id_seq;
CREATE TABLE test.customers (
    id integer NOT NULL DEFAULT nextval('test.customers_id_seq'::regclass),
    username varchar(50) NOT NULL,
    email varchar(100) NOT NULL,
    address text,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT customers_pkey PRIMARY KEY (id),
    CONSTRAINT customers_email_key UNIQUE (email)
);

CREATE TABLE test.departments (
    id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
    name text NOT NULL,
    CONSTRAINT departments_pkey PRIMARY KEY (id)
);

CREATE SEQUENCE test.users_id_seq;
CREATE TABLE test.users (
    id integer NOT NULL DEFAULT nextval('test.users_id_seq'::regclass),
    username varchar(50) NOT NULL,
    email varchar(100) NOT NULL,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT users_pkey PRIMARY KEY (id),
    CONSTRAINT users_email_key UNIQUE (email)
);

CREATE TABLE test.employees (
    id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
    employee_code varchar(20) NOT NULL,
    email varchar(255) NOT NULL,
    full_name text NOT NULL,
    age integer,
    department_id integer,
    salary numeric(12, 2) DEFAULT 0,
    created_at timestamp without time zone DEFAULT now(),
    CONSTRAINT employees_pkey PRIMARY KEY (id),
    CONSTRAINT employees_email_key UNIQUE (email),
    CONSTRAINT employees_employee_code_key UNIQUE (employee_code),
    CONSTRAINT employees_age_check CHECK ((age >= 18)),
    CONSTRAINT employees_department_fk FOREIGN KEY (department_id) REFERENCES test.departments(id) ON UPDATE CASCADE ON DELETE SET NULL
);