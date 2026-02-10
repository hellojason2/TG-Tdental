-- Auto-generated database schema from SPA scraping
-- Source: https://tamdentist.tdental.vn
-- Generated from 10 inferred tables


-- Source endpoint: GET /Web/Session/GetSessionInfo
CREATE TABLE session (
    id SERIAL NOT NULL,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    userpartnerid VARCHAR(255) NOT NULL,
    partnerid VARCHAR(255) NOT NULL,
    usercompanies JSONB NOT NULL,
    expirationdate TIMESTAMP NOT NULL,
    isadmin BOOLEAN NOT NULL,
    permissions JSONB NOT NULL,
    groups JSONB NOT NULL,
    rules JSONB NOT NULL,
    modules JSONB NOT NULL,
    settings VARCHAR(255) NOT NULL,
    expiredin INTEGER NOT NULL,
    tenantid VARCHAR(255) NOT NULL,
    isuppercasepartnername BOOLEAN NOT NULL,
    features JSONB NOT NULL,
    totpenabled BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Source endpoint: GET /api/IrConfigParameters/GetParam
CREATE TABLE irconfigparameters (
    id SERIAL PRIMARY KEY,
    value VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Source endpoint: GET /mail/init_messaging
CREATE TABLE mail (
    id SERIAL PRIMARY KEY,
    needactioninboxcount INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Source endpoint: POST /api/Partnercategories/Autocomplete
CREATE TABLE autocomplete (
    id SERIAL NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    completename VARCHAR(255) NULL,
    color VARCHAR(255) NOT NULL,
    type VARCHAR(255) NOT NULL,
    iscollaborators BOOLEAN NOT NULL,
    isactive BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Source endpoint: GET /api/Companies
CREATE TABLE companies (
    id SERIAL NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    logo VARCHAR(255) NULL,
    active BOOLEAN NOT NULL,
    ishead BOOLEAN NOT NULL,
    periodlockdate TIMESTAMP NULL,
    medicalfacilitycode VARCHAR(255) NULL,
    hotline VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NULL,
    address VARCHAR(255) NOT NULL,
    addressv2 VARCHAR(255) NOT NULL,
    usedaddressv2 BOOLEAN NOT NULL,
    taxcode VARCHAR(255) NULL,
    taxunitname VARCHAR(255) NULL,
    taxunitaddress VARCHAR(255) NULL,
    taxbankname VARCHAR(255) NULL,
    taxbankaccount VARCHAR(255) NULL,
    taxphone VARCHAR(20) NULL,
    householdbusinesses JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Source endpoint: GET /api/productcategories
CREATE TABLE productcategories (
    id SERIAL NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    completename VARCHAR(255) NOT NULL,
    parentid VARCHAR(255) NULL,
    parent VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Source endpoint: POST /api/products/autocomplete2
CREATE TABLE autocomplete2 (
    id SERIAL NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    namenosign VARCHAR(255) NOT NULL,
    defaultcode VARCHAR(255) NOT NULL,
    priceunit DECIMAL(12,2) NULL,
    purchaseprice DECIMAL(12,2) NULL,
    standardprice DECIMAL(12,2) NOT NULL,
    categid UUID NOT NULL,
    categ JSONB NOT NULL,
    type VARCHAR(255) NOT NULL,
    type2 VARCHAR(255) NOT NULL,
    listprice DECIMAL(12,2) NOT NULL,
    firm VARCHAR(255) NULL,
    laboprice DECIMAL(12,2) NULL,
    uomid UUID NOT NULL,
    uom JSONB NOT NULL,
    quantity DECIMAL(12,2) NOT NULL,
    islabo BOOLEAN NOT NULL,
    displayname VARCHAR(255) NOT NULL,
    stepconfigs VARCHAR(255) NULL,
    taxid VARCHAR(255) NULL,
    tax VARCHAR(255) NULL,
    companyname VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Source endpoint: GET /api/Partners/GetPagedPartnersCustomer
CREATE TABLE getpagedpartnerscustomer (
    id SERIAL NOT NULL PRIMARY KEY,
    ref VARCHAR(255) NOT NULL,
    avatar TEXT NULL,
    displayname VARCHAR(255) NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) NULL,
    street VARCHAR(255) NULL,
    cityname VARCHAR(255) NULL,
    districtname VARCHAR(255) NULL,
    wardname VARCHAR(255) NULL,
    citynamev2 VARCHAR(255) NULL,
    wardnamev2 VARCHAR(255) NULL,
    birthyear INTEGER NOT NULL,
    birthmonth VARCHAR(255) NULL,
    birthday VARCHAR(255) NULL,
    orderstate VARCHAR(255) NOT NULL,
    orderresidual DECIMAL(12,2) NOT NULL,
    totaldebit DECIMAL(12,2) NOT NULL,
    amounttreatmenttotal DECIMAL(12,2) NOT NULL,
    amountrevenuetotal DECIMAL(12,2) NOT NULL,
    jobtitle VARCHAR(255) NULL,
    cardtype VARCHAR(255) NULL,
    sourceid UUID NOT NULL,
    sourcename VARCHAR(255) NULL,
    companyname VARCHAR(255) NOT NULL,
    date TIMESTAMP NOT NULL,
    companyid UUID NOT NULL,
    appointmentdate TIMESTAMP NULL,
    nextappointmentdate TIMESTAMP NULL,
    saleorderdate TIMESTAMP NULL,
    lasttreatmentcompletedate TIMESTAMP NULL,
    memberlevel VARCHAR(255) NULL,
    amountbalance DECIMAL(12,2) NOT NULL,
    customertype VARCHAR(255) NULL,
    categories JSONB NOT NULL,
    dateofbirth TIMESTAMP NOT NULL,
    age VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    addressv2 VARCHAR(255) NOT NULL,
    active BOOLEAN NOT NULL,
    userid VARCHAR(255) NULL,
    salename VARCHAR(255) NULL,
    gender VARCHAR(255) NOT NULL,
    genderdisplay VARCHAR(255) NOT NULL,
    comment VARCHAR(255) NULL,
    treatmentstatus VARCHAR(255) NOT NULL,
    usedaddressv2 BOOLEAN NOT NULL,
    marketingstaffid VARCHAR(255) NULL,
    contactstatusid VARCHAR(255) NULL,
    potentiallevel VARCHAR(255) NULL,
    serviceinterests VARCHAR(255) NULL,
    marketingstaff VARCHAR(255) NULL,
    contactstatus VARCHAR(255) NULL,
    countryid UUID NOT NULL,
    country VARCHAR(255) NULL,
    salepartnerid VARCHAR(255) NULL,
    customerstatus VARCHAR(255) NULL,
    unactiveby VARCHAR(255) NULL,
    unactivedate TIMESTAMP NULL,
    unactivereason VARCHAR(255) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Source endpoint: GET /api/CrmTasks/CountTasksByType
CREATE TABLE counttasksbytype (
    id SERIAL PRIMARY KEY,
    stage VARCHAR(255) NULL,
    total DECIMAL(12,2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Source endpoint: GET /api/ApplicationUsers
CREATE TABLE applicationusers (
    id SERIAL NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL,
    partnerid UUID NOT NULL,
    active BOOLEAN NOT NULL,
    phonenumber VARCHAR(20) NULL,
    jobid VARCHAR(255) NULL,
    jobname VARCHAR(255) NULL,
    ref VARCHAR(255) NULL,
    avatar TEXT NULL,
    employees JSONB NOT NULL,
    teammembers JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- Suggested indexes
CREATE INDEX idx_autocomplete_type ON autocomplete(type);
CREATE INDEX idx_companies_medicalfacilitycode ON companies(medicalfacilitycode);
CREATE INDEX idx_companies_phone ON companies(phone);
CREATE INDEX idx_companies_taxcode ON companies(taxcode);
CREATE INDEX idx_companies_taxphone ON companies(taxphone);
CREATE INDEX idx_autocomplete2_defaultcode ON autocomplete2(defaultcode);
CREATE INDEX idx_autocomplete2_type ON autocomplete2(type);
CREATE INDEX idx_autocomplete2_type2 ON autocomplete2(type2);
CREATE INDEX idx_getpagedpartnerscustomer_phone ON getpagedpartnerscustomer(phone);
CREATE INDEX idx_getpagedpartnerscustomer_email ON getpagedpartnerscustomer(email);
CREATE INDEX idx_getpagedpartnerscustomer_cardtype ON getpagedpartnerscustomer(cardtype);
CREATE INDEX idx_getpagedpartnerscustomer_customertype ON getpagedpartnerscustomer(customertype);
CREATE INDEX idx_getpagedpartnerscustomer_treatmentstatus ON getpagedpartnerscustomer(treatmentstatus);
CREATE INDEX idx_getpagedpartnerscustomer_contactstatusid ON getpagedpartnerscustomer(contactstatusid);
CREATE INDEX idx_getpagedpartnerscustomer_contactstatus ON getpagedpartnerscustomer(contactstatus);
CREATE INDEX idx_getpagedpartnerscustomer_customerstatus ON getpagedpartnerscustomer(customerstatus);
CREATE INDEX idx_applicationusers_phonenumber ON applicationusers(phonenumber);


-- ══════════════════════════════════════════════════════════════
-- AI-Enhanced Suggestions (via GROQ / llama-3.3-70b-versatile)
-- ══════════════════════════════════════════════════════════════
ALTER TABLE session ADD CONSTRAINT fk_session_partnerid FOREIGN KEY (partnerid) REFERENCES companies (id);
ALTER TABLE session ADD CONSTRAINT fk_session_userpartnerid FOREIGN KEY (userpartnerid) REFERENCES companies (id);
ALTER TABLE session ADD CONSTRAINT fk_session_tenantid FOREIGN KEY (tenantid) REFERENCES companies (id);
CREATE TABLE applicationusers (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    tenantid VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    userid INTEGER NOT NULL,
    companyid INTEGER NOT NULL,
    appointmentdate TIMESTAMP NOT NULL,
    appointmenttime TIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE appointments ADD CONSTRAINT fk_appointments_userid FOREIGN KEY (userid) REFERENCES applicationusers (id);
ALTER TABLE appointments ADD CONSTRAINT fk_appointments_companyid FOREIGN KEY (companyid) REFERENCES companies (id);
CREATE INDEX idx_session_expirationdate ON session (expirationdate);
CREATE INDEX idx_appointments_appointmentdate ON appointments (appointmentdate);
CREATE INDEX idx_appointments_userid ON appointments (userid);
CREATE INDEX idx_companies_name ON companies (name);
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE session ADD CONSTRAINT fk_session_username FOREIGN KEY (username) REFERENCES users (username);
CREATE TABLE usercompanies (
    id SERIAL PRIMARY KEY,
    userid INTEGER NOT NULL,
    companyid INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE usercompanies ADD CONSTRAINT fk_usercompanies_userid FOREIGN KEY (userid) REFERENCES users (id);
ALTER TABLE usercompanies ADD CONSTRAINT fk_usercompanies_companyid FOREIGN KEY (companyid) REFERENCES companies (id);
CREATE INDEX idx_usercompanies_userid ON usercompanies (userid);
CREATE INDEX idx_usercompanies_companyid ON usercompanies (companyid);
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE userpermissions (
    id SERIAL PRIMARY KEY,
    userid INTEGER NOT NULL,
    permissionid INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
ALTER TABLE userpermissions ADD CONSTRAINT fk_userpermissions_userid FOREIGN KEY (userid) REFERENCES users (id);
ALTER TABLE userpermissions ADD CONSTRAINT fk_userpermissions_permissionid FOREIGN KEY (permissionid) REFERENCES permissions (id);
CREATE INDEX idx_userpermissions_userid ON userpermissions (userid);
CREATE INDEX idx_userpermissions_permissionid ON userpermissions (permissionid);
