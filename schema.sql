--
-- PostgreSQL database dump
--

-- Dumped from database version 12.2
-- Dumped by pg_dump version 12.2

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

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: interaction_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.interaction_status AS ENUM (
    'success',
    'failed',
    'pending',
    'no_response'
);


ALTER TYPE public.interaction_status OWNER TO postgres;

--
-- Name: interaction_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.interaction_type AS ENUM (
    'call',
    'sms',
    'email',
    'whatsapp',
    'telegram'
);


ALTER TYPE public.interaction_type OWNER TO postgres;

--
-- Name: project_status; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.project_status AS ENUM (
    'planning',
    'in_progress',
    'completed',
    'on_hold',
    'cancelled'
);


ALTER TYPE public.project_status OWNER TO postgres;

--
-- Name: project_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.project_type AS ENUM (
    'residential',
    'commercial',
    'mixed_use',
    'land'
);


ALTER TYPE public.project_type OWNER TO postgres;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    tenant_id uuid NOT NULL,
    action character varying NOT NULL,
    resource_type character varying NOT NULL,
    resource_id uuid NOT NULL,
    details jsonb,
    user_id uuid,
    "timestamp" timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone,
    customer_id uuid
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- Name: call_interactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.call_interactions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    interaction_id uuid,
    call_sid character varying,
    recording_url character varying,
    transcript text,
    keypad_inputs jsonb,
    menu_selections jsonb,
    call_quality_metrics jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone
);


ALTER TABLE public.call_interactions OWNER TO postgres;

--
-- Name: communication_preferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.communication_preferences (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    customer_id uuid,
    enabled_channels character varying[] DEFAULT ARRAY['sms'::text, 'email'::text],
    default_channel character varying DEFAULT 'sms'::character varying,
    sms_enabled boolean DEFAULT true,
    email_enabled boolean DEFAULT true,
    whatsapp_enabled boolean DEFAULT false,
    telegram_enabled boolean DEFAULT false,
    voice_enabled boolean DEFAULT false,
    sms_settings jsonb,
    email_settings jsonb,
    whatsapp_settings jsonb,
    telegram_settings jsonb,
    voice_settings jsonb,
    message_templates jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone,
    push_enabled boolean DEFAULT true,
    push_frequency character varying(20) DEFAULT 'daily'::character varying,
    email_frequency character varying(20) DEFAULT 'daily'::character varying,
    sms_frequency character varying(20) DEFAULT 'daily'::character varying,
    quiet_hours_start character varying(5) DEFAULT '22:00'::character varying,
    quiet_hours_end character varying(5) DEFAULT '08:00'::character varying,
    timezone character varying(50) DEFAULT 'UTC'::character varying
);


ALTER TABLE public.communication_preferences OWNER TO postgres;

--
-- Name: customers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone,
    domain character varying(255)
);


ALTER TABLE public.customers OWNER TO postgres;

--
-- Name: interaction_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interaction_logs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    lead_id uuid,
    customer_id uuid,
    interaction_type public.interaction_type,
    status public.interaction_status,
    start_time timestamp with time zone,
    end_time timestamp with time zone,
    duration integer,
    user_input jsonb,
    error_message text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone,
    response_time double precision
);


ALTER TABLE public.interaction_logs OWNER TO postgres;

--
-- Name: lead_scores; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.lead_scores (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    lead_id uuid,
    score double precision DEFAULT 0.0,
    last_updated timestamp with time zone,
    scoring_factors jsonb,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone
);


ALTER TABLE public.lead_scores OWNER TO postgres;

--
-- Name: leads; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.leads (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying NOT NULL,
    phone character varying,
    email character varying,
    location character varying,
    budget character varying,
    property_type character varying,
    customer_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone,
    source character varying(255),
    status character varying(50) DEFAULT 'new'::character varying,
    notes text,
    assigned_to uuid,
    first_name character varying(255),
    last_name character varying(255),
    created_by uuid,
    updated_by uuid
);


ALTER TABLE public.leads OWNER TO postgres;

--
-- Name: login_attempts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.login_attempts (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid,
    email character varying NOT NULL,
    ip_address character varying NOT NULL,
    user_agent character varying,
    success boolean DEFAULT false,
    attempt_time timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    failure_reason character varying
);


ALTER TABLE public.login_attempts OWNER TO postgres;

