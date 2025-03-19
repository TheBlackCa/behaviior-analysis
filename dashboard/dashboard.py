import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style='dark')

def create_daily_usage_df(df):
    df = df.set_index("dteday")  # Set index ke datetime
    daily_usage_df = df.resample(rule='D').agg({
        "cnt": "sum",
        "casual": "sum",
        "registered": "sum",
        "temp": "mean",
        "windspeed": "mean"
    })
    daily_usage_df = daily_usage_df.reset_index()
    daily_usage_df.rename(columns={
        "cnt": "total_usage",
        "casual": "total_casual",
        "registered": "total_registered",
        "temp": "average_temperature",
        "windspeed": "average_windspeed"
    }, inplace=True)
    
    return daily_usage_df

def create_temp_min_max_df(df):
    df = df.set_index("dteday")
    min_max_temp_df = df.resample(rule='D').agg({
        "temp": ["min", "max"],
    })

    # Perbaikan struktur DataFrame
    min_max_temp_df.columns = ["minimum_temp", "maximum_temp"]
    min_max_temp_df = min_max_temp_df.reset_index()
    
    return min_max_temp_df

def create_wind_min_max_df(df):
    df = df.set_index("dteday")
    min_max_wind_df = df.resample(rule='D').agg({
        "windspeed": ["min", "max"],
    })

    # Perbaikan struktur DataFrame
    min_max_wind_df.columns = ["minimum_wind", "maximum_wind"]
    min_max_wind_df = min_max_wind_df.reset_index()
    
    return min_max_wind_df

# Membaca data dan memastikan format datetime
all_df = pd.read_csv("dashboard/day.csv")
all_df["dteday"] = pd.to_datetime(all_df["dteday"])  # Konversi ke datetime

min_date = all_df["dteday"].min()
max_date = all_df["dteday"].max()
 
