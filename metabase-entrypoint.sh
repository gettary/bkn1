#!/bin/bash
# Pass the correct connection URL to Metabase
exec java -jar /app/metabase.jar -DMB_APPLICATION_DB_URL=postgresql://bkn1_user:bkn1_password@bkn1_postgres:5432/bkn1_db
