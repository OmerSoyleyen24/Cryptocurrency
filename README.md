Cryptocurrency Analytics & AI Forecasting Tool
A high-performance full-stack application that provides historical cryptocurrency data visualization and utilizes Deep Learning (LSTM/GRU/Dense) models to forecast market trends. This project demonstrates a decoupled microservices-ready architecture with automated CI/CD pipelines.

🏗 System Architecture & Deployment
The application is built on a distributed cloud architecture to ensure scalability, cost-efficiency, and separation of concerns:

Frontend: Netlify (Atomic Deploys & CDN-backed)

Backend API: Railway (Containerized Environment)

Database: Clever Cloud (Managed MySQL)

🌟 Key Features
Historical Data Processing: Ingests and normalizes large-scale historical market data via Kucoin API.

Competitive AI Forecasting: Implements a multi-model approach using LSTM, GRU, and Dense architectures for time-series prediction.

Automated Model Selection: Benchmarks neural network performance using MSE and RMSE metrics to dynamically select the most accurate model for each specific dataset.

Decoupled Architecture: Frontend and Backend are hosted independently, communicating via a secured RESTful API.

🛠 Tech Stack
Frontend: React.js, Context API, Axios, Tailwind CSS

Backend: Python, REST API (Flask/FastAPI)

AI/ML: TensorFlow, Keras, NumPy, Pandas, Scikit-learn

Data Persistence: MySQL (hosted on Clever Cloud)

DevOps: GitHub Actions, Netlify CI/CD

🧠 Technical Deep Dive: Hybrid AI Forecasting
Unlike standard crypto trackers, this tool implements a Competitive Model Selection engine. The backend evaluates three distinct architectures to mitigate issues like the "vanishing gradient" problem and "overfitting":

LSTM (Long Short-Term Memory): Optimized for capturing long-term temporal dependencies in volatile cycles.

GRU (Gated Recurrent Unit): A streamlined alternative that often provides faster convergence and higher accuracy for specific price patterns.

Dense (Baseline): A fully connected neural network used to ensure that complex recurrent models are providing a genuine predictive advantage over simpler architectures.

Optimization Strategy: Data is pre-processed using MinMaxScaler for normalization. The system automatically benchmarks all three models and serves the one with the highest statistical significance for the final visualization.

📥 Local Development
Clone the repo:

Bash
git clone https://github.com/OmerSoyleyen24/Cryptocurrency.git
Environment Variables:
Create a .env file in the root directory and add:

Kod snippet'i
REACT_APP_API_URL=your_railway_backend_url
DATABASE_URL=your_clever_cloud_db_url
Install & Run:

Bash
npm install && npm start
👤 Author
Ömer Söyleyen

Portfolio: https://portfolio-website-omersoyleyen.netlify.app
