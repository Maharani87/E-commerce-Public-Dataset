import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="E-Commerce Dashboard", layout="wide")

st.title("📊 E-Commerce Performance & Delivery Dashboard")
st.markdown("Dashboard interaktif untuk menganalisis performa penjualan dan durasi pengiriman.")

# Memuat data & menyiapkan kolom kalkulasi
@st.cache_data
def load_data():
    df = pd.read_csv("dashboard/main_data.csv")
    
    # Ubah kolom timestamp ke tipe datetime
    datetime_cols = ["order_purchase_timestamp", "order_delivered_customer_date"]
    for col in datetime_cols:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col])
            
    # Buat kolom delivery_time_days jika belum ada
    if "delivery_time_days" not in df.columns and "order_delivered_customer_date" in df.columns:
        df["delivery_time_days"] = (df["order_delivered_customer_date"] - df["order_purchase_timestamp"]).dt.days

    # Buat kolom is_southeast jika belum ada
    if "is_southeast" not in df.columns and "customer_state" in df.columns:
        southeast_states = ["SP", "RJ", "MG", "ES"]
        df["is_southeast"] = df["customer_state"].apply(lambda x: "Southeast" if x in southeast_states else "Other")
        
    return df

main_df = load_data()

# Sidebar Filter
st.sidebar.header("Filter Data")
min_date = main_df["order_purchase_timestamp"].min().date()
max_date = main_df["order_purchase_timestamp"].max().date()

start_date, end_date = st.sidebar.date_input(
    label="Rentang Waktu",
    min_value=min_date,
    max_value=max_date,
    value=[min_date, max_date]
)

filtered_df = main_df[
    (main_df["order_purchase_timestamp"].dt.date >= start_date) & 
    (main_df["order_purchase_timestamp"].dt.date <= end_date)
]

# Metrik Utama
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Pesanan", value=f"{filtered_df['order_id'].nunique():,}")
with col2:
    st.metric("Total Pendapatan", value=f"BRL {filtered_df['price'].sum():,.2f}")
with col3:
    avg_delivery = filtered_df['delivery_time_days'].mean() if "delivery_time_days" in filtered_df.columns else 0
    st.metric("Rata-rata Pengiriman", value=f"{avg_delivery:.1f} Hari")

st.divider()

# Visualisasi 1: Top 5 Kategori Produk
st.subheader("Top 5 Kategori Produk Berdasarkan Pendapatan")
product_performance = filtered_df.groupby("product_category_name")["price"].sum().reset_index()
product_performance.columns = ["product_category_name", "total_revenue"]
top_5_products = product_performance.sort_values(by="total_revenue", ascending=False).head(5)

fig, ax = plt.subplots(figsize=(10, 4))
sns.barplot(x="total_revenue", y="product_category_name", data=top_5_products, palette="Blues_r", ax=ax)
ax.set_xlabel("Total Pendapatan (BRL)")
ax.set_ylabel("Kategori Produk")
st.pyplot(fig)

# Visualisasi 2: Perbandingan Pengiriman
st.subheader("Perbandingan Rata-Rata Waktu Pengiriman")
if "is_southeast" in filtered_df.columns and "delivery_time_days" in filtered_df.columns:
    delivery_comp = filtered_df.groupby("is_southeast")["delivery_time_days"].mean().reset_index()

    fig2, ax2 = plt.subplots(figsize=(6, 4))
    sns.barplot(x="is_southeast", y="delivery_time_days", data=delivery_comp, palette="Set2", ax=ax2)
    ax2.set_xlabel("Wilayah")
    ax2.set_ylabel("Rata-Rata Waktu Pengiriman (Hari)")
    st.pyplot(fig2)
else:
    st.warning("Kolom wilayah/waktu pengiriman tidak ditemukan di dataset.")