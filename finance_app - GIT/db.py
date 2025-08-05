import pandas as pd
import os
from datetime import datetime

DATA_DIR = "data"

def get_user_file(username):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    return os.path.join(DATA_DIR, f"{username}.csv")

def add_transaction(username, islem_tipi, kategori, tutar, aciklama):
    filename = get_user_file(username)
    tarih = datetime.now().strftime("%Y-%m-%d")
    yeni_kayit = pd.DataFrame([{
        "Tarih": tarih,
        "Tip": islem_tipi,
        "Kategori": kategori,
        "Tutar" : tutar,
        "Açıklama" : aciklama
    }])
    
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df = pd.concat([df, yeni_kayit], ignore_index=True)
    else:
        df = yeni_kayit

    df.to_csv(filename, index=False)

def get_transactions(username):
    filename = get_user_file(username)
    if os.path.exists(filename):
        return pd.read_csv(filename)
    else:
        return pd.DataFrame(columns=["Tarih", "Tip", "Kategori", "Tutar", "Açıklama"])
    
def get_total_by_category(username):
    df = get_transactions(username)
    gider_df = df[df["Tip"] == "Gider"]
    return gider_df.groupby("Kategori")["Tutar"].sum()

def get_monthly_totals(username):
    df = get_transactions(username)
    df["Tarih"] = pd.to_datetime(df["Tarih"])
    df["Ay"] = df["Tarih"].dt.to_period("M").astype(str)
    return df.groupby(["Ay", "Tip"])["Tutar"].sum().unstack().fillna(0)