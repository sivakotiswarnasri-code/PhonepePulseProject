import streamlit as st
from streamlit_option_menu import option_menu
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import mysql.connector as sql
from matplotlib import cm
import plotly.express as px
import squarify
import plotly.graph_objects as go

#dataframe creation

my_db = sql.connect(
    host='localhost',
    user='root',
    password='12345678',
    database='phone_pe_pulse'
)
cursor = my_db.cursor()


def Transaction_by_year(year):
    query = """
    SELECT States, SUM(Transaction_count) AS Transaction_count
    FROM aggregated_transaction
    WHERE Years = {year}
    GROUP BY States
    """
    return pd.read_sql(query, my_db)

def Quarterly_analysis():
    query = """
    SELECT Years, Quater, SUM(Transaction_count) AS Transaction_count
    FROM aggregated_transaction
    GROUP BY Years, Quater
    ORDER BY Years, Quater
    """
    return pd.read_sql(query, my_db)

def Transaction_type_analysis():
    query = """
    SELECT Transaction_type, SUM(Transaction_count) AS Transaction_count
    FROM aggregated_transaction
    GROUP BY Transaction_type
    """
    df = pd.read_sql(query, my_db)

    all_types = ["Financial Services","Merchant Payments","Peer-to-Peer","Other Transaction Type","Recharge & Bill Payment"]
    df = df.set_index("Transaction_type").reindex(all_types, fill_value=0).reset_index()

    return df

def Growth_analysis():
    query = """
    SELECT Years, SUM(Transaction_count) AS Transaction_count
    FROM aggregated_transaction
    GROUP BY Years
    ORDER BY Years
    """
    df = pd.read_sql(query, my_db)
    df["Growth_%"] = df["Transaction_count"].pct_change() * 100
    return df

def High_low_analysis():
    query = """
    SELECT 
        CASE 
            WHEN Transaction_amount > (SELECT AVG(Transaction_amount) FROM aggregated_transaction)
            THEN 'High Value'
            ELSE 'Low Value'
        END AS Category,
        SUM(Transaction_count) AS Transaction_count
    FROM aggregated_transaction
    GROUP BY Category
    """
    return pd.read_sql(query, my_db)



st.set_page_config(layout="wide")
st.title("PHONEPE TRANSACTION INSIGHTS")

with st.sidebar:

    select= option_menu("Navigation", ["Home", "Analysis"])

if select == "Home":


    query = """
    SELECT States, SUM(Transaction_count) AS value
    FROM aggregated_transaction
    GROUP BY States
    """

    df_map = pd.read_sql(query, my_db)



    df_map.rename(columns={
        "States": "state"
    }, inplace=True)

    st.subheader("India State-wise Transaction Map")

    fig_map = px.choropleth(
        df_map,
        geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
        featureidkey="properties.ST_NM",
        locations="state",
        color="value",
        color_continuous_scale="Reds",
        title="State-wise Transaction Distribution"
    )
    fig_map.update_layout(height=600, margin= {"r":0, "t":50, "l":0, "b":0})

    fig_map.update_geos(fitbounds="locations", visible=False)

    st.plotly_chart(fig_map, use_container_width=True)
    st.divider()
