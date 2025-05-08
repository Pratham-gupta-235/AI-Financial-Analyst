# 📊 AI Financial Analyst

A multi-agent AI system that performs in-depth stock analysis using real-time market data with interactive visualizations.

## 🧠 Overview

This application uses CrewAI's multi-agent architecture to analyze stocks with specialized AI agents:

- **🧮 Financial Analyst Agent**: Fetches and analyzes real-time stock data.
- **📝 Report Writer Agent**: Transforms technical analysis into professional investment reports.

The application leverages SambaNova's Llama-4-Maverick model to provide institutional-grade stock analysis with a user-friendly Streamlit interface.

## 🎥 Demo Video

Watch the application in action below:

<video width="800" controls>
  <source src="path_to_your_video.mp4" type="video/mp4">
  Your browser does not support the video tag.
</video>

Alternatively, [click here to download the video](path_to_your_video.mp4).

## 🚀 Features

- 📈 Real-time stock data analysis using YFinance.
- 📊 Comprehensive analysis of price movements, financial metrics, and market trends.
- 📉 Interactive data visualizations including candlestick charts, technical indicators, and performance metrics.
- 🧾 Professional investment reports with clear sections and visual indicators.
- 🖥️ Interactive Streamlit interface for easy stock analysis.

## ⚙️ Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Pratham-gupta-235/AI-Financial-Analyst.git
   cd AI-Financial-Analyst
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the root directory with your SambaNova API key:
   ```env
   SAMBANOVA_API_KEY=your_api_key_here
   ```

## ▶️ Usage

1. **Run the Streamlit application**:
   ```bash
   streamlit run financial_analyst.py
   ```

2. **In the sidebar**:
   - 🔑 Enter your SambaNova API key.
   - 💼 Enter a stock symbol (e.g., AAPL, GOOGL).
   - 📥 Click "Analyze Stock".
   - 📤 View and download the generated analysis report.

## 📊 Visualizations

The application provides powerful interactive visualizations to enhance your stock analysis:

- **Candlestick Chart**: View price action with 20-day and 50-day moving averages.
- **Volume Analysis**: Color-coded volume bars showing trading activity.
- **Technical Indicators**: RSI (Relative Strength Index) with overbought/oversold levels.
- **Performance Gauge**: Visual representation of the current price position in the 52-week range.

All charts are interactive, allowing you to zoom, pan, and hover for detailed information.

## 🗂️ Project Structure

- `financial_analyst.py`: Main Streamlit application.
- `tools/financial_tools.py`: Custom tools for stock data retrieval.
- `.env`: Environment variables (API keys).
- `requirements.txt`: Project dependencies.

## 📌 Requirements

- 🐍 Python 3.11+
- 🔐 SambaNova API key
- 🌐 Internet connection for real-time stock data retrieval

## 📝 License

This project is licensed under the MIT License.