with st.sidebar:
    st.image("pemanis.jpeg")
    
    start_date, end_date = st.date_input(
        label='Rentang Waktu', 
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

# Filter berdasarkan rentang tanggal
main_df = all_df[(all_df["dteday"] >= pd.to_datetime(start_date)) & 
                 (all_df["dteday"] <= pd.to_datetime(end_date))]

# Menggunakan fungsi untuk mendapatkan data harian
daily_usage_df = create_daily_usage_df(main_df)
min_max_temp_df = create_temp_min_max_df(main_df)
min_max_wind_df = create_wind_min_max_df(main_df)

# Gabungkan daily_usage_df dengan min_max_temp_df dan min_max_wind_df
daily_usage_df = daily_usage_df.merge(min_max_temp_df, on="dteday", how="left")
daily_usage_df = daily_usage_df.merge(min_max_wind_df, on="dteday", how="left")

st.header('Bicycle Rental User Behavior Analysis :sparkles:')
st.subheader('Daily Usage')

col1, col2, col3 = st.columns(3)

with col1:
    total_usage = daily_usage_df["total_usage"].sum() 
    st.metric("Total usage", value=f"{total_usage} Unit")

with col2:
    total_casual = daily_usage_df["total_casual"].sum()
    st.metric("Total Casual Usage", value=f"{total_casual} Unit")

with col3:
    total_registered = daily_usage_df["total_registered"].sum()
    st.metric("Total Registered Usage", value=f"{total_registered} Unit")

fig, ax = plt.subplots(figsize=(30, 10))
ax.plot(
    daily_usage_df["dteday"],
    daily_usage_df["total_usage"],
    marker='o', 
    linewidth=2,
    color="blue"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

# Menyiapkan data untuk bar chart
user_counts = {
    "User Type": ["Casual", "Registered"],
    "Total Users": [
        daily_usage_df["total_casual"].sum(), 
        daily_usage_df["total_registered"].sum()
    ]
}

user_df = pd.DataFrame(user_counts)

# Membuat bar chart
fig, ax = plt.subplots(figsize=(20, 6))
sns.barplot(
    x="User Type", 
    y="Total Users", 
    data=user_df,
    palette=["red", "blue"],  # Warna untuk Casual & Registered
    ax=ax
)
st.pyplot(fig)

st.subheader('Relation between temperature and total usage')
col1, col2, col3 = st.columns(3)

with col1:
    average_temperature = daily_usage_df["average_temperature"].mean()
    st.metric("Average temperature", value=f"{average_temperature:.2f} °C")

with col2:
    max_temperature = daily_usage_df["maximum_temp"].max()
    st.metric("Max temperature", value=f"{max_temperature:.2f} °C")

with col3:
    min_temperature = daily_usage_df["minimum_temp"].min()
    st.metric("Min temperature", value=f"{min_temperature:.2f} °C")

fig, ax1 = plt.subplots(figsize=(30, 10))
ax1.plot(
    daily_usage_df["dteday"],
    daily_usage_df["total_usage"],
    marker='o', 
    linewidth=2,
    color="red"
)
ax1.set_xlabel('Date', fontsize=12)
ax1.set_ylabel('Total Users', fontsize=25, color='red')
ax1.tick_params(axis='y', labelsize=25, labelcolor='red')

ax2 = ax1.twinx()
ax2.plot(
    daily_usage_df["dteday"],
    daily_usage_df["average_temperature"],
    marker='o', 
    linewidth=2,
    color="blue",
    label="Avg Temp"
)
ax2.plot(
    daily_usage_df["dteday"],
    daily_usage_df["maximum_temp"],
    marker='o', 
    linestyle="dashed",
    linewidth=2,
    color="green",
    label="Max Temp"
)
ax2.plot(
    daily_usage_df["dteday"],
    daily_usage_df["minimum_temp"],
    marker='o', 
    linestyle="dashed",
    linewidth=2,
    color="purple",
    label="Min Temp"
)
ax2.set_xlabel('Date', fontsize=12)
ax2.set_ylabel('Temperature (°C)', fontsize=25, color='blue')
ax2.tick_params(axis='y', labelsize=25, labelcolor='blue')
ax2.legend()

st.pyplot(fig)

st.subheader('Relation between windspeed and total usage')
col1, col2, col3 = st.columns(3)

with col1:
    average_wind = daily_usage_df["average_windspeed"].mean()
    st.metric("Average windspeed", value=f"{average_wind:.2f}")

with col2:
    max_wind = daily_usage_df["maximum_wind"].max()
    st.metric("Max windspeed", value=f"{max_wind:.2f}")

with col3:
    min_wind = daily_usage_df["minimum_wind"].min()
    st.metric("Min windspeed", value=f"{min_wind:.2f}")

fig, ax1 = plt.subplots(figsize=(30, 10))
ax1.plot(
    daily_usage_df["dteday"],
    daily_usage_df["total_usage"],
    marker='o', 
    linewidth=2,
    color="red"
)
ax1.set_xlabel('Date', fontsize=12)
ax1.set_ylabel('Total Users', fontsize=25, color='red')
ax1.tick_params(axis='y', labelsize=25, labelcolor='red')

ax2 = ax1.twinx()
ax2.plot(
    daily_usage_df["dteday"],
    daily_usage_df["average_windspeed"],
    marker='o', 
    linewidth=2,
    color="blue",
    label="Avg Temp"
)
ax2.plot(
    daily_usage_df["dteday"],
    daily_usage_df["maximum_wind"],
    marker='o', 
    linestyle="dashed",
    linewidth=2,
    color="green",
    label="Max Temp"
)
ax2.plot(
    daily_usage_df["dteday"],
    daily_usage_df["minimum_wind"],
    marker='o', 
    linestyle="dashed",
    linewidth=2,
    color="purple",
    label="Min Temp"
)
ax2.set_xlabel('Date', fontsize=12)
ax2.set_ylabel('Windspeed', fontsize=25, color='blue')
ax2.tick_params(axis='y', labelsize=25, labelcolor='blue')
ax2.legend()

st.pyplot(fig)
