# Examples

Interactive Google Colab notebooks demonstrating various use cases.

## Stress: 28-day rolling average

[Open in Google Colab](https://colab.research.google.com/github/matin/garth/blob/main/colabs/stress.ipynb)

Stress levels from one day to another can vary by extremes, but there's always
a general trend. Using a scatter plot with a rolling average shows both the
individual days and the trend. The Colab retrieves up to three years of daily
data. If there's less than three years of data, it retrieves whatever is
available.

![Stress: Graph of 28-day rolling average](https://github.com/matin/garth/assets/98985/868ecf25-4644-4879-b28f-ed0706a9e7b9)

## Sleep analysis over 90 days

[Open in Google Colab](https://colab.research.google.com/github/matin/garth/blob/main/colabs/sleep.ipynb)

The Garmin Connect app only shows a maximum of seven days for sleep
stages—making it hard to see trends. The Connect API supports retrieving
daily sleep quality in 28-day pages, but that doesn't show details. Using
`SleepData.list()` gives us the ability to retrieve an arbitrary number of
days with enough detail to produce a stacked bar graph of the daily sleep
stages.

![Sleep stages over 90 days](https://github.com/matin/garth/assets/98985/ba678baf-0c8a-4907-aa91-be43beec3090)

One specific graph that's useful but not available in the Connect app is
sleep start and end times over an extended period. This provides context
to the sleep hours and stages.

![Sleep times over 90 days](https://github.com/matin/garth/assets/98985/c5583b9e-ab8a-4b5c-bfe6-1cb0ca95d1de)

## ChatGPT analysis of Garmin stats

[Open in Google Colab](https://colab.research.google.com/github/matin/garth/blob/main/colabs/chatgpt_analysis_of_stats.ipynb)

ChatGPT's Advanced Data Analysis can provide incredible insight
into the data in a way that's much simpler than using Pandas and Matplotlib.

Start by using the linked Colab to download a CSV of the last three years
of your stats, and upload the CSV to ChatGPT.

Here are example outputs:

**How do I sleep on different days of the week?**

<img width="600" alt="Sleep by day of week" src="https://github.com/matin/garth/assets/98985/b7507459-2482-43d6-bf55-c3a1f756facb">

**On what days do I exercise the most?**

<img width="600" alt="Exercise by day of week" src="https://github.com/matin/garth/assets/98985/11294be2-8e1a-4fed-a489-13420765aada">
