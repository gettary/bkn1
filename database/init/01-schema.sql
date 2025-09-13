-- BKN1 Assessment System Database Schema

-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table with role-based access
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('Admin', 'Moderator', 'User')),
    full_name VARCHAR(100) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Assessments table (แบบประเมิน)
CREATE TABLE assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(200) NOT NULL,
    fiscal_year INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('draft', 'published')),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(name)
);

-- Assessment items table (ประเด็น - main topics)
CREATE TABLE assessment_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indicators table (ตัวชี้วัด)
CREATE TABLE indicators (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_item_id UUID REFERENCES assessment_items(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indicator items table (รายการตัวชี้วัด)
CREATE TABLE indicator_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    indicator_id UUID REFERENCES indicators(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    target_value VARCHAR(200),
    actual_target VARCHAR(200),
    order_index INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User permissions table (control who can see what data)
CREATE TABLE user_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    indicator_id UUID REFERENCES indicators(id) ON DELETE CASCADE,
    can_view BOOLEAN DEFAULT FALSE,
    can_edit BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, indicator_id)
);

-- User data table (data entered by users)
CREATE TABLE user_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    indicator_item_id UUID REFERENCES indicator_items(id) ON DELETE CASCADE,
    performance VARCHAR(500),
    rate VARCHAR(100),
    score VARCHAR(100),
    image_path VARCHAR(500),
    status VARCHAR(20) NOT NULL CHECK (status IN ('draft', 'complete')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, indicator_item_id)
);

-- Create indexes for better performance
CREATE INDEX idx_assessments_fiscal_year ON assessments(fiscal_year);
CREATE INDEX idx_assessments_status ON assessments(status);
CREATE INDEX idx_assessment_items_assessment_id ON assessment_items(assessment_id);
CREATE INDEX idx_indicators_assessment_item_id ON indicators(assessment_item_id);
CREATE INDEX idx_indicator_items_indicator_id ON indicator_items(indicator_id);
CREATE INDEX idx_user_permissions_user_id ON user_permissions(user_id);
CREATE INDEX idx_user_permissions_indicator_id ON user_permissions(indicator_id);
CREATE INDEX idx_user_data_user_id ON user_data(user_id);
CREATE INDEX idx_user_data_indicator_item_id ON user_data(indicator_item_id);

-- Create default admin user (password: admin123)
INSERT INTO users (username, email, password_hash, role, full_name) VALUES 
('admin', 'admin@bkn1.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2Xvz3o.2Zu', 'Admin', 'ผู้ดูแลระบบ'),
('moderator', 'moderator@bkn1.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2Xvz3o.2Zu', 'Moderator', 'ผู้ควบคุม'),
('user1', 'user1@bkn1.local', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj2Xvz3o.2Zu', 'User', 'ผู้ใช้งานทั่วไป');

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assessments_updated_at BEFORE UPDATE ON assessments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_data_updated_at BEFORE UPDATE ON user_data
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();