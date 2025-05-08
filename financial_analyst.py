import streamlit as st
import os
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from dotenv import load_dotenv
from crewai import Agent, Crew, Process, Task, LLM
from pydantic import BaseModel
import json
from tools.financial_tools import YFinanceStockTool, HistoricalStockDataTool

# Load environment variables
load_dotenv()

# Define Pydantic models for structured output
class StockAnalysis(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    market_cap: float
    pe_ratio: float
    recommendation: str
    analysis_summary: str
    risk_assessment: str
    technical_indicators: dict
    fundamental_metrics: dict

# Initialize SambaNova LLM
@st.cache_resource
def load_llm():
    return LLM(
        model="NVIDIABuild-Autogen-65",
        api_key=os.getenv("SAMBANOVA_API_KEY"),
        temperature=0.3
    )

# Create agents and tasks
def create_agents_and_tasks(symbol: str):
    llm = load_llm()
    
    # Initialize tools
    stock_tool = YFinanceStockTool()
    
    # Stock Analysis Agent
    stock_analysis_agent = Agent(
        role="Wall Street Financial Analyst",
        goal=f"Conduct a comprehensive, data-driven analysis of {symbol} stock using real-time market data",
        backstory="""You are a seasoned Wall Street analyst with 15+ years of experience in equity research.
                     You're known for your meticulous analysis and data-driven insights.
                     You ALWAYS base your analysis on real-time market data, never relying solely on pre-existing knowledge.
                     You're an expert at interpreting financial metrics, market trends, and providing actionable insights.""",
        llm=llm,
        verbose=True,
        memory=True,
        tools=[stock_tool]
    )

    # Report Writing Agent
    report_writer_agent = Agent(
        role="Financial Report Specialist",
        goal="Transform detailed financial analysis into a professional, comprehensive investment report",
        backstory="""You are an expert financial writer with a track record of creating institutional-grade research reports.
                     You excel at presenting complex financial data in a clear, structured format.
                     You always maintain professional standards while making reports accessible and actionable.
                     You're known for your clear data presentation, trend analysis, and risk assessment capabilities.""",
        llm=llm,
        verbose=True
    )

    # Analysis Task
    analysis_task = Task(
        description=f"""Analyze {symbol} stock using the stock_data_tool to fetch real-time data. Your analysis must include:

        1. Latest Trading Information (HIGHEST PRIORITY)
           - Latest stock price with specific date
           - Percentage change
           - Trading volume
           - Market status (open/closed)
           - Highlight if this is from the most recent trading session

        2. 52-Week Performance (CRITICAL)
           - 52-week high with exact date
           - 52-week low with exact date
           - Current price position relative to 52-week range
           - Calculate percentage from highs and lows

        3. Financial Deep Dive
           - Market capitalization
           - P/E ratio and other key metrics
           - Revenue growth and profit margins
           - Dividend information (if applicable)

        4. Technical Analysis
           - Recent price movements
           - Volume analysis
           - Key technical indicators

        5. Market Context
           - Business summary
           - Analyst recommendations
           - Key risk factors

        IMPORTANT: 
        - ALWAYS use the stock_data_tool to fetch real-time data
        - Begin your analysis with the latest price and 52-week data
        - Include specific dates for all price points
        - Clearly indicate when each price point was recorded
        - Calculate and show percentage changes
        - Verify all numbers with live data
        - Compare current metrics with historical trends""",
        expected_output="A comprehensive analysis report with real-time data, including all specified metrics and clear section breakdowns",
        agent=stock_analysis_agent
    )

    # Report Task
    report_task = Task(
        description=f"""Transform the analysis into a professional investment report for {symbol}. The report must:

        1. Structure:
           - Begin with an executive summary
           - Use clear section headers
           - Include tables for data presentation
           - Add emoji indicators for trends (📈 📉)

        2. Content Requirements:
           - Include timestamps for all data points
           - Present key metrics in tables
           - Use bullet points for key insights
           - Compare metrics to industry averages
           - Explain technical terms
           - Highlight potential risks

        3. Sections:
           - Executive Summary
           - Market Position Overview
           - Financial Metrics Analysis
           - Technical Analysis
           - Risk Assessment
           - Future Outlook

        4. Formatting:
           - Use markdown formatting
           - Create tables for data comparison
           - Include trend emojis
           - Use bold for key metrics
           - Add bullet points for key takeaways

        IMPORTANT:
        - Maintain professional tone
        - Clearly state all data sources
        - Include risk disclaimers
        - Format in clean, readable markdown""",
        expected_output="A professionally formatted investment report in markdown, with clear sections, data tables, and visual indicators",
        agent=report_writer_agent
    )

    # Create Crew
    crew = Crew(
        agents=[stock_analysis_agent, report_writer_agent],
        tasks=[analysis_task, report_task],
        process=Process.sequential,
        verbose=True
    )

    return crew

# Visualization functions
def create_price_chart(data_df, symbol):
    """Create an interactive candlestick chart with moving averages"""
    fig = go.Figure()
    
    # Add candlestick chart
    fig.add_trace(go.Candlestick(
        x=data_df['Date'],
        open=data_df['Open'], 
        high=data_df['High'],
        low=data_df['Low'], 
        close=data_df['Close'],
        name='Price'
    ))
    
    # Add moving averages if available
    if 'MA20' in data_df.columns:
        fig.add_trace(go.Scatter(
            x=data_df['Date'],
            y=data_df['MA20'],
            line=dict(color='orange', width=2),
            name='20-day MA'
        ))
    
    if 'MA50' in data_df.columns:
        fig.add_trace(go.Scatter(
            x=data_df['Date'],
            y=data_df['MA50'],
            line=dict(color='blue', width=2),
            name='50-day MA'
        ))
    
    # Layout
    fig.update_layout(
        title=f'{symbol} Stock Price',
        xaxis_title='Date',
        yaxis_title='Price (USD)',
        template='plotly_white',
        height=500,
        xaxis_rangeslider_visible=False
    )
    
    return fig

def create_volume_chart(data_df, symbol):
    """Create a volume chart"""
    fig = go.Figure()
    
    # Add volume bars
    colors = ['red' if row['Close'] < row['Open'] else 'green' for _, row in data_df.iterrows()]
    
    fig.add_trace(go.Bar(
        x=data_df['Date'],
        y=data_df['Volume'],
        marker_color=colors,
        name='Volume'
    ))
    
    # Layout
    fig.update_layout(
        title=f'{symbol} Trading Volume',
        xaxis_title='Date',
        yaxis_title='Volume',
        template='plotly_white',
        height=300
    )
    
    return fig

def create_rsi_chart(data_df, symbol):
    """Create RSI chart"""
    if 'RSI' not in data_df.columns:
        return None
    
    fig = go.Figure()
    
    # Add RSI line
    fig.add_trace(go.Scatter(
        x=data_df['Date'],
        y=data_df['RSI'],
        line=dict(color='purple', width=2),
        name='RSI'
    ))
    
    # Add overbought/oversold lines
    fig.add_shape(
        type="line", line_color="red", line_width=1, opacity=0.5, line_dash="dash",
        x0=data_df['Date'].iloc[0], x1=data_df['Date'].iloc[-1], y0=70, y1=70
    )
    fig.add_shape(
        type="line", line_color="green", line_width=1, opacity=0.5, line_dash="dash",
        x0=data_df['Date'].iloc[0], x1=data_df['Date'].iloc[-1], y0=30, y1=30
    )
    
    # Layout
    fig.update_layout(
        title=f'{symbol} RSI (Relative Strength Index)',
        xaxis_title='Date',
        yaxis_title='RSI Value',
        template='plotly_white',
        height=300,
        yaxis=dict(range=[0, 100])
    )
    
    return fig

def create_performance_gauge(current_price, low_price, high_price):
    """Create a gauge chart showing where current price is in 52-week range"""
    # Calculate percentage position in range
    range_size = high_price - low_price
    position = ((current_price - low_price) / range_size) * 100
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=position,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Position in 52-Week Range"},
        gauge={
            'axis': {'range': [0, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 33], 'color': "red"},
                {'range': [33, 66], 'color': "yellow"},
                {'range': [66, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': position
            }
        }
    ))
    
    return fig