elif select== "Analysis":

    case_study= st.selectbox("Select Case Study",["Decoding Transaction Dynamics on PhonePe",
                                                    "Transaction Analysis for Market Expansion",
                                                    "User Engagement and Growth Strategy",
                                                    "Insurance Engagement Analysis",
                                                    "Insurance Transactions Analysis"])

    if case_study== "Decoding Transaction Dynamics on PhonePe":
        st.subheader("Decoding Transaction Dynamics")
        st.subheader("High-Value Transaction States")

        query = """
        SELECT States, AVG(Transaction_amount) AS Transaction_amount
        FROM aggregated_transaction
        GROUP BY States
        """

        df_avg_amount = pd.read_sql(query, my_db)

        fig_avg_amt = px.bar(
        df_avg_amount.sort_values("Transaction_amount", ascending=False),
        x="States",
        y="Transaction_amount",
        color="Transaction_amount",
        title="Average Transaction Amount by State",
        color_continuous_scale="Viridis"
        )

        st.plotly_chart(fig_avg_amt, use_container_width=True)
        st.divider()
      
        st.subheader("Quarterly Growth Analysis")
      
        color_map={
          2018:"#6642f5",
          2019:"#c229d6",
          2020:"#15dfe6",
          2021:"#f5628e",
          2022:"#ed15a9",
          2023:"#f0b20a",
          2024:"#bef00c",
        } 
       
        df2= Quarterly_analysis()

        years= sorted(df2["Years"].unique())

        tabs= st.tabs([str(year) for year in years])

        for tab,year in zip(tabs,years):
           with tab:
                st.markdown(f"Year:{year}")

                df_year= df2[df2["Years"]==year]
                fig, ax= plt.subplots(figsize=(18,8))
                sns.lineplot(data=df_year, x= "Quater",y="Transaction_count", marker="o",color= color_map.get(year,"blue"), ax=ax)
                ax.set_title(f"Quarterly Growth:{year}",fontsize=16)
                st.pyplot(fig)
                st.divider()
    
        st.subheader("Transaction Type Cumulative Trend (Stacked Area)")
        #query = """
        #SELECT Years, Transaction_type, SUM(Transaction_count) AS Transaction_count
        #FROM aggregated_transaction
        #GROUP BY Years, Transaction_type
        #ORDER BY Years
        #"""

        #df_type_year = pd.read_sql(query, my_db)
        #fig_area = px.area(
          #  df_type_year,
          #  x="Years",
          ##  y="Transaction_count",
          #  color="Transaction_type",
          #  title="Transaction Type Trend Over Years (Stacked Area)",
           # labels={"Transaction_count": "Transaction Count"}
        #)
        #fig_area = px.line(
         #           df_type_year,
          #          x="Years",
           #         y="Transaction_count",
            #        title="Transaction Trend"
            #)

        #st.plotly_chart(fig, use_container_width=True)
        #st.divider()
        query = """
            SELECT Years,
            Transaction_type,
            SUM(Transaction_count) AS Transaction_count
            FROM aggregated_transaction
            GROUP BY Years, Transaction_type
            ORDER BY Years
            """


        df_type_year = pd.read_sql(query, my_db)

# Convert datatype
        df_type_year["Years"] = df_type_year["Years"].astype(str)

# Create STACKED AREA chart
        fig_area = px.area(
        df_type_year,
        x="Years",
        y="Transaction_count",
        color="Transaction_type",
        title="Transaction Type Trend Over Years",
        labels={
            "Transaction_count": "Transaction Count",
            "Years": "Year"
            }
        )

# Improve layout
        fig_area.update_layout(
        height=500
        )

# Display chart
        st.plotly_chart(
        fig_area,
        use_container_width=True,
        config={
            "displayModeBar": False
            }
        )

# Free memory
        del fig_area
       

        st.divider()
	


        
        st.header("Growth Rate & Decline Detection")
        df4= Growth_analysis()

        df4["Growth_%"]= pd.to_numeric(df4["Growth_%"],errors="coerce").fillna(0)
        df4["color"]= df4["Growth_%"].apply(lambda x: "green" if x>=0 else "red")

        fig4, ax4 = plt.subplots(figsize=(18,8), dpi=100)

        sns.lineplot(data=df4, x="Years", y="Growth_%", marker="o", ax=ax4)

        ax4.scatter(df4["Years"], df4["Growth_%"], color=df4["color"], s=120, zorder=5)

        ax4.axhline(0, color="black", linestyle="--")

        ax4.set_title("Growth Rate (%)", fontsize=16)
        ax4.set_xlabel("Years", fontsize=16)
        ax4.set_ylabel("Growth (%)", fontsize=14)

        ax4.grid(True, linestyle="--", alpha=0.5)

        st.pyplot(fig4)
        st.divider()
       
        st.header("High vs Low Value Transaction Analysis")
        df5 = High_low_analysis()
        explode=[0.1 if cat=="High Value" else 0 for cat in df5["Category"]]
        fig5, ax5 = plt.subplots(figsize=(3,3))  # Make pie chart bigger

        ax5.pie(
            df5["Transaction_count"],
            labels=df5["Category"],
            autopct="%1.1f%%",
            colors=["green", "orange"],
            radius=0.7,
            startangle=90,
            explode=explode
        )

        ax5.set_title("High vs Low Transactions", fontsize=3) 
        st.pyplot(fig5)

    elif case_study == "Transaction Analysis for Market Expansion":
        st.subheader("Transaction Analysis for Market Expansion")

        st.subheader("State-wise Transaction Growth Analysis")

