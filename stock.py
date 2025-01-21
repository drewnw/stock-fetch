import certifi
import ssl
import discord
from discord.ext import commands
import yfinance as yf
from dotenv import load_dotenv
import os
import matplotlib.pyplot as plt

# bot token
load_dotenv()

# grab token
TOKEN = os.getenv('DISCORD_TOKEN')

# Setup SSL context to use certifi's certificates
ssl_context = ssl.create_default_context(cafile=certifi.where())

# Define intents
intents = discord.Intents.default()
intents.message_content = True  # Required to read message content

# bot instance w intents
bot = commands.Bot(command_prefix='/', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')


# command to fetch stock data and plot graph
@bot.command()
async def stock(ctx, ticker: str):
    stock = yf.Ticker(ticker)
    try:
        current_price = stock.info.get('currentPrice', 'N/A')
        eps = stock.info.get('trailingEps', 'N/A')
        pe_ratio = stock.info.get('trailingPE', 'N/A')
        dividend_yield = stock.info.get('dividendYield', 'N/A')
        market_cap = stock.info.get('marketCap', 'N/A')
        volume = stock.info.get('volume', 'N/A')

        # Ensure numerical values are formatted properly
        if isinstance(current_price, (int, float)):
            current_price = f"{current_price:,.2f}"
        if isinstance(eps, (int, float)):
            eps = f"{eps:.2f}"
        if isinstance(pe_ratio, (int, float)):
            pe_ratio = f"{pe_ratio:.2f}"
        if isinstance(dividend_yield, (int, float)):
            dividend_yield = f"{dividend_yield * 100:.2f}%"
        if isinstance(market_cap, (int, float)):
            market_cap = f"{market_cap:,.2f}"
        if isinstance(volume, (int, float)):
            volume = f"{volume:,.2f}"

        # output msg
        message = (f"**{ticker.upper()} Stock Information**\n"
                   f"Current Price: ${current_price}\n"
                   f"EPS: {eps}\n"
                   f"PE Ratio: {pe_ratio}\n"
                   f"Dividend Yield: {dividend_yield}\n"
                   f"Market Cap: ${market_cap}\n"
                   f"Volume: {volume}")

        await ctx.send(message)

        # fetches stock data from last 6 months
        hist = stock.history(period="6mo")

        # Plot the graph for the stock's closing price
        plt.figure(figsize=(10, 5))
        plt.plot(hist.index, hist['Close'], label='Closing Price', color='blue')
        plt.title(f"{ticker.upper()} Stock Price - Last 6 Months")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.legend()

        # graph as img
        graph_image = f"{ticker}_stock_graph.png"
        plt.savefig(graph_image)
        plt.close()

        # send graph
        await ctx.send(file=discord.File(graph_image))

    except Exception as e:
        await ctx.send(f"Error fetching data for {ticker.upper()}: {str(e)}")


# Run the bot with the token
bot.run(TOKEN)
