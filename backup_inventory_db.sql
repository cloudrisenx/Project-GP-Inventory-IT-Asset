--
-- PostgreSQL database dump
--

\restrict YKutFUa8bFjYdmInAwHwnWPIeZ8GFhYK3ADfSTbsAbhndoZlHanP1eJFgsKT78s

-- Dumped from database version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: asset_status; Type: TABLE; Schema: public; Owner: inventory_admin
--

CREATE TABLE public.asset_status (
    status_id integer NOT NULL,
    status_name character varying(50) NOT NULL,
    description text
);


ALTER TABLE public.asset_status OWNER TO inventory_admin;

--
-- Name: asset_status_status_id_seq; Type: SEQUENCE; Schema: public; Owner: inventory_admin
--

CREATE SEQUENCE public.asset_status_status_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.asset_status_status_id_seq OWNER TO inventory_admin;

--
-- Name: asset_status_status_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: inventory_admin
--

ALTER SEQUENCE public.asset_status_status_id_seq OWNED BY public.asset_status.status_id;


--
-- Name: assets; Type: TABLE; Schema: public; Owner: inventory_admin
--

CREATE TABLE public.assets (
    asset_id integer NOT NULL,
    barcode character varying(50),
    product_name character varying(200) NOT NULL,
    model character varying(100),
    manufacturer character varying(100),
    category_id integer,
    location_id integer,
    status_id integer,
    supplier_id integer,
    image_path text,
    serial_number character varying(100),
    purchase_date date,
    purchase_cost numeric(15,2),
    keterangan text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    warranty_info character varying,
    department_id integer,
    qty integer,
    age_asset integer
);


ALTER TABLE public.assets OWNER TO inventory_admin;

--
-- Name: assets_asset_id_seq; Type: SEQUENCE; Schema: public; Owner: inventory_admin
--

CREATE SEQUENCE public.assets_asset_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.assets_asset_id_seq OWNER TO inventory_admin;

--
-- Name: assets_asset_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: inventory_admin
--

ALTER SEQUENCE public.assets_asset_id_seq OWNED BY public.assets.asset_id;


--
-- Name: categories; Type: TABLE; Schema: public; Owner: inventory_admin
--

CREATE TABLE public.categories (
    category_id integer NOT NULL,
    name character varying(100) NOT NULL,
    department_id integer NOT NULL,
    code character varying(50)
);


ALTER TABLE public.categories OWNER TO inventory_admin;

--
-- Name: categories_category_id_seq; Type: SEQUENCE; Schema: public; Owner: inventory_admin
--

CREATE SEQUENCE public.categories_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categories_category_id_seq OWNER TO inventory_admin;

--
-- Name: categories_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: inventory_admin
--

ALTER SEQUENCE public.categories_category_id_seq OWNED BY public.categories.category_id;


--
-- Name: departments; Type: TABLE; Schema: public; Owner: inventory_admin
--

CREATE TABLE public.departments (
    department_id integer NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(50)
);


ALTER TABLE public.departments OWNER TO inventory_admin;

--
-- Name: departments_department_id_seq; Type: SEQUENCE; Schema: public; Owner: inventory_admin
--

CREATE SEQUENCE public.departments_department_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.departments_department_id_seq OWNER TO inventory_admin;

--
-- Name: departments_department_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: inventory_admin
--

ALTER SEQUENCE public.departments_department_id_seq OWNED BY public.departments.department_id;


--
-- Name: locations; Type: TABLE; Schema: public; Owner: inventory_admin
--

CREATE TABLE public.locations (
    location_id integer NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(50)
);


ALTER TABLE public.locations OWNER TO inventory_admin;

--
-- Name: locations_location_id_seq; Type: SEQUENCE; Schema: public; Owner: inventory_admin
--

CREATE SEQUENCE public.locations_location_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.locations_location_id_seq OWNER TO inventory_admin;

--
-- Name: locations_location_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: inventory_admin
--

ALTER SEQUENCE public.locations_location_id_seq OWNED BY public.locations.location_id;


--
-- Name: suppliers; Type: TABLE; Schema: public; Owner: inventory_admin
--

CREATE TABLE public.suppliers (
    supplier_id integer NOT NULL,
    company_name character varying(150) NOT NULL,
    contact_person character varying(100),
    phone character varying(20)
);


ALTER TABLE public.suppliers OWNER TO inventory_admin;

--
-- Name: suppliers_supplier_id_seq; Type: SEQUENCE; Schema: public; Owner: inventory_admin
--

CREATE SEQUENCE public.suppliers_supplier_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.suppliers_supplier_id_seq OWNER TO inventory_admin;

--
-- Name: suppliers_supplier_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: inventory_admin
--

ALTER SEQUENCE public.suppliers_supplier_id_seq OWNED BY public.suppliers.supplier_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: inventory_admin
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(255) NOT NULL,
    nama_lengkap character varying(100),
    role character varying(20) DEFAULT 'user'::character varying
);


ALTER TABLE public.users OWNER TO inventory_admin;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: inventory_admin
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO inventory_admin;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: inventory_admin
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: asset_status status_id; Type: DEFAULT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.asset_status ALTER COLUMN status_id SET DEFAULT nextval('public.asset_status_status_id_seq'::regclass);


