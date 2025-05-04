-- Create a new table without priority
CREATE TABLE detection_results_new (
    id INTEGER NOT NULL, 
    aadhar VARCHAR, 
    disease VARCHAR, 
    confidence FLOAT, 
    PRIMARY KEY (id)
);

-- Copy data from old table
INSERT INTO detection_results_new (id, aadhar, disease, confidence)
SELECT id, aadhar, disease, confidence FROM detection_results;

-- Drop old table and rename new table
DROP TABLE detection_results;
ALTER TABLE detection_results_new RENAME TO detection_results;

-- Recreate indexes
CREATE INDEX ix_detection_results_id ON detection_results (id);
CREATE INDEX ix_detection_results_aadhar ON detection_results (aadhar);