def fetch_historical_data(symbol):
    """Fetch historical data for visualization"""
    # Initialize the tool
    historical_tool = HistoricalStockDataTool()
    
    # Get 1 year of daily data
    hist_data_str = historical_tool._run(symbol=symbol, period="1y", interval="1d")
    hist_data = json.loads(hist_data_str)
    
    # Convert to dataframe
    if 'data' in hist_data:
        df = pd.DataFrame(hist_data['data'])
        return df
    return None

# Streamlit UI
st.set_page_config(page_title="AI Financial Analyst", layout="wide")

st.title("🤖 AI Financial Analyst")

# Sidebar
with st.sidebar:
    st.header("Configuration")
    
    # API Key input
    api_key = st.text_input(
        "SambaNova API Key",
        type="password",
        value=os.getenv("SAMBANOVA_API_KEY", ""),
        help="Enter your SambaNova API key"
    )
    if api_key:
        os.environ["SAMBANOVA_API_KEY"] = api_key

    # Stock Symbol input
    symbol = st.text_input(
        "Stock Symbol",
        value="AAPL",
        help="Enter a stock symbol (e.g., AAPL, GOOGL)"
    ).upper()

    # Analysis button
    analyze_button = st.button("Analyze Stock", type="primary")

# Main content area
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
    st.session_state.report = None
    st.session_state.historical_data = None

