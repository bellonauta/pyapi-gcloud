--
-- PostgreSQL database dump
--

-- Dumped from database version 13.2
-- Dumped by pg_dump version 13.3

-- Started on 2021-06-02 16:40:04

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
-- TOC entry 200 (class 1259 OID 16426)
-- Name: consumer; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.consumer (
    id integer NOT NULL,
    name character varying(60),
    phone character varying(15),
    email character varying(100),
    active character varying(1)
);


--
-- TOC entry 201 (class 1259 OID 16429)
-- Name: consumer_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.consumer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3636 (class 0 OID 0)
-- Dependencies: 201
-- Name: consumer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.consumer_id_seq OWNED BY public.consumer.id;


--
-- TOC entry 202 (class 1259 OID 16431)
-- Name: manufacturer; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.manufacturer (
    id integer NOT NULL,
    name character varying(60)
);


--
-- TOC entry 203 (class 1259 OID 16434)
-- Name: manufacturer_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.manufacturer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3637 (class 0 OID 0)
-- Dependencies: 203
-- Name: manufacturer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.manufacturer_id_seq OWNED BY public.manufacturer.id;


--
-- TOC entry 204 (class 1259 OID 16436)
-- Name: order; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public."order" (
    id integer NOT NULL,
    status character varying(30),
    consumer integer,
    payment_mode character varying(30),
    payment_amount numeric(12,2),
    payment_installments integer,
    payment_installment_value numeric(11,2),
    delivery_mode character varying(40)
);


--
-- TOC entry 205 (class 1259 OID 16439)
-- Name: order_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.order_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3638 (class 0 OID 0)
-- Dependencies: 205
-- Name: order_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.order_id_seq OWNED BY public."order".id;


--
-- TOC entry 206 (class 1259 OID 16441)
-- Name: orderproduct; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orderproduct (
    order_id integer NOT NULL,
    product_id integer NOT NULL,
    product_units numeric(7,3),
    product_unit_price numeric(11,2),
    product_unit_amount numeric(12,2)
);


--
-- TOC entry 207 (class 1259 OID 16444)
-- Name: product; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.product (
    id integer NOT NULL,
    name character varying(60),
    description character varying,
    barcode character varying(100),
    unitprice numeric(11,2),
    active character varying(1)
);


--
-- TOC entry 208 (class 1259 OID 16450)
-- Name: product_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- TOC entry 3639 (class 0 OID 0)
-- Dependencies: 208
-- Name: product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.product_id_seq OWNED BY public.product.id;


--
-- TOC entry 209 (class 1259 OID 16452)
-- Name: productmanufacturer; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.productmanufacturer (
    product_id integer NOT NULL,
    manufacturer_id integer NOT NULL,
    active character varying(1)
);


--
-- TOC entry 3475 (class 2604 OID 16455)
-- Name: consumer id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.consumer ALTER COLUMN id SET DEFAULT nextval('public.consumer_id_seq'::regclass);


--
-- TOC entry 3476 (class 2604 OID 16456)
-- Name: manufacturer id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.manufacturer ALTER COLUMN id SET DEFAULT nextval('public.manufacturer_id_seq'::regclass);


--
-- TOC entry 3477 (class 2604 OID 16457)
-- Name: order id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."order" ALTER COLUMN id SET DEFAULT nextval('public.order_id_seq'::regclass);


--
-- TOC entry 3478 (class 2604 OID 16458)
-- Name: product id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product ALTER COLUMN id SET DEFAULT nextval('public.product_id_seq'::regclass);


--
-- TOC entry 3621 (class 0 OID 16426)
-- Dependencies: 200
-- Data for Name: consumer; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.consumer (id, name, phone, email, active) FROM stdin;
\.


--
-- TOC entry 3623 (class 0 OID 16431)
-- Dependencies: 202
-- Data for Name: manufacturer; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.manufacturer (id, name) FROM stdin;
\.


--
-- TOC entry 3625 (class 0 OID 16436)
-- Dependencies: 204
-- Data for Name: order; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public."order" (id, status, consumer, payment_mode, payment_amount, payment_installments, payment_installment_value, delivery_mode) FROM stdin;
\.


--
-- TOC entry 3627 (class 0 OID 16441)
-- Dependencies: 206
-- Data for Name: orderproduct; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.orderproduct (order_id, product_id, product_units, product_unit_price, product_unit_amount) FROM stdin;
\.


--
-- TOC entry 3628 (class 0 OID 16444)
-- Dependencies: 207
-- Data for Name: product; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.product (id, name, description, barcode, unitprice, active) FROM stdin;
\.


--
-- TOC entry 3630 (class 0 OID 16452)
-- Dependencies: 209
-- Data for Name: productmanufacturer; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.productmanufacturer (product_id, manufacturer_id, active) FROM stdin;
\.


--
-- TOC entry 3640 (class 0 OID 0)
-- Dependencies: 201
-- Name: consumer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.consumer_id_seq', 1, false);


--
-- TOC entry 3641 (class 0 OID 0)
-- Dependencies: 203
-- Name: manufacturer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.manufacturer_id_seq', 185, true);


--
-- TOC entry 3642 (class 0 OID 0)
-- Dependencies: 205
-- Name: order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.order_id_seq', 1, false);


--
-- TOC entry 3643 (class 0 OID 0)
-- Dependencies: 208
-- Name: product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.product_id_seq', 190, true);


--
-- TOC entry 3480 (class 2606 OID 16460)
-- Name: consumer consumer_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.consumer
    ADD CONSTRAINT consumer_pkey PRIMARY KEY (id);


--
-- TOC entry 3482 (class 2606 OID 16462)
-- Name: manufacturer manufacturer_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.manufacturer
    ADD CONSTRAINT manufacturer_pkey PRIMARY KEY (id);


--
-- TOC entry 3484 (class 2606 OID 16464)
-- Name: order order_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public."order"
    ADD CONSTRAINT order_pkey PRIMARY KEY (id);


--
-- TOC entry 3486 (class 2606 OID 16466)
-- Name: orderproduct orderproduct_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orderproduct
    ADD CONSTRAINT orderproduct_pkey PRIMARY KEY (order_id, product_id);


--
-- TOC entry 3488 (class 2606 OID 16468)
-- Name: product product_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_pkey PRIMARY KEY (id);


--
-- TOC entry 3490 (class 2606 OID 16470)
-- Name: productmanufacturer productmanufacturer_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.productmanufacturer
    ADD CONSTRAINT productmanufacturer_pkey PRIMARY KEY (product_id, manufacturer_id);


-- Completed on 2021-06-02 16:40:06

--
-- PostgreSQL database dump complete
--