# Get years from SQL
        year_query = "SELECT DISTINCT Years FROM aggregated_transaction ORDER BY Years"
        years_df = pd.read_sql(year_query, my_db)

        year = st.selectbox("Select Year for Growth Analysis", years_df["Years"], key="market_year1")

# Get data from SQL
        query = """
        SELECT States, SUM(Transaction_count) AS Transaction_count
        FROM aggregated_transaction
        WHERE Years = %s
        GROUP BY States
        """

        df_state_growth = pd.read_sql(query, my_db, params=(year,))

# Plot
        fig6, ax6 = plt.subplots(figsize=(12,6))
        sns.barplot(data=df_state_growth, x="States", y="Transaction_count", palette="viridis", ax=ax6)

        plt.xticks(rotation=90)
        ax6.set_title(f"State-wise Transaction Count - {year}")

        st.pyplot(fig6)
        st.divider()


        st.header("Low-Performance State Identification")
        query = f"""
            SELECT 
            States,
            SUM(Transaction_count) AS Transaction_count,
            CASE 
                WHEN SUM(Transaction_count) < 
                (SELECT AVG(state_total)
                FROM (
                 SELECT SUM(Transaction_count) AS state_total
                 FROM aggregated_transaction
                 WHERE Years = {year}
                 GROUP BY States
                ) AS sub)
                THEN 'Low Risk'
            ELSE 'High Risk'
            END AS Performance
            FROM aggregated_transaction
            WHERE Years = {year}
            GROUP BY States
            """
       
        df_state_growth = pd.read_sql(query, my_db)
        fig7= go.Figure(
            go.Heatmap(
                z=[df_state_growth["Transaction_count"].tolist()],
                x=df_state_growth["States"],
                y=["Transaction Count"],
                text=[df_state_growth["Performance"].tolist()],
                hovertemplate="State: %{x}<br>Transactions: %{z}<br>Risk: %{text}<extra></extra>",
                colorscale=[[0,"yellow"],[1,"red"]],
                showscale=False
            )
        )

        fig7.update_layout(title="State-wise Performance Heatmap(Low vs High Risk)")
        st.plotly_chart(fig7)


        st. header("Year-wise Market Expansion Trend")
        query = """
        SELECT Years, SUM(Transaction_count) AS Transaction_count
        FROM aggregated_transaction
        GROUP BY Years
        ORDER BY Years
        """
        df_year_trend = pd.read_sql(query, my_db)
        fig8, ax8= plt.subplots(figsize=(12,6))
        sns.lineplot(data=df_year_trend, x="Years",y="Transaction_count", marker="o", color="blue", ax= ax8)
        ax8.set_title("Year-wise Total Transactions(Market Expanion Trend)")
        st.pyplot(fig8)
        st.divider()

        st.header("District-level Penetration Analysis (Lollipop Chart)")
        

        states_df = pd.read_sql("SELECT DISTINCT States FROM map_transaction", my_db)
        state_for_district = st.selectbox(
            "Select State for District ",
            states_df["States"], key="district_state"
        )

        state_for_district_safe = state_for_district.replace("'", "\\'")

        query = f"""
        SELECT Districts, SUM(Transaction_count) AS Transaction_count
        FROM map_transaction
        WHERE States = '{state_for_district_safe}'
        GROUP BY Districts
        ORDER BY Transaction_count DESC
        LIMIT 10
        """

        df_top10 = pd.read_sql(query, my_db)

        if df_top10.empty:
            st.warning(f"No transaction data found for {state_for_district}")
        else:
           
            y_pos = range(len(df_top10))

            fig, ax = plt.subplots(figsize=(12,6))

           
            ax.hlines(
                y=y_pos,
                xmin=0,
                xmax=df_top10["Transaction_count"],
                color="skyblue",
                linewidth=3
            )

           
            ax.plot(
                df_top10["Transaction_count"],
                y_pos,
                "o",
                color="orange",
                markersize=10
            )

            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(df_top10["Districts"])

            
            for i, row in df_top10.iterrows():
                ax.text(
                    row.Transaction_count + max(df_top10["Transaction_count"]) * 0.01,
                    i,
                    f"{row.Transaction_count:,}",
                    va="center",
                    fontsize=10
                )

            
        ax.set_xlabel("Transaction Count", fontsize=12)
        ax.set_ylabel("Districts", fontsize=12)
        ax.set_title(f"Top 10 Districts by Transaction Count - {state_for_district}", fontsize=14)

           
        st.pyplot(fig)

        st.header("Top States Driving Transaction Volume")

        query_states = "SELECT DISTINCT States FROM aggregated_transaction"
        df_states = pd.read_sql(query_states, my_db)

        state_selected = st.selectbox("Select State", df_states["States"].tolist())

        query_txn = f"""
        SELECT Transaction_type, SUM(Transaction_count) AS Transaction_count
        FROM aggregated_transaction
        WHERE States = '{state_selected}'
        GROUP BY Transaction_type
        ORDER BY Transaction_count DESC
        """
        df_txn = pd.read_sql(query_txn, my_db)

        fig_txn = px.bar(
            df_txn,
            x="Transaction_count",
            y="Transaction_type",
            orientation="h",
            title=f"Transaction Volume by Type - {state_selected}",
            color="Transaction_count",
            color_continuous_scale="Oranges"
        )
        fig_txn.update_layout(yaxis={'categoryorder':'total ascending'})  # Largest on top
        st.plotly_chart(fig_txn, use_container_width=True)



    elif case_study == "User Engagement and Growth Strategy":
        st.subheader("User Engagement and Growth Strategy")

        st.header("High App Opens → Strong Engagement Regions(Treemap)")
        year_query = """
        SELECT DISTINCT Years 
        FROM map_users 
        WHERE AppOpens > 0
        ORDER BY Years
        """
        years_df = pd.read_sql(year_query, my_db)

        year_for_user = st.selectbox(
            "Select Year",
            years_df["Years"],
            key="user_year2"
        )
        query = f"""
        SELECT States, SUM(AppOpens) AS AppOpens
        FROM map_users
        WHERE Years = {year_for_user}
        GROUP BY States
        """
        df_state_engagement = pd.read_sql(query, my_db)
        if not df_state_engagement.empty:
            fig_user2 = px.treemap(
            df_state_engagement,
            path=["States"],
            values="AppOpens",
            color="AppOpens",
            color_continuous_scale="Blues",
            title=f"App Opens Distribution by State - {year_for_user}"
            )

            st.plotly_chart(fig_user2, use_container_width=True)

        else:
            st.warning("No data available for selected year ")
            st.divider()
        st.header("Category-wise User Engagement")

        query_years = """
        SELECT DISTINCT Years
        FROM aggregated_user
        ORDER BY Years
        """
        years_df = pd.read_sql(query_years, my_db)
        years = years_df["Years"].tolist()

       
        tabs = st.tabs([str(year) for year in years])

        for i, year in enumerate(years):
         with tabs[i]:
        # Use an f-string to substitute the year
            query_brands = f"""
            SELECT Brands, SUM(Transaction_count) AS Transaction_count
            FROM aggregated_user
            WHERE Years = {year} AND Transaction_count > 0
            GROUP BY Brands
            ORDER BY Transaction_count DESC
        """
        df_brands = pd.read_sql(query_brands, my_db)

        if not df_brands.empty:
            df_brands_top = df_brands.head(5)

            fig = px.pie(
                df_brands_top,
                names="Brands",
                values="Transaction_count",
                title=f"Category-wise User Engagement - {year}",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df_brands)
        else:
            st.warning(f"No transaction data available for {year}")
        st.header("State-Level Transaction Inequality")
        query = """
            SELECT 
                States,
                SUM(Transaction_count) AS Transaction_count,
                CASE 
                    WHEN SUM(Transaction_count) >= (
                        SELECT AVG(state_total)
                        FROM (
                            SELECT SUM(Transaction_count) AS state_total
                            FROM aggregated_transaction
                            GROUP BY States
                        ) AS sub
                    )
                    THEN 'Above Avg'
                    ELSE 'Below Avg'
                END AS Category
            FROM aggregated_transaction
            GROUP BY States
            ORDER BY Transaction_count DESC
            """

        df_state_txn = pd.read_sql(query, my_db)
        fig_user4 = px.bar(
        df_state_txn.sort_values("Transaction_count", ascending=False),
        x="States",
        y="Transaction_count",
        color="Category",
        title="State-Level Transaction Inequality",
        color_discrete_map={"Above Avg":"green","Below Avg":"red"}
        )
        st.plotly_chart(fig_user4, use_container_width=True)
        st.divider()

        st.header("Top Districts Driving Growth")

        query_states = "SELECT DISTINCT States FROM map_users ORDER BY States"
        df_states = pd.read_sql(query_states, my_db)
        states = df_states["States"].tolist()

    
        state_for_top_districts = st.selectbox(
            "Select State", states, key="user_state_district"
        )

        query_district = f"""
        SELECT Districts, SUM(RegisteredUsers) AS RegisteredUsers, SUM(AppOpens) AS AppOpens
        FROM map_users
        WHERE States = '{state_for_top_districts}'
        GROUP BY Districts
        ORDER BY RegisteredUsers DESC
        LIMIT 10
        """

        df_district_growth = pd.read_sql(query_district, my_db)

        
        if not df_district_growth.empty:
            fig_user5, ax_user5 = plt.subplots(figsize=(12,6))
            
            ax_user5.barh(df_district_growth["Districts"], df_district_growth["RegisteredUsers"], color="purple")
            
           
            for i, val in enumerate(df_district_growth["RegisteredUsers"]):
                ax_user5.text(val + max(df_district_growth["RegisteredUsers"]) * 0.01, i, f"{val:,}", va="center")
            
            ax_user5.set_xlabel("Registered Users", fontsize=12)
            ax_user5.set_ylabel("Districts", fontsize=12)
            ax_user5.set_title(f"Top 10 Districts Driving Growth - {state_for_top_districts}", fontsize=14)
            ax_user5.invert_yaxis()
            
            plt.tight_layout()
            st.pyplot(fig_user5)
        else:
            st.warning(f"No data available for {state_for_top_districts}")

        st.divider()
                

        st.header("Quarterly App Engagement Trend by State")
        query = """
        SELECT States, Quater, SUM(AppOpens) AS AppOpens
        FROM map_users
        GROUP BY States, Quater
        ORDER BY States, Quater
        """
        df_peak = pd.read_sql(query, my_db)
        fig_line = px.line(
                df_peak,
                x="Quater",
                y="AppOpens",
                color="States",
                markers=True,
                title="Quarterly AppOpens Trend by State"
        )
        st.plotly_chart(fig_line, use_container_width=True)
        st.divider()

    elif case_study == "Insurance Engagement Analysis":
        st.subheader("Insurance Engagement Analysis")

        st.header("State-wise Insurance Adoption Analysis")


        Aggre_insurance = pd.read_sql("SELECT * FROM aggregated_insurance", my_db)

       
        year_ins = st.selectbox(
            "Select Year", 
            sorted(Aggre_insurance["Years"].unique()),  # now this works
            key="ins_year1"
        )

        df_ins_state = (
            Aggre_insurance[Aggre_insurance["Years"] == year_ins]
            .groupby("States")["Transaction_count"]
            .sum()
            .reset_index()
            .sort_values("Transaction_count", ascending=False)
            .head(8)
        )

        fig14 = px.pie(
            df_ins_state,
            names="States",
            values="Transaction_count",
            title=f"Top States Share in Insurance Adoption - {year_ins}"
        )

        st.plotly_chart(fig14, use_container_width=True)
        st.header("User Engagement vs Transactions Trend")

        query_users_year = """
        SELECT Years, SUM(Transaction_count) AS User_Transactions
        FROM aggregated_user
        GROUP BY Years
        ORDER BY Years
        """
        df_users_year = pd.read_sql(query_users_year, my_db)

        query_ins_year = """
        SELECT Years, SUM(Transaction_count) AS Insurance_Transactions
        FROM aggregated_insurance
        GROUP BY Years
        ORDER BY Years
        """
        df_ins_year = pd.read_sql(query_ins_year, my_db)

        df_trend = pd.merge(df_users_year, df_ins_year, on="Years", how="outer").fillna(0)
        fig = px.line(
            df_trend,
            x="Years",
            y=["User_Transactions", "Insurance_Transactions"],
            markers=True,
            title="Yearly User Transactions vs Insurance Transactions",
            labels={
                "value": "Transaction Count",
                "variable": "Category"
            }
        )

        st.plotly_chart(fig, use_container_width=True)        
        st.header("Low Engagement Region Identification")
       
        query_users_state = """
        SELECT States, SUM(RegisteredUsers) AS RegisteredUsers, SUM(AppOpens) AS AppOpens
        FROM map_users
        GROUP BY States
        ORDER BY States
        """
        df_engagement = pd.read_sql(query_users_state, my_db)

        query_ins_state = """
        SELECT States, SUM(Transaction_count) AS Transaction_count
        FROM aggregated_insurance
        GROUP BY States
        ORDER BY States
        """
        df_ins_txn = pd.read_sql(query_ins_state, my_db)

        # Merge datasets on States
        df_merge = pd.merge(df_engagement, df_ins_txn, on="States")

        # Identify Low Engagement regions
        avg_txn = df_merge["Transaction_count"].mean()
        avg_users = df_merge["RegisteredUsers"].mean()

        df_merge["Category"] = df_merge.apply(
            lambda row: "Low Engagement" 
            if (row["Transaction_count"] < avg_txn and row["RegisteredUsers"] < avg_users)
            else "Active Region",
            axis=1
        )

        # Plot
        fig17 = px.bar(
            df_merge.sort_values("Transaction_count"),
            x="States",
            y="Transaction_count",
            color="Category",
            title="Low Engagement Regions",
            color_discrete_map={"Low Engagement":"red","Active Region":"green"}
        )
        fig17.update_layout(xaxis_tickangle=-45)

        st.plotly_chart(fig17, use_container_width=True)
        st.divider()
        
        st.header("Quarterly Growth Trend Analysis(Area Chart)")

      
        query_quarter = """
        SELECT Years, Quater, SUM(Transaction_count) AS Transaction_count
        FROM aggregated_insurance
        GROUP BY Years, Quater
        ORDER BY Years, Quater
        """
        df_quarter = pd.read_sql(query_quarter, my_db)

        # Plot stacked area chart
        fig18 = px.area(
            df_quarter,
            x="Quater",
            y="Transaction_count",
            color="Years",
            title="Quarterly Insurance Growth Trend",
            labels={"Transaction_count":"Transaction Count", "Quater":"Quarter"}
        )

        st.plotly_chart(fig18, use_container_width=True)
        st.divider()
        
        st.header("Insurance Product Popularity Analysis")

        # SQL query to get top 10 states by insurance transactions
        query_top_states = """
        SELECT States, SUM(Transaction_count) AS Transaction_count
        FROM aggregated_insurance
        GROUP BY States
        ORDER BY Transaction_count DESC
        LIMIT 10
        """

        df_product = pd.read_sql(query_top_states, my_db)

        # Pie chart for top states in insurance adoption
        fig15 = px.pie(
            df_product,
            names="States",
            values="Transaction_count",
            hole=0.4,
            title="Top States in Insurance Adoption"
        )

        fig15.update_traces(textinfo="percent+label", textposition="outside")
        fig15.update_layout(showlegend=False)

        st.plotly_chart(fig15, use_container_width=True)
        st.divider()
                
    elif case_study == "Insurance Transactions Analysis":

        st.subheader("Insurance Transactions Analysis")

        st.header("Correlation Between Transaction Count and Amount")


        # SQL query to get yearly sum of transaction count and amount
        query_corr = """
        SELECT Years, 
            SUM(Transaction_count) AS Transaction_count,
            SUM(Transaction_amount) AS Transaction_amount
        FROM aggregated_insurance
        GROUP BY Years
        ORDER BY Years
        """

        df_year = pd.read_sql(query_corr, my_db)

        # Line chart to show correlation
        fig19 = px.line(
            df_year,
            x="Years",
            y=["Transaction_count", "Transaction_amount"],
            markers=True,
            title="Transaction Count vs Amount Trend"
        )

        st.plotly_chart(fig19, use_container_width=True)

        st.header("Insurance Penetration vs Population Density")
        st.header("Insurance Penetration vs Population Density")

