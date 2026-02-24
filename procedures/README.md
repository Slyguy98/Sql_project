# 🎮 Steam Market Intelligence System
> **An End-to-End SQL Data Engineering & Analytics Pipeline**

A professional-grade data infrastructure project that transforms raw Steam store data into a high-performance relational database. This system processes over **27,000 games** and **76,000 unique genre mappings** to identify market trends and player sentiment.

## 🏗️ Data Architecture (Relational Schema)
Unlike basic flat-file projects, this system utilizes a **Normalized Schema** to ensure data integrity and query speed:
*   **`games`**: Core entity table containing 18 dimensions (Price, Ratings, Developer, etc.).
*   **`genres`**: Unique catalog of global market categories.
*   **`game_genres`**: A **Many-to-Many Bridge Table** managing 76,000+ relationships.
*   **`player_metrics`**: Time-series table tracking sustained player engagement.

## 📊 Analytical Insights (SQL Views)
The system features pre-compiled [PostgreSQL Views](https://www.postgresql.org) to answer complex business questions:
*   **Market Dominance:** Identifies which genres saturate the Steam store by volume.
*   **Price vs. Sentiment:** Analyzes the "Sweet Spot" ($10-$20 range) for maximum player approval.
*   **Sustainability Index:** Uses `average_playtime` to separate viral spikes from long-term retention.

## ⚙️ Project Pipeline
### 1. Build the Infrastructure
Initialize the entire environment (Schema Build -> Bulk Load -> Relational Mapping) with one automated command:
```bash
sudo -u postgres psql -d postgres -f seeds/initial_data.sql