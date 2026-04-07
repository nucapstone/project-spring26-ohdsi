import redshift_connector
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import credentials
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

#set up connections. note: the CREDENTIALS.py file is NOT to be pushed 
connection = redshift_connector.connect(
     host=credentials.HOST,
     port=credentials.PORT,
     database=credentials.DATABASE,
     user=credentials.USER,
     password=credentials.PASSWORD)

def connect():
    cursor = connection.cursor()

    query = f'''
            SELECT *
            FROM {credentials.SCHEMA}.cohort_features 
        '''
    
    cursor.execute(query)
    df = cursor.fetch_dataframe()

    connection.close()
    return df

df=connect()
print(df.shape)

df_sample = df.sample(n=20000, random_state=42)

def kde_age_bySex(df=df):
    g = sns.FacetGrid(
        df,
        col="outcome_dementia",
        hue="sex",
        height=5,
        aspect=1.2
    )

    g.map(
        sns.kdeplot,
        "age_at_t0",
        fill=True,
        alpha=0.4,
        cut=0
    )

    g.add_legend()
    g.set_axis_labels("Age at T0", "Density")
    g.set_titles("{col_name}")
    plt.savefig("figs/Age_Distribution_bySex.png")
    plt.show()


def age_hist(df=df):
    plt.figure(figsize=(8, 5))

    sns.histplot(
        data=df,
        x="age_at_t0",
        hue="outcome_dementia",
        binwidth=1,
        kde=True,
        stat="count",
        common_norm=False
    )

    plt.title("Age Distribution by Dementia Outcome")
    plt.xlabel("Age")
    plt.ylabel("Density")
    plt.savefig("figs/Age_Distribution.png")
    plt.show()

def age_counts(df=df):
    plt.figure(figsize=(6, 4))

    sns.countplot(
        data=df,
        x="sex",
        hue="outcome_dementia"
    )

    plt.title("Sex Distribution by Dementia Outcome")
    plt.xlabel("Sex")
    plt.ylabel("Count")
    plt.savefig("figs/Sex_Countplot.png")
    plt.show()

def heatmap(df=df):
    plt.figure(figsize=(14, 12))

    # Select numeric columns only
    numeric_df = df.select_dtypes(include=np.number)
    numeric_df = numeric_df.drop(columns=['person_id'])

    # Correlation matrix
    corr = numeric_df.corr()

    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        annot_kws={"size": 8}
    )

    plt.title("Correlation Heatmap", fontsize=16)
    plt.xticks(rotation=45, ha="right", fontsize=10)
    plt.yticks(fontsize=10)

    plt.tight_layout()
    plt.savefig("figs/heatmap.png")
    plt.show()

kde_age_bySex(df)
age_hist(df)
age_counts(df)
heatmap(df)