if analyze_button:
    try:
        with st.spinner(f'Analyzing {symbol}... This may take a few minutes.'):
            # Create and run the crew
            crew = create_agents_and_tasks(symbol)
            result = crew.kickoff()
            # Convert the CrewOutput to string if needed
            if hasattr(result, 'raw'):
                st.session_state.report = result.raw
            else:
                st.session_state.report = str(result)
            
            # Fetch historical data for visualizations
            st.session_state.historical_data = fetch_historical_data(symbol)
            st.session_state.symbol = symbol
            st.session_state.analysis_complete = True

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if st.session_state.analysis_complete and st.session_state.report:
    # Create tabs for report and visualizations
    tab1, tab2 = st.tabs(["Analysis Report", "Visualizations"])
    
    with tab1:
        st.markdown("### Analysis Report")
        st.markdown(st.session_state.report)
        
        # Download button
        st.download_button(
            label="Download Report",
            data=st.session_state.report,
            file_name=f"stock_analysis_{st.session_state.symbol}_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown"
        )
    
    with tab2:
        st.markdown(f"### {st.session_state.symbol} Stock Visualizations")
        
        if st.session_state.historical_data is not None:
            data_df = st.session_state.historical_data
            
            # Price Chart
            st.plotly_chart(create_price_chart(data_df, st.session_state.symbol), use_container_width=True)
            
            # Two columns for volume and RSI
            col1, col2 = st.columns(2)
            
            with col1:
                # Volume Chart
                st.plotly_chart(create_volume_chart(data_df, st.session_state.symbol), use_container_width=True)
            
            with col2:
                # RSI Chart
                rsi_chart = create_rsi_chart(data_df, st.session_state.symbol)
                if rsi_chart:
                    st.plotly_chart(rsi_chart, use_container_width=True)
            
            # Performance Gauge - Calculate prices from dataframe
            if len(data_df) > 0:
                current_price = data_df['Close'].iloc[-1]
                low_price = data_df['Low'].min()
                high_price = data_df['High'].max()
                
                st.plotly_chart(create_performance_gauge(current_price, low_price, high_price), use_container_width=True)
        else:
            st.warning("No historical data available for visualization")

# Footer
st.markdown("---")