 FastAPI Backend Architecture for AI Property Analysis Platform

This document describes a **production-grade FastAPI backend folder structure** commonly used in large AI SaaS platforms.  
The goal is to create a backend that is **maintainable, scalable, and modular**.

This structure separates responsibilities clearly so teams can work independently on services like AI pipelines, financial calculations, report generation, and API routes.

---

# 1. High-Level Backend Architecture

The backend follows a **modular service architecture**.

System flow:

User Request → API Routes → Services → AI Pipelines → Rules Engine → Financial Engine → Report Generator → Storage → Response

Each module has a clearly defined responsibility.

---

# 2. Recommended FastAPI Project Structure


backend/
│
├── app/
│ │
│ ├── main.py
│ │
│ ├── config/
│ │ ├── settings.py
│ │ └── logging.py
│ │
│ ├── database/
│ │ ├── connection.py
│ │ ├── base.py
│ │ └── session.py
│ │
│ ├── models/
│ │ ├── property_model.py
│ │ ├── image_model.py
│ │ ├── detection_model.py
│ │ ├── asset_model.py
│ │ └── report_model.py
│ │
│ ├── schemas/
│ │ ├── property_schema.py
│ │ ├── image_schema.py
│ │ ├── detection_schema.py
│ │ ├── asset_schema.py
│ │ └── report_schema.py
│ │
│ ├── routes/
│ │ ├── property_routes.py
│ │ ├── image_routes.py
│ │ ├── analysis_routes.py
│ │ └── report_routes.py
│ │
│ ├── services/
│ │ ├── property_service.py
│ │ ├── image_service.py
│ │ └── analysis_service.py
│ │
│ ├── ai/
│ │ ├── models/
│ │ │ ├── open_vocab_detector.py
│ │ │ ├── vlm_model.py
│ │ │ └── object_detector.py
│ │ │
│ │ └── detection_pipeline.py
│ │
│ ├── pipelines/
│ │ └── image_processing_pipeline.py
│ │
│ ├── rules_engine/
│ │ └── asset_rules_engine.py
│ │
│ ├── financial_engine/
│ │ └── cost_segregation_engine.py
│ │
│ ├── report_generator/
│ │ └── excel_report_generator.py
│ │
│ ├── workers/
│ │ └── celery_worker.py
│ │
│ ├── storage/
│ │ └── storage_manager.py
│ │
│ ├── utils/
│ │ ├── image_utils.py
│ │ └── file_utils.py
│ │
│ └── config_files/
│ ├── asset_rules.json
│ ├── synonyms.json
│ └── cost_tables.json
│
└── requirements.txt


---

# 3. Explanation of Each Module

## main.py

Application entry point.

Responsibilities:

- start FastAPI application
- register routes
- load configuration
- initialize database
- initialize background workers

---

## config/

Contains application configuration.

Examples:

- environment variables
- database credentials
- API keys
- logging configuration

Files:

- settings.py
- logging.py

---

## database/

Handles database configuration.

Files:

connection.py  
Creates PostgreSQL engine.

base.py  
Defines SQLAlchemy base model.

session.py  
Creates database session dependency.

---

## models/

Contains SQLAlchemy ORM models.

Examples:

Property model  
Image model  
Detection model  
Asset model  
Report model

These map directly to database tables.

---

## schemas/

Defines Pydantic models used for:

- request validation
- response formatting

Examples:

PropertyCreate  
PropertyResponse  
ImageUpload  
DetectionResponse

---

## routes/

Defines FastAPI endpoints.

Example route modules:

property_routes.py

Endpoints:

POST /property  
GET /property/{id}  
GET /properties

image_routes.py

POST /upload-images

analysis_routes.py

POST /analyze-property

report_routes.py

GET /report/{property_id}

---

## services/

Contains business logic separated from routes.

Example:

property_service.py

Handles:

- property creation
- property queries
- linking images

This keeps route handlers clean.

---

# 4. AI Module

The AI module contains object detection models.

Structure:

ai/models/

open_vocab_detector.py  
Detects objects using open vocabulary detection.

vlm_model.py  
Vision language model for semantic refinement.

object_detector.py  
High precision object detection model.

detection_pipeline.py

Pipeline:

image → model1 → model2 → model3 → merged detections

---

# 5. Image Processing Pipeline

Location:

pipelines/image_processing_pipeline.py

Responsibilities:

- resize images
- normalize format
- filter low quality images
- extract metadata

Libraries used:

OpenCV  
Pillow

---

# 6. Rules Engine

Location:

rules_engine/asset_rules_engine.py

Purpose:

Map detected objects to tax depreciation categories.

Example rule:

mirror → 5 year asset  
cabinet → 5 year asset  
door → 39 year structural

Rules stored in:

asset_rules.json

---

# 7. Financial Engine

Location:

financial_engine/cost_segregation_engine.py

Responsible for cost segregation calculations.

Example formulas:

replacement_cost = unit_cost × quantity

allocation_factor = improvement_basis / total_replacement_cost

final_asset_value = replacement_cost × allocation_factor

---

# 8. Report Generator

Location:

report_generator/excel_report_generator.py

Generates Excel reports.

Libraries:

pandas  
openpyxl

Report sections:

Property Summary  
Detected Assets  
Replacement Cost Table  
Allocation Table  
Depreciation Schedule  
Tax Savings

Reports saved to:

storage/reports/

---

# 9. Background Workers

Location:

workers/celery_worker.py

Handles asynchronous tasks:

- image processing
- AI detection
- report generation

Queue system example:

Redis + Celery

---

# 10. Storage Module

Location:

storage/storage_manager.py

Handles:

- image uploads
- report storage
- cloud storage integration

Example providers:

AWS S3  
Supabase Storage

---

# 11. Utils Module

Utility helper functions.

Examples:

image_utils.py

- image resizing
- compression

file_utils.py

- file validation
- file handling

---

# 12. Config Files

Location:

config_files/

Contains configurable logic:

asset_rules.json  
synonyms.json  
cost_tables.json

These allow updating rules without modifying code.

---

# 13. Benefits of This Structure

This architecture provides:

Clear separation of responsibilities

Easy scaling of AI services

Maintainable codebase

Modular development for large teams

Ability to replace AI models easily

---

# 14. Backend Workflow

Full system flow:

User uploads property

Images stored

Image preprocessing

AI object detection

Object normalization

Deduplication

Asset classification

Cost calculations

Excel report generation

Report storage

User downloads report

---

# 15. Summary

This folder structure is commonly used in **large AI SaaS platforms built with FastAPI**.

It ensures:

clean architecture

scalability

maintainability

clear service boundaries

Using this design makes the backend easier to extend with new AI models, financial logic, or reporting features.
"""

