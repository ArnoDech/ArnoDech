```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class AboutMe:
    username: str = "ArnoDech"
    role: str = "Data & AI Engineer"
        email: str = "arnauddeschamp9@gmail.com"

    summary: str = (
        "I design scalable data platforms and AI-powered solutions, "
        "from data ingestion to production deployment."
    )

    data_engineering: tuple[str, ...] = (
        "Airbyte",
        "Apache Airflow",
        "Apache Kafka",
        "Apache Flink",
        "Apache Spark",
        "Databricks",
        "dbt",
        "Debezium",
        "Snowflake",
        "Talend",
    )

    analytics: tuple[str, ...] = (
        "Power BI",
        "Qlik Sense",
        "Spotfire",
        "Tableau",
    )

    cloud: tuple[str, ...] = (
        "Microsoft Azure",
        "AWS",
    )

    ai_and_data_science: tuple[str, ...] = (
        "Azure AI Foundry",
        "Azure Machine Learning",
        "LangChain",
        "LLMs",
        "NLP",
        "NumPy",
        "pandas",
        "scikit-learn",
        "TensorFlow",
    )

    backend: tuple[str, ...] = (
        "FastAPI",
        "Flask",
        "Django",
    )

    certifications: tuple[str, ...] = (
        "Microsoft Azure — Certification name",
        "Databricks — Certification name",
        "Snowflake — Certification name",
        "Talend — Certification name",
    )

    interests: tuple[str, ...] = (
        "Data architecture",
        "Generative AI",
        "MLOps",
        "Real-time data processing",
    )

    links: dict[str, str] = field(default_factory=lambda: {
        "LinkedIn": "https://fr.linkedin.com/in/arnaud-deschamp",
    })

profile = AboutMe()
```