--
-- Name: assets asset_id; Type: DEFAULT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.assets ALTER COLUMN asset_id SET DEFAULT nextval('public.assets_asset_id_seq'::regclass);


--
-- Name: categories category_id; Type: DEFAULT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.categories ALTER COLUMN category_id SET DEFAULT nextval('public.categories_category_id_seq'::regclass);


--
-- Name: departments department_id; Type: DEFAULT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.departments ALTER COLUMN department_id SET DEFAULT nextval('public.departments_department_id_seq'::regclass);


--
-- Name: locations location_id; Type: DEFAULT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.locations ALTER COLUMN location_id SET DEFAULT nextval('public.locations_location_id_seq'::regclass);


--
-- Name: suppliers supplier_id; Type: DEFAULT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.suppliers ALTER COLUMN supplier_id SET DEFAULT nextval('public.suppliers_supplier_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: asset_status; Type: TABLE DATA; Schema: public; Owner: inventory_admin
--

COPY public.asset_status (status_id, status_name, description) FROM stdin;
1	Available	\N
2	In Use	\N
3	Broken	\N
4	Services	\N
\.


--
-- Data for Name: assets; Type: TABLE DATA; Schema: public; Owner: inventory_admin
--

COPY public.assets (asset_id, barcode, product_name, model, manufacturer, category_id, location_id, status_id, supplier_id, image_path, serial_number, purchase_date, purchase_cost, keterangan, created_at, warranty_info, department_id, qty, age_asset) FROM stdin;
5	HRD/UNK-16/GS/2026-02/GPB	Iphone 16 Pro Max King 	16 Pro Max King	Apple	7	2	2	4	\N	19291981881291	2026-02-27	2001112.00	\N	2026-02-23 03:48:10.931517	1 Tahun	5	1	60
62	ENG/HW1-INTEL/GS/2026-02/GPB	PC Set i5 10400 	Intel i5 10400	Intel	1	2	2	\N	\N	S1MOCS029945RJC	2026-02-23	3100000.00	Penggantian Unit baru dikarenakan ada konsleting arus listrik di area SSD	2026-02-23 06:31:01.500697	1 Tahun Distributor	1	1	60
1	ENG/HW1-X1/SVR/2024-01/GPB	Laptop ThinkPad X1 Carbon	X1 Carbon Gen 9	Lenovo	1	1	1	1	\N	SN123456789	2024-01-15	18500000.00	Laptop operasional admin IT	2026-02-23 03:19:49.002128	3 Tahun On-Site	1	1	36
2	HRD/NET-M404D/BOF/2023-11/GPB	Printer LaserJet Pro	M404dn	HP	2	5	1	2	\N	PRNT998877	2023-11-20	4500000.00	Printer ruangan HRD	2026-02-23 03:19:49.002128	1 Tahun	5	1	24
3	HK/ELC-KARCH/KPR/2024-02/GPB	Vacuum Cleaner Industrial	Karcher NT 30/1	Karcher	3	6	1	3	\N	VAC-001-GP	2024-02-10	6200000.00	Unit standby lantai 5	2026-02-23 03:19:49.002128	2 Tahun Servis	8	2	48
4	FBP/ROOM-LA/REST/2023-05/GPB	Coffee Machine Espresso	La Marzocco Linea	La Marzocco	4	7	1	4	\N	ESP-9922	2023-05-05	125000000.00	Mesin kopi bar utama	2026-02-23 03:19:49.002128	1 Tahun Sparepart	9	1	60
\.


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: inventory_admin
--

COPY public.categories (category_id, name, department_id, code) FROM stdin;
2	Perangkat Jaringan	1	NET
3	Peralatan Listrik	1	ELC
6	Mesin Dapur	9	KIT
8	Peralatan Makan	10	UTN
5	Alat Kebersihan	8	ALK
141	Laptop Under	9	LU
4	Perlengkapan Kamar 1	8	ROOM
1	Hardware Komputer	1	HW1
\.


--
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: inventory_admin
--

COPY public.departments (department_id, name, code) FROM stdin;
1	ENGINEERING	ENG
2	Jagat Distrik	JD
3	Front Office	FO
4	Sales	SLS
5	HRD	HRD
6	Accounting	ACCT
7	Marketing	MKT
8	House Keeping	HK
9	FBP	FBP
10	FBS	FBS
\.


--
-- Data for Name: locations; Type: TABLE DATA; Schema: public; Owner: inventory_admin
--

COPY public.locations (location_id, name, code) FROM stdin;
1	Ruang Server IT	SVR
3	Gudang F&B	GDG2
4	Lobby Resepsionis	LBY
5	Back Office	BOF
6	Kamar President Suite	KPR
7	Restoran Utama	REST
8	Dapur Tengah	DAP
2	Gudang Utama	GS
\.


--
-- Data for Name: suppliers; Type: TABLE DATA; Schema: public; Owner: inventory_admin
--

COPY public.suppliers (supplier_id, company_name, contact_person, phone) FROM stdin;
1	entercom	admmin	08898989
2	Tech KR	Risen	083838481461
3	Griya persada	Anjas	0828282811
4	Google	Big boss	08887761
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: inventory_admin
--

COPY public.users (id, username, password, nama_lengkap, role) FROM stdin;
2	guest	scrypt:32768:8:1$jwef9QV4RbjNxRmG$51aef46d120bc389f7668649eb0dc4ce1fb5126f56dbcc76d108f5da03e46d14f6ab2f5d7f7aad1af0a56a277fc45506b32a653bae37490518f1e3d5f287e1ba	Akun Tamu	guest
1	admin	scrypt:32768:8:1$GK1UoyUvPfOeC9sM$371a5d61a0e502c8c5c3e4bd30f0fbaf8d975d1d38664cc834b58d3d6b83da5774276792e7adf567a975b306dc357ded11eaa7cddf5e01f5b6540570c2aa807b	Administrator	admin
3	griyapersada	scrypt:32768:8:1$qywUoOOabAxfo4wQ$e68fa16f7f1158ab2b2fc4bd94ad37626caac34d0aacd106ac3c9c11f705ce5e1ceb4e35db11436c530267e83cc3f5b2a431777f1b0f2d7c3fea5bdb57c8a460	Griyapersada Bandungan	admin
4	risenx	scrypt:32768:8:1$4fuk1kyd32ybFCmB$83dcdee26145e0abc32446bac120ce247c894113949f334ab0cb4eb5c42099141dc8db41e3b297fd9a025df9fcab0732a836145373ae3cb173479c7780554c92	CloudRisenx	user
\.


--
-- Name: asset_status_status_id_seq; Type: SEQUENCE SET; Schema: public; Owner: inventory_admin
--

SELECT pg_catalog.setval('public.asset_status_status_id_seq', 3, true);


--
-- Name: assets_asset_id_seq; Type: SEQUENCE SET; Schema: public; Owner: inventory_admin
--

SELECT pg_catalog.setval('public.assets_asset_id_seq', 62, true);


--
-- Name: categories_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: inventory_admin
--

SELECT pg_catalog.setval('public.categories_category_id_seq', 142, true);


--
-- Name: departments_department_id_seq; Type: SEQUENCE SET; Schema: public; Owner: inventory_admin
--

SELECT pg_catalog.setval('public.departments_department_id_seq', 14, true);


--
-- Name: locations_location_id_seq; Type: SEQUENCE SET; Schema: public; Owner: inventory_admin
--

SELECT pg_catalog.setval('public.locations_location_id_seq', 11, true);


--
-- Name: suppliers_supplier_id_seq; Type: SEQUENCE SET; Schema: public; Owner: inventory_admin
--

SELECT pg_catalog.setval('public.suppliers_supplier_id_seq', 3, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: inventory_admin
--

SELECT pg_catalog.setval('public.users_id_seq', 3, true);


--
-- Name: asset_status asset_status_pkey; Type: CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.asset_status
    ADD CONSTRAINT asset_status_pkey PRIMARY KEY (status_id);


--
-- Name: asset_status asset_status_status_name_key; Type: CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.asset_status
    ADD CONSTRAINT asset_status_status_name_key UNIQUE (status_name);


--
-- Name: assets assets_barcode_key; Type: CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_barcode_key UNIQUE (barcode);


--
-- Name: assets assets_pkey; Type: CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_pkey PRIMARY KEY (asset_id);


--
-- Name: categories categories_code_key; Type: CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_code_key UNIQUE (code);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);


--
-- Name: departments departments_code_key; Type: CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_code_key UNIQUE (code);


--
-- Name: departments departments_name_key; Type: CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_name_key UNIQUE (name);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (department_id);


--
-- Name: locations locations_code_key; Type: CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_code_key UNIQUE (code);


--
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (location_id);


--
-- Name: suppliers suppliers_pkey; Type: CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.suppliers
    ADD CONSTRAINT suppliers_pkey PRIMARY KEY (supplier_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: idx_department_id; Type: INDEX; Schema: public; Owner: inventory_admin
--

CREATE INDEX idx_department_id ON public.categories USING btree (department_id);


--
-- Name: assets assets_supplier_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT assets_supplier_id_fkey FOREIGN KEY (supplier_id) REFERENCES public.suppliers(supplier_id);


--
-- Name: assets fk_department; Type: FK CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT fk_department FOREIGN KEY (department_id) REFERENCES public.departments(department_id) ON DELETE CASCADE;


--
-- Name: categories fk_department; Type: FK CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT fk_department FOREIGN KEY (department_id) REFERENCES public.departments(department_id) ON DELETE CASCADE;


--
-- Name: assets fk_location; Type: FK CONSTRAINT; Schema: public; Owner: inventory_admin
--

ALTER TABLE ONLY public.assets
    ADD CONSTRAINT fk_location FOREIGN KEY (location_id) REFERENCES public.locations(location_id) ON DELETE SET NULL;


--
-- PostgreSQL database dump complete
--

\unrestrict YKutFUa8bFjYdmInAwHwnWPIeZ8GFhYK3ADfSTbsAbhndoZlHanP1eJFgsKT78s

