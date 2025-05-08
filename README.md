# 📊 AI Financial Analyst

A multi-agent AI system that performs in-depth stock analysis using real-time market data.

### Demo:
<video controls autoplay muted playsinline src="media/demo.mp4" width="100%"></video>

## 🧠 Overview

This application uses **CrewAI's** multi-agent architecture to analyze stocks with specialized AI agents:
- 🧮 **Financial Analyst Agent**: Fetches and analyzes real-time stock data  
- 📝 **Report Writer Agent**: Transforms technical analysis into professional investment reports

The application leverages **SambaNova's Llama-4-Maverick model** to provide institutional-grade stock analysis with a user-friendly **Streamlit** interface.

## 🚀 Features

- 📈 Real-time stock data analysis using YFinance  
- 📊 Comprehensive analysis of price movements, financial metrics, and market trends  
- 🧾 Professional investment reports with clear sections and visual indicators  
- 🖥️ Interactive Streamlit interface for easy stock analysis  

## ⚙️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Pratham-gupta-235/AI-Financial-Analyst.git
   cd AI-Financial-Analyst
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a .env file in the root directory with your SambaNova API key:
   ```env
   SAMBANOVA_API_KEY=your_api_key_here
   ```

## ▶️ Usage
1. Run the Streamlit application:
   
   ```bash
   streamlit run financial_analyst.py
   ```
2. In the sidebar:

   🔑 Enter your SambaNova API key 
   
   💼 Enter a stock symbol (e.g., AAPL, GOOGL)
   
   📥 Click "Analyze Stock"
   
   📤 View and download the generated analysis report

## 🗂️ Project Structure
   ``financial_analyst.py``: Main Streamlit application
   
   ```tools/financial_tools.py```: Custom tools for stock data retrieval
   
   ```.env```: Environment variables (API keys)
   
   ```requirements.txt```: Project dependencies

## 📌 Requirements
   🐍 Python 3.11+
   
   🔐 SambaNova API key
   
   🌐 Internet connection for real-time stock data retrieval
   
   📝 License
   This project is licensed under the MIT License.
