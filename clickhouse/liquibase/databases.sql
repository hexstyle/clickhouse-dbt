--liquibase formatted plpgsql
--changeset system:databases stripComments:false splitStatements:false context:casual runAlways:false runOnChange:true failOnError:true

CREATE DATABASE IF NOT EXISTS online_reporting ON CLUSTER 'global_cluster';
       