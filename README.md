# 📊 End-to-End Data Pipeline and Analytics with RapidAPI, AWS, and Apache Airflow

## 🚀 Project Overview
Developed a **full-scale ETL pipeline** for data extraction, transformation, and visualization using **RapidAPI**, **AWS services**, and **Apache Airflow**.  

The pipeline ingests raw data from RapidAPI into an **S3 Landing Zone**, where **AWS Lambda** functions are triggered to process and convert **JSON → CSV**. The processed files move through an **Intermediate Zone** into a **Transformed Zone** in S3. From there, data is loaded into **Amazon Redshift** for querying and finally visualized in **AWS QuickSight** dashboards.  

The entire workflow is orchestrated via **Apache Airflow** running on an **EC2 instance (public IP)** and managed using **VS Code Remote-SSH**.  

---

## 🔄 Data Flow (Architecture)

1. **Extract & Load**  
   - Data pulled from **RapidAPI** using Python.  
   - Stored in **S3 Landing Zone**.  

2. **Trigger & Transform (Lambda 1)**  
   - **S3 event trigger** activates a **Lambda function**.  
   - Cleans, parses, and converts **JSON → CSV**.  
   - Stores results in **Intermediate Zone**.  

3. **Further Processing (Lambda 2)**  
   - Another **Lambda** refines and validates data.  
   - Writes final output to **Transformed Zone** in S3.  

4. **Load & Query**  
   - Transformed datasets ingested into **Amazon Redshift**.  
   - Supports scalable queries and analytics.  

5. **Visualization**  
   - KPIs and trends delivered via **AWS QuickSight dashboards**.  

6. **Orchestration**  
   - **Airflow DAGs on EC2 (public IP)** schedule, monitor, and automate ETL cycles.  
   - Managed securely through **VS Code Remote-SSH**.  

---

## ✨ Key Features
- Automated **Lambda-based JSON → CSV conversion** with **S3 event triggers**.  
- **Multi-zone S3 storage**: Landing → Intermediate → Transformed.  
- **Centralized orchestration** with **Airflow on EC2**, accessible via VS Code Remote-SSH.  
- **Redshift + QuickSight** integration for advanced analytics & visualization.  
- **Scalable, modular, and serverless design** for cost-efficient processing.  

---

## 🛠️ Tech Stack
- **Data Source:** RapidAPI  
- **Orchestration:** Apache Airflow (EC2)  
- **Data Storage:** Amazon S3 (Landing, Intermediate, Transformed)  
- **Transformation:** AWS Lambda (Python)  
- **Data Warehouse:** Amazon Redshift  
- **Visualization:** AWS QuickSight  
- **Development Tools:** VS Code Remote-SSH, IAM  

---

## 📂 Project Structure
```bash
.
├── airflow_dags/         # Airflow DAGs for ETL orchestration
├── lambda_functions/     # Python scripts for JSON → CSV and transformations
├── dashboards/           # AWS QuickSight reports and screenshots
├── README.md             # Project documentation