# SQL query: get top 10 states by total transactions (users + insurance)
        query_user_ins = """
        SELECT 
            u.States,
            u.Total_Users,
            COALESCE(i.Total_Insurance, 0) AS Total_Insurance
        FROM (
            SELECT States, SUM(Transaction_count) AS Total_Users
            FROM aggregated_user
            GROUP BY States
        ) u
        LEFT JOIN (
            SELECT States, SUM(Transaction_count) AS Total_Insurance
            FROM aggregated_insurance
            GROUP BY States
        ) i
        ON u.States = i.States
        ORDER BY u.Total_Users DESC
        LIMIT 10
        """

        # Execute query
        df_merge = pd.read_sql(query_user_ins, my_db)

        # Display table for verification
        st.dataframe(df_merge)


        fig = go.Figure()

        # Primary y-axis: Registered Users
        fig.add_trace(go.Bar(
            x=df_merge["States"],
            y=df_merge["Total_Users"],
            name="Registered Users",
            marker_color="blue",
            yaxis="y1"
        ))

        # Secondary y-axis: Insurance Transactions
        fig.add_trace(go.Bar(
            x=df_merge["States"],
            y=df_merge["Total_Insurance"],
            name="Insurance Transactions",
            marker_color="orange",
            yaxis="y2"
        ))

        # Layout with dual y-axis
        fig.update_layout(
            title="User vs Insurance Transactions (Top 10 States)",
            xaxis=dict(title="States"),
            yaxis=dict(
                title="Registered Users",
                showgrid=False,
                side="left"
            ),
            yaxis2=dict(
                title="Insurance Transactions",
                overlaying="y",
                side="right"
            ),
            barmode="group",
            legend=dict(x=0.7, y=1.1),
            template="plotly_white"
        )

        st.plotly_chart(fig, use_container_width=True)