--
-- Name: message_interactions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.message_interactions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    interaction_id uuid,
    message_id character varying,
    content text,
    response_content text,
    response_time integer,
    delivery_status character varying,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone
);


ALTER TABLE public.message_interactions OWNER TO postgres;

--
-- Name: mfa_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mfa_settings (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    is_enabled boolean DEFAULT false,
    secret_key character varying,
    backup_codes character varying[],
    phone_number character varying,
    email character varying,
    preferred_method character varying DEFAULT 'totp'::character varying,
    last_used timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone
);


ALTER TABLE public.mfa_settings OWNER TO postgres;

--
-- Name: outreach_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.outreach_logs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    lead_id uuid,
    channel character varying NOT NULL,
    status character varying NOT NULL,
    message text,
    customer_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone
);


ALTER TABLE public.outreach_logs OWNER TO postgres;

--
-- Name: password_resets; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.password_resets (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    token character varying NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    is_used boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.password_resets OWNER TO postgres;

--
-- Name: permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.permissions (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    action character varying NOT NULL,
    resource character varying NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone
);


ALTER TABLE public.permissions OWNER TO postgres;

--
-- Name: project_leads; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.project_leads (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    project_id uuid NOT NULL,
    lead_id uuid NOT NULL,
    assigned_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.project_leads OWNER TO postgres;

--
-- Name: projects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.projects (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying(100) NOT NULL,
    description character varying(500),
    type public.project_type NOT NULL,
    status public.project_status DEFAULT 'planning'::public.project_status NOT NULL,
    location character varying(200) NOT NULL,
    total_units integer,
    price_range character varying(100),
    amenities jsonb,
    completion_date timestamp with time zone,
    customer_id uuid NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone,
    property_type character varying
);


ALTER TABLE public.projects OWNER TO postgres;

--
-- Name: real_estate_buyers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.real_estate_buyers (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying NOT NULL,
    phone character varying,
    email character varying,
    location character varying,
    budget character varying,
    property_type character varying,
    customer_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone
);


ALTER TABLE public.real_estate_buyers OWNER TO postgres;

--
-- Name: real_estate_projects; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.real_estate_projects (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying NOT NULL,
    price character varying,
    size character varying,
    type character varying,
    builder character varying,
    location character varying,
    completion_date character varying,
    customer_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone
);


ALTER TABLE public.real_estate_projects OWNER TO postgres;

--
-- Name: refresh_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.refresh_tokens (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    token character varying(255) NOT NULL,
    user_id uuid NOT NULL,
    customer_id uuid NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    is_revoked boolean DEFAULT false,
    device_info text
);


ALTER TABLE public.refresh_tokens OWNER TO postgres;

--
-- Name: role_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.role_permissions (
    role_id uuid NOT NULL,
    permission_id uuid NOT NULL
);


ALTER TABLE public.role_permissions OWNER TO postgres;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying NOT NULL,
    description text,
    customer_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- Name: scraped_leads; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scraped_leads (
    id uuid DEFAULT public.gen_random_uuid() NOT NULL,
    customer_id uuid NOT NULL,
    lead_type character varying NOT NULL,
    data jsonb NOT NULL,
    source character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.scraped_leads OWNER TO postgres;

--
-- Name: scraping_configs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.scraping_configs (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    customer_id uuid,
    enabled_sources character varying[] DEFAULT ARRAY['magicbricks'::text, '99acres'::text, 'housing'::text],
    scraping_delay integer DEFAULT 2,
    max_retries integer DEFAULT 3,
    proxy_enabled boolean DEFAULT false,
    proxy_url character varying,
    user_agent character varying,
    max_pages_per_source integer DEFAULT 5,
    auto_scrape_enabled boolean DEFAULT false,
    auto_scrape_interval integer DEFAULT 24,
    locations character varying[] DEFAULT ARRAY[]::character varying[],
    property_types character varying[] DEFAULT ARRAY[]::character varying[],
    price_range_min double precision,
    price_range_max double precision,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone,
    CONSTRAINT valid_price_range CHECK (((price_range_min IS NULL) OR (price_range_max IS NULL) OR (price_range_min <= price_range_max)))
);


ALTER TABLE public.scraping_configs OWNER TO postgres;

--
-- Name: tenants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tenants (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    name character varying NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone
);


ALTER TABLE public.tenants OWNER TO postgres;

--
-- Name: user_communication_preferences; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_communication_preferences (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    user_id uuid NOT NULL,
    communication_preferences_id uuid NOT NULL,
    channel character varying NOT NULL,
    is_enabled boolean DEFAULT true,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone
);


ALTER TABLE public.user_communication_preferences OWNER TO postgres;

--
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_roles (
    user_id uuid NOT NULL,
    role_id uuid NOT NULL
);


ALTER TABLE public.user_roles OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    email character varying NOT NULL,
    password_hash character varying NOT NULL,
    is_active boolean DEFAULT true,
    is_superuser boolean DEFAULT false,
    customer_id uuid,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone,
    username character varying NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: COLUMN users.username; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.username IS 'Username for login (unique, not null)';


--
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- Name: call_interactions call_interactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.call_interactions
    ADD CONSTRAINT call_interactions_pkey PRIMARY KEY (id);


--
-- Name: communication_preferences communication_preferences_customer_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.communication_preferences
    ADD CONSTRAINT communication_preferences_customer_id_key UNIQUE (customer_id);


--
-- Name: communication_preferences communication_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.communication_preferences
    ADD CONSTRAINT communication_preferences_pkey PRIMARY KEY (id);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- Name: interaction_logs interaction_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_logs
    ADD CONSTRAINT interaction_logs_pkey PRIMARY KEY (id);


--
-- Name: lead_scores lead_scores_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lead_scores
    ADD CONSTRAINT lead_scores_pkey PRIMARY KEY (id);


--
-- Name: leads leads_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leads
    ADD CONSTRAINT leads_pkey PRIMARY KEY (id);


--
-- Name: login_attempts login_attempts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.login_attempts
    ADD CONSTRAINT login_attempts_pkey PRIMARY KEY (id);


--
-- Name: message_interactions message_interactions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message_interactions
    ADD CONSTRAINT message_interactions_pkey PRIMARY KEY (id);


--
-- Name: mfa_settings mfa_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mfa_settings
    ADD CONSTRAINT mfa_settings_pkey PRIMARY KEY (id);


--
-- Name: mfa_settings mfa_settings_user_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mfa_settings
    ADD CONSTRAINT mfa_settings_user_id_key UNIQUE (user_id);


--
-- Name: outreach_logs outreach_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.outreach_logs
    ADD CONSTRAINT outreach_logs_pkey PRIMARY KEY (id);


--
-- Name: password_resets password_resets_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT password_resets_pkey PRIMARY KEY (id);


--
-- Name: password_resets password_resets_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT password_resets_token_key UNIQUE (token);


--
-- Name: permissions permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.permissions
    ADD CONSTRAINT permissions_pkey PRIMARY KEY (id);


--
-- Name: project_leads project_leads_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_leads
    ADD CONSTRAINT project_leads_pkey PRIMARY KEY (id);


--
-- Name: project_leads project_leads_project_id_lead_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_leads
    ADD CONSTRAINT project_leads_project_id_lead_id_key UNIQUE (project_id, lead_id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: real_estate_buyers real_estate_buyers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.real_estate_buyers
    ADD CONSTRAINT real_estate_buyers_pkey PRIMARY KEY (id);


--
-- Name: real_estate_projects real_estate_projects_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.real_estate_projects
    ADD CONSTRAINT real_estate_projects_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- Name: refresh_tokens refresh_tokens_token_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_token_key UNIQUE (token);


--
-- Name: role_permissions role_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_pkey PRIMARY KEY (role_id, permission_id);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: scraped_leads scraped_leads_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scraped_leads
    ADD CONSTRAINT scraped_leads_pkey PRIMARY KEY (id);


--
-- Name: scraping_configs scraping_configs_customer_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scraping_configs
    ADD CONSTRAINT scraping_configs_customer_id_key UNIQUE (customer_id);


--
-- Name: scraping_configs scraping_configs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scraping_configs
    ADD CONSTRAINT scraping_configs_pkey PRIMARY KEY (id);


--
-- Name: tenants tenants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tenants
    ADD CONSTRAINT tenants_pkey PRIMARY KEY (id);


--
-- Name: leads unique_lead_email; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leads
    ADD CONSTRAINT unique_lead_email UNIQUE (email);


--
-- Name: leads unique_lead_phone; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leads
    ADD CONSTRAINT unique_lead_phone UNIQUE (phone);


--
-- Name: user_communication_preferences user_communication_preference_user_id_communication_prefere_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_communication_preferences
    ADD CONSTRAINT user_communication_preference_user_id_communication_prefere_key UNIQUE (user_id, communication_preferences_id, channel);


--
-- Name: user_communication_preferences user_communication_preferences_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_communication_preferences
    ADD CONSTRAINT user_communication_preferences_pkey PRIMARY KEY (id);


--
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (user_id, role_id);


--
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_audit_logs_resource_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_logs_resource_id ON public.audit_logs USING btree (resource_id);


--
-- Name: idx_audit_logs_tenant_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_logs_tenant_id ON public.audit_logs USING btree (tenant_id);


--
-- Name: idx_audit_logs_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_audit_logs_user_id ON public.audit_logs USING btree (user_id);


--
-- Name: idx_interaction_logs_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_interaction_logs_customer_id ON public.interaction_logs USING btree (customer_id);


--
-- Name: idx_interaction_logs_lead_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_interaction_logs_lead_id ON public.interaction_logs USING btree (lead_id);


--
-- Name: idx_leads_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_leads_customer_id ON public.leads USING btree (customer_id);


--
-- Name: idx_leads_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_leads_email ON public.leads USING btree (email);


--
-- Name: idx_leads_phone; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_leads_phone ON public.leads USING btree (phone);


--
-- Name: idx_login_attempts_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_login_attempts_email ON public.login_attempts USING btree (email);


--
-- Name: idx_login_attempts_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_login_attempts_user_id ON public.login_attempts USING btree (user_id);


--
-- Name: idx_outreach_logs_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_outreach_logs_customer_id ON public.outreach_logs USING btree (customer_id);


--
-- Name: idx_outreach_logs_lead_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_outreach_logs_lead_id ON public.outreach_logs USING btree (lead_id);


--
-- Name: idx_project_leads_lead_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_project_leads_lead_id ON public.project_leads USING btree (lead_id);


--
-- Name: idx_project_leads_project_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_project_leads_project_id ON public.project_leads USING btree (project_id);


--
-- Name: idx_projects_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_projects_customer_id ON public.projects USING btree (customer_id);


--
-- Name: idx_refresh_tokens_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_refresh_tokens_customer_id ON public.refresh_tokens USING btree (customer_id);


--
-- Name: idx_refresh_tokens_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_refresh_tokens_user_id ON public.refresh_tokens USING btree (user_id);


--
-- Name: idx_users_customer_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_customer_id ON public.users USING btree (customer_id);


--
-- Name: idx_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_users_email ON public.users USING btree (email);


--
-- Name: idx_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX idx_users_username ON public.users USING btree (username);


--
-- Name: audit_logs update_audit_logs_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_audit_logs_updated_at BEFORE UPDATE ON public.audit_logs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: call_interactions update_call_interactions_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_call_interactions_updated_at BEFORE UPDATE ON public.call_interactions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: communication_preferences update_communication_preferences_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_communication_preferences_updated_at BEFORE UPDATE ON public.communication_preferences FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: customers update_customers_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON public.customers FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: interaction_logs update_interaction_logs_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_interaction_logs_updated_at BEFORE UPDATE ON public.interaction_logs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: lead_scores update_lead_scores_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_lead_scores_updated_at BEFORE UPDATE ON public.lead_scores FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: leads update_leads_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_leads_updated_at BEFORE UPDATE ON public.leads FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: login_attempts update_login_attempts_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_login_attempts_updated_at BEFORE UPDATE ON public.login_attempts FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: message_interactions update_message_interactions_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_message_interactions_updated_at BEFORE UPDATE ON public.message_interactions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: mfa_settings update_mfa_settings_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_mfa_settings_updated_at BEFORE UPDATE ON public.mfa_settings FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: outreach_logs update_outreach_logs_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_outreach_logs_updated_at BEFORE UPDATE ON public.outreach_logs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: password_resets update_password_resets_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_password_resets_updated_at BEFORE UPDATE ON public.password_resets FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: permissions update_permissions_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_permissions_updated_at BEFORE UPDATE ON public.permissions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: project_leads update_project_leads_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_project_leads_updated_at BEFORE UPDATE ON public.project_leads FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: projects update_projects_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON public.projects FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: real_estate_buyers update_real_estate_buyers_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_real_estate_buyers_updated_at BEFORE UPDATE ON public.real_estate_buyers FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: real_estate_projects update_real_estate_projects_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_real_estate_projects_updated_at BEFORE UPDATE ON public.real_estate_projects FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: refresh_tokens update_refresh_tokens_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_refresh_tokens_updated_at BEFORE UPDATE ON public.refresh_tokens FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: role_permissions update_role_permissions_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_role_permissions_updated_at BEFORE UPDATE ON public.role_permissions FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: roles update_roles_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_roles_updated_at BEFORE UPDATE ON public.roles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: scraping_configs update_scraping_configs_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_scraping_configs_updated_at BEFORE UPDATE ON public.scraping_configs FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: tenants update_tenants_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON public.tenants FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: user_roles update_user_roles_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_user_roles_updated_at BEFORE UPDATE ON public.user_roles FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: users update_users_updated_at; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: audit_logs audit_logs_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: audit_logs audit_logs_tenant_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES public.tenants(id);


--
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: call_interactions call_interactions_interaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.call_interactions
    ADD CONSTRAINT call_interactions_interaction_id_fkey FOREIGN KEY (interaction_id) REFERENCES public.interaction_logs(id);


--
-- Name: communication_preferences communication_preferences_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.communication_preferences
    ADD CONSTRAINT communication_preferences_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: interaction_logs interaction_logs_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_logs
    ADD CONSTRAINT interaction_logs_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: interaction_logs interaction_logs_lead_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interaction_logs
    ADD CONSTRAINT interaction_logs_lead_id_fkey FOREIGN KEY (lead_id) REFERENCES public.leads(id);


--
-- Name: lead_scores lead_scores_lead_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.lead_scores
    ADD CONSTRAINT lead_scores_lead_id_fkey FOREIGN KEY (lead_id) REFERENCES public.leads(id);


--
-- Name: leads leads_assigned_to_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leads
    ADD CONSTRAINT leads_assigned_to_fkey FOREIGN KEY (assigned_to) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: leads leads_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.leads
    ADD CONSTRAINT leads_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: login_attempts login_attempts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.login_attempts
    ADD CONSTRAINT login_attempts_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: message_interactions message_interactions_interaction_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message_interactions
    ADD CONSTRAINT message_interactions_interaction_id_fkey FOREIGN KEY (interaction_id) REFERENCES public.interaction_logs(id);


--
-- Name: mfa_settings mfa_settings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mfa_settings
    ADD CONSTRAINT mfa_settings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: outreach_logs outreach_logs_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.outreach_logs
    ADD CONSTRAINT outreach_logs_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: outreach_logs outreach_logs_lead_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.outreach_logs
    ADD CONSTRAINT outreach_logs_lead_id_fkey FOREIGN KEY (lead_id) REFERENCES public.leads(id);


--
-- Name: password_resets password_resets_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_resets
    ADD CONSTRAINT password_resets_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: project_leads project_leads_lead_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_leads
    ADD CONSTRAINT project_leads_lead_id_fkey FOREIGN KEY (lead_id) REFERENCES public.leads(id);


--
-- Name: project_leads project_leads_project_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.project_leads
    ADD CONSTRAINT project_leads_project_id_fkey FOREIGN KEY (project_id) REFERENCES public.projects(id);


--
-- Name: projects projects_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.projects
    ADD CONSTRAINT projects_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: real_estate_buyers real_estate_buyers_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.real_estate_buyers
    ADD CONSTRAINT real_estate_buyers_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: real_estate_projects real_estate_projects_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.real_estate_projects
    ADD CONSTRAINT real_estate_projects_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: refresh_tokens refresh_tokens_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: refresh_tokens refresh_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: role_permissions role_permissions_permission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_permission_id_fkey FOREIGN KEY (permission_id) REFERENCES public.permissions(id);


--
-- Name: role_permissions role_permissions_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.role_permissions
    ADD CONSTRAINT role_permissions_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: roles roles_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: scraped_leads scraped_leads_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scraped_leads
    ADD CONSTRAINT scraped_leads_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id) ON DELETE CASCADE;


--
-- Name: scraping_configs scraping_configs_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.scraping_configs
    ADD CONSTRAINT scraping_configs_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- Name: user_communication_preferences user_communication_preference_communication_preferences_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_communication_preferences
    ADD CONSTRAINT user_communication_preference_communication_preferences_id_fkey FOREIGN KEY (communication_preferences_id) REFERENCES public.communication_preferences(id);


--
-- Name: user_communication_preferences user_communication_preferences_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_communication_preferences
    ADD CONSTRAINT user_communication_preferences_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: users users_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(id);


--
-- PostgreSQL database dump complete
--

