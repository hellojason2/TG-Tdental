-- Auto-generated database schema from SPA scraping
-- Source: https://tamdentist.tdental.vn/
-- Generated from 0 inferred tables


-- Suggested indexes


-- ══════════════════════════════════════════════════════════════
-- AI-Enhanced Suggestions (via GROQ / llama-3.3-70b-versatile)
-- ══════════════════════════════════════════════════════════════
```sql
CREATE TABLE Users (
  id INT PRIMARY KEY,
  tenantId INT,
  deviceId INT,
  username VARCHAR(255),
  email VARCHAR(255) UNIQUE
);

CREATE TABLE Sessions (
  id INT PRIMARY KEY,
  userId INT,
  deviceId INT,
  sessionId VARCHAR(255) UNIQUE,
  token VARCHAR(255),
  refreshToken VARCHAR(255),
  expiresAt TIMESTAMP
);

CREATE TABLE Configs (
  id INT PRIMARY KEY,
  tenantId INT,
  key VARCHAR(255),
  value VARCHAR(255)
);

ALTER TABLE Users ADD CONSTRAINT UC_Users UNIQUE (email);

CREATE INDEX idx_Users_tenantId ON Users (tenantId);
CREATE INDEX idx_Sessions_userId ON Sessions (userId);
CREATE INDEX idx_Sessions_deviceId ON Sessions (deviceId);
CREATE INDEX idx_Sessions_sessionId ON Sessions (sessionId);
CREATE INDEX idx_Configs_tenantId ON Configs (tenantId);
```