# SQL query using correct column names
        st.header("Year-over-Year Insurance Growth")

        # SQL query to calculate Year-over-Year growth for insurance transactions
        query_yoy = """
        WITH yearly_txn AS (
            SELECT Years, SUM(Transaction_count) AS Transaction_count
            FROM aggregated_insurance
            GROUP BY Years
        ),
        yoy_calc AS (
            SELECT 
                Years,
                Transaction_count,
                LAG(Transaction_count) OVER (ORDER BY Years) AS prev_year_txn
            FROM yearly_txn
        )
        SELECT
            Years,
            Transaction_count,
            CASE 
                WHEN prev_year_txn IS NULL THEN 0
                ELSE ROUND((Transaction_count - prev_year_txn) * 100.0 / prev_year_txn, 2)
            END AS Growth_Percent
        FROM yoy_calc
        ORDER BY Years
        """

        df_yoy = pd.read_sql(query_yoy, my_db)

        # Area chart showing YoY Growth %
        fig_area = px.area(
            df_yoy,
            x="Years",
            y="Growth_Percent",
            title="Year-over-Year Insurance Growth (%)",
            markers=True,
            color_discrete_sequence=["#f0e40a"]
        )

        st.plotly_chart(fig_area, use_container_width=True)

        st.header("Market Concentration Analysis")

        # SQL query to calculate Top 5 States vs Others
        query_top5 = """
        WITH state_sum AS (
            SELECT States, SUM(Transaction_count) AS Transaction_count
            FROM aggregated_insurance
            GROUP BY States
        ),
        ranked AS (
            SELECT
                States,
                Transaction_count,
                ROW_NUMBER() OVER (ORDER BY Transaction_count DESC) AS rn
            FROM state_sum
        )
        SELECT
            CASE WHEN rn <= 5 THEN 'Top 5 States' ELSE 'Other States' END AS Category,
            SUM(Transaction_count) AS Value
        FROM ranked
        GROUP BY Category
        """

        df_pie = pd.read_sql(query_top5, my_db)

        fig21 = px.pie(
            df_pie,
            names="Category",
            values="Value",
            title="Top 5 States vs Others"
        )

        st.plotly_chart(fig21, use_container_width=True)
        st.divider()

        st.header("Average Insurance Transaction Value by State")

        # SQL query to calculate average transaction value by state
        query_avg_value = """
        SELECT 
            States,
            SUM(Transaction_amount) AS Total_Amount,
            SUM(Transaction_count) AS Total_Transactions,
            CASE WHEN SUM(Transaction_count) = 0 THEN 0 
                ELSE SUM(Transaction_amount) / SUM(Transaction_count) 
            END AS Avg_Value
        FROM aggregated_insurance
        GROUP BY States
        ORDER BY Avg_Value DESC
        """

        df_avg = pd.read_sql(query_avg_value, my_db)

        fig22 = px.bar(
            df_avg,
            x="States",
            y="Avg_Value",
            title="Average Transaction Value by State",
            color="Avg_Value",
            color_continuous_scale=px.colors.sequential.Viridis
        )

        fig22.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig22, use_container_width=True)
        st.divider()
                

        
