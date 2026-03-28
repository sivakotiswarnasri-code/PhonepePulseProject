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

#aggregate_insurance_df
cursor.execute("SELECT * FROM aggregated_insurance")


table1= cursor.fetchall()

Aggre_insurance= pd.DataFrame(table1, columns=("States","Years","Quater","Transaction_type",
                                                     "Transaction_count",
                                                     "Transaction_amount"))



#aggregate_transaction_df
cursor.execute("SELECT * FROM aggregated_transaction")


table2= cursor.fetchall()

Aggre_transaction= pd.DataFrame(table2, columns=("States","Years","Quater","Transaction_type",
                                                     "Transaction_count",
                                                     "Transaction_amount"))


#aggregate_users_df
cursor.execute("SELECT * FROM aggregated_user")


table3= cursor.fetchall()

Aggre_user= pd.DataFrame(table3, columns=("States","Years","Quater","Brands",
                                                     "Transaction_count",
                                                     "Percentage"))

#map_insurance_df
cursor.execute("SELECT * FROM map_insurance")


table4= cursor.fetchall()

Map_insurance= pd.DataFrame(table4, columns=("States","Years","Quater","Districts",
                                                     "Transaction_count",
                                                     "Transaction_amount"))

#map_transactions_df
cursor.execute("SELECT * FROM map_transaction")


table5= cursor.fetchall()

Map_transaction= pd.DataFrame(table5, columns=("States","Years","Quater","Districts",
                                                     "Transaction_count",
                                                     "Transaction_amount"))

#map_user_df
cursor.execute("SELECT * FROM map_users")


table6= cursor.fetchall()

Map_users= pd.DataFrame(table6, columns=("States","Years","Quater","Districts",
                                                     "RegisteredUsers",
                                                     "AppOpens"))

#top_insurance_df
cursor.execute("SELECT * FROM top_insurance")


table7= cursor.fetchall()

Top_insurance= pd.DataFrame(table7, columns=("States","Years","Quater","Pincodes",
                                                     "Transaction_count",
                                                     "Transaction_amount"))

#top_transaction_df
cursor.execute("SELECT * FROM top_transaction")


table8= cursor.fetchall()

Top_transaction= pd.DataFrame(table8, columns=("States","Years","Quater","Pincodes",
                                                     "Transaction_count",
                                                     "Transaction_amount"))

#top_user_df
cursor.execute("SELECT * FROM top_user")


table9= cursor.fetchall()

Top_user= pd.DataFrame(table9, columns=("States","Years","Quater","Pincodes",
                                                     "RegisteredUsers"))


def Transaction_by_year(year):
    ty= Aggre_transaction[Aggre_transaction["Years"]== year]
    ty.reset_index(drop= True, inplace=True)

    tyg= ty.groupby("States")["Transaction_count"].sum().reset_index()
    return tyg

def Quarterly_analysis():
    qag= Aggre_transaction.groupby(["Years","Quater"])["Transaction_count"].sum().reset_index()
    return qag

def Transaction_type_analysis():
    Tta=Aggre_transaction.groupby("Transaction_type")["Transaction_count"].sum().reset_index()
    all_types= ["Financial Services","Merchant Payments","Peer-to-Peer","Other Transaction Type","Recharge & Bill Payment"]
    Tta= Tta.set_index("Transaction_type").reindex(all_types, fill_value=0).reset_index()

    return Tta

def Growth_analysis():
    ga= Aggre_transaction.groupby("Years")["Transaction_count"].sum().reset_index()
    ga["Growth_%"]= ga["Transaction_count"].pct_change()*100
    return ga

def High_low_analysis():
    Ha= Aggre_transaction.copy()
    avg= Ha["Transaction_amount"].mean()
    Ha["Category"]= Ha["Transaction_amount"].apply(lambda x: "High Value" if x>avg else "Low Value")

    Ha= Ha.groupby("Category")["Transaction_count"].sum().reset_index()
    return Ha

#streamlit part

st.set_page_config(layout="wide")
st.title("PHONEPE TRANSACTION INSIGHTS")

with st.sidebar:

    select= option_menu("Navigation", ["Home", "Analysis"])

if select == "Home":


    df_map = Aggre_transaction.groupby("States")["Transaction_count"].sum().reset_index()

# Rename columns to match choropleth requirements
    df_map.rename(columns={
        "States": "state",
        "Transaction_count": "value"
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
        df_avg_amount = Aggre_transaction.groupby("States")["Transaction_amount"].mean().reset_index()
        fig_avg_amt = px.bar(df_avg_amount.sort_values("Transaction_amount", ascending=False),
                     x="States", y="Transaction_amount", color="Transaction_amount",
                     title="Average Transaction Amount by State", color_continuous_scale="Viridis")
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
        df_type_year = Aggre_transaction.groupby(["Years","Transaction_type"])["Transaction_count"].sum().reset_index()
        fig_area = px.area(
            df_type_year,
            x="Years",
            y="Transaction_count",
            color="Transaction_type",
            title="Transaction Type Trend Over Years (Stacked Area)",
            labels={"Transaction_count": "Transaction Count"}
        )
        st.plotly_chart(fig_area, use_container_width=True)
        st.divider()
           


        
        st.header("Growth Rate & Decline Detection")
        df4= Growth_analysis()

        df4["Growth_%"]= pd.to_numeric(df4["Growth_%"],errors="coerce").fillna(0)
        df4["color"]= df4["Growth_%"].apply(lambda x: "green" if x>=0 else "red")

        fig4, ax4= plt.subplots(figsize=(18,8),dpi=100)

        ax4.plot(df4["Years"], df4["Growth_%"], color="blue", linewidth=2, linestyle="-", marker="o")
        ax4.scatter(df4["Years"], df4["Growth_%"], color=df4["color"],s=120, zorder=5)
        sns.lineplot(data=df4, x="Years",y="Growth_%", marker="o",color="blue", ax= ax4)
        ax4.axhline(0, color="black",linestyle="--")
        ax4.set_ylim(min(df4["Growth_%"].min(),0)-1, df4["Growth_%"].max()+1)
        ax4.set_title("Growth Rate (%) ", fontsize=16)
        ax4.set_xlabel("Years",fontsize=16)
        ax4.set_ylabel("Growth(%)", fontsize=14)
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

        ax5.set_title("High vs Low Transactions", fontsize=3)  # Use ax5, not ax
        st.pyplot(fig5)

    elif case_study == "Transaction Analysis for Market Expansion":
        st.subheader("Transaction Analysis for Market Expansion")

        st.subheader("State-wise Transaction Growth Analysis")
        year = st.selectbox("Select Year for Growth Analysis", Aggre_transaction["Years"].unique(), key="market_year1")
        df_state_growth = Aggre_transaction[Aggre_transaction["Years"]==year].groupby("States")["Transaction_count"].sum().reset_index()
        fig6,ax6= plt.subplots(figsize=(12,6))
        sns.barplot(data=df_state_growth, x= "States", y="Transaction_count", palette="viridis",ax=ax6)
        plt.xticks(rotation=90)
        ax6.set_title(f"State-wise Transaction Count- {year}")
        st.pyplot(fig6)
        st.divider()


        st.header("Low-Performance State Identification")
        avg_txn= df_state_growth["Transaction_count"].mean()
        df_state_growth["Performance"] =df_state_growth["Transaction_count"].apply(
            lambda x: "Low Risk" if x< df_state_growth["Transaction_count"].mean() else "High Risk")

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
        df_year_trend= Aggre_transaction.groupby(["Years"])["Transaction_count"].sum().reset_index()
        fig8, ax8= plt.subplots(figsize=(12,6))
        sns.lineplot(data=df_year_trend, x="Years",y="Transaction_count", marker="o", color="blue", ax= ax8)
        ax8.set_title("Year-wise Total Transactions(Market Expanion Trend)")
        st.plotly_chart(fig8)
        st.divider()

        st.header("District-level Penetration Analysis (Lollipop Chart)")
        state_for_district=st.selectbox("Select State",
                                        Map_transaction["States"].unique(),
                                        key= "Market_State_District")
        
        df_district= (
            Map_transaction[Map_transaction["States"]== state_for_district].groupby("Districts")["Transaction_count"]
                                                    .sum().sort_values(ascending=False).reset_index()
        )

        df_top10= df_district.head(10)
        fig9, ax9= plt.subplots(figsize=(12,6))
        ax9.hlines(y= df_top10["Districts"],
                    xmin=0,
                    xmax= df_top10["Transaction_count"],
                    color="blue",
                    linewidth=2)
        
        ax9.plot(df_top10["Transaction_count"],
                df_top10["Districts"],
                "o",
                color="orange",
                markersize=10)
        
        for i, row in df_top10.iterrows():
            ax9.text(
                row["Transaction_count"]+max(df_top10["Transaction_count"])*0.01, row["Districts"],
                f"{row["Transaction_count"]:,}",
                va="center",
                fontsize=10
            )

        ax9.set_xlabel("Transaction Count", fontsize=12)
        ax9.set_ylabel("Districts", fontsize=12)
        ax9.set_title(f"Top 10 Districts by Transaction Count- {state_for_district}",fontsize=14)
        st.pyplot(fig9)        


        st.header("Categorical-wise Transaction Analysis")
        df_category= Aggre_transaction[Aggre_transaction["Years"]==year].copy()
        df_category["Transaction_type"]= df_category["Transaction_type"].str.strip().str.title()

        df_category["Transaction_type"]= df_category["Transaction_type"].replace({
            "Recharge & Bill payment": "Recharge & Bill payment",
            "Peer-to-Peer": "Peer-to-Peer"
        })
        df_category= df_category.groupby("Transaction_type")["Transaction_count"].sum().reset_index()
        
        all_types= ['Financial Services','Peer-to-Peer', 'Recharge & Bill payment','Other Transaction Type','Merchant Payments']

        df_category= df_category.set_index("Transaction_type").reindex(all_types, fill_value=0).reset_index()
       
        explode=[0.1 if cat=="Financial Services" else 0 for cat in df_category["Transaction_type"]]
        
        fig10=px.pie(df_category,
                     names="Transaction_type",
                     values="Transaction_count",
                     title=f"Category-wise Transaction Distribution-{year}",
                     color="Transaction_type",
                     color_discrete_sequence=px.colors.qualitative.Set3
        )
    
        fig10. update_traces(
            textposition="inside",
            textinfo="percent+label",
            pull=explode,
            hovertemplate="<b>%{label}</b><br>Transactions: %{value}<br>Percent: %{percent}<extra></extra>"
        )
        st.plotly_chart(fig10, use_container_width=True)
        st.divider()
    elif case_study == "User Engagement and Growth Strategy":
        st.subheader("User Engagement and Growth Strategy")

        st.header("High App Opens → Strong Engagement Regions(Treemap)")
        valid_years= Map_users.groupby("Years")["AppOpens"].sum()
        valid_years1= valid_years[valid_years>0].index.tolist()
        year_for_user = st.selectbox("Select Year", sorted(valid_years1), key="user_year2")
        
        df_map_users = Map_users[Map_users["Years"].astype(str)==str(year_for_user)]
        df_state_engagement = df_map_users.groupby("States")["AppOpens"].sum().reset_index()

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
        valid_years_series= Aggre_user.groupby("Years")["Transaction_count"].sum()
        years= sorted(valid_years_series[valid_years_series>0].index.tolist())
        tabs= st.tabs([str(year) for year in years])

        for i, year in enumerate(years):
            with tabs[i]:

                df_cat_user = Aggre_user[Aggre_user["Years"]==year]
                df_grouped = df_cat_user.groupby("Brands")["Transaction_count"].sum().reset_index()
    
                if not df_grouped.empty:
                    fig_user3 = px.pie(
                        df_grouped,
                        names="Brands",
                        values="Transaction_count",
                        title=f"Category-wise User Engagement - {year_for_user}",
                        color_discrete_sequence=px.colors.qualitative.Set2
                    )
                    fig_user3.update_traces(textposition="inside", textinfo="percent+label")
                    st.plotly_chart(fig_user3, use_container_width=True)
                else:
                    st.warning(f"No data available for {year}")

        st.header("State-Level Transaction Inequality")
        df_state_txn = Aggre_transaction.groupby("States")["Transaction_count"].sum().reset_index()
        avg_txn_count = df_state_txn["Transaction_count"].mean()
        df_state_txn["Category"] = df_state_txn["Transaction_count"].apply(lambda x: "Above Avg" if x>=avg_txn_count else "Below Avg")
    
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
        state_for_top_districts = st.selectbox("Select State", Map_users["States"].unique(), key="user_state_district")
        df_district_growth = Map_users[Map_users["States"]==state_for_top_districts].groupby("Districts")[["RegisteredUsers","AppOpens"]].sum().sort_values("RegisteredUsers", ascending=False).head(10).reset_index()
    
        fig_user5, ax_user5 = plt.subplots(figsize=(12,6))
        ax_user5.barh(df_district_growth["Districts"], df_district_growth["RegisteredUsers"], color="purple")
        for i, val in enumerate(df_district_growth["RegisteredUsers"]):
            ax_user5.text(val+max(df_district_growth["RegisteredUsers"])*0.01, i, f"{val:,}", va="center")
            ax_user5.set_xlabel("Registered Users")
            ax_user5.set_ylabel("Districts")
            ax_user5.set_title(f"Top 10 Districts Driving Growth - {state_for_top_districts}")
            ax_user5.invert_yaxis()
        st.pyplot(fig_user5)
        st.divider()        

        df_peak = Map_users.groupby(["States","Quater"])["AppOpens"].sum().reset_index()

        st.header("Quarterly App Engagement Trend by State")
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

        year_ins = st.selectbox("Select Year", Aggre_insurance["Years"].unique(), key="ins_year1")

        df_ins_state =( Aggre_insurance[Aggre_insurance["Years"] == year_ins] \
                    .groupby("States")["Transaction_count"]).sum().reset_index()

        fig14 = px.pie(
        df_ins_state.sort_values("Transaction_count", ascending=False).head(8),
        names="States",
        values="Transaction_count",
        title=f"Top States Share in Insurance Adoption - {year_ins}"
        )

        st.plotly_chart(fig14, use_container_width=True) 

        st.header("User Engagement vs Transactions Trend")


        df_users_year = Map_users.groupby("Years")[["RegisteredUsers", "AppOpens"]].sum().reset_index()
        df_txn_year = Aggre_insurance.groupby("Years")["Transaction_count"].sum().reset_index()


        df_trend = pd.merge(df_users_year, df_txn_year, on="Years")


        fig16 = px.line(
        df_trend,
        x="Years",
        y=["RegisteredUsers", "Transaction_count"],
        markers=True,
        title="User Growth vs Insurance Transactions Over Years"
        )

        st.plotly_chart(fig16, use_container_width=True)


        st.header("Low Engagement Region Identification")
        df_engagement= Map_users.groupby("States").agg({
            "RegisteredUsers":"sum",
            "AppOpens": "sum"
        }).reset_index()
        df_ins_txn=Aggre_insurance.groupby("States")["Transaction_count"].sum().reset_index()
        df_merge = pd.merge( df_engagement,  df_ins_txn, on="States")
        df_low = df_merge.copy()

        avg_txn = df_low["Transaction_count"].mean()
        avg_users = df_low["RegisteredUsers"].mean()

        df_low["Category"] = df_low.apply(
        lambda row: "Low Engagement" if (row["Transaction_count"] < avg_txn and row["RegisteredUsers"] < avg_users)
        else "Active Region",
        axis=1
        )

        fig17 = px.bar(
        df_low.sort_values("Transaction_count"),
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

        df_quarter = Aggre_insurance.groupby(["Years","Quater"])["Transaction_count"].sum().reset_index()

        fig18 = px.area(
            df_quarter,
            x="Quater",
            y="Transaction_count",
            color="Years",
            markers=True,
            title="Quarterly Insurance Growth Trend"
        )
        st.plotly_chart(fig18, use_container_width=True)
        st.divider()
        
        
        
        st.header("Insurance Product Popularity Analysis")

        df_product = Aggre_insurance.groupby("States")["Transaction_count"].sum().reset_index()
        df_product=  df_product.sort_values("Transaction_count", ascending=False).head(10)
        fig15 = px.pie(
            df_product,
            names="States",
            values="Transaction_count",
            hole=0.4,
            title="Top States in Insurance Adoption"
        )

        fig15.update_traces(textinfo="percent+label", textposition="outside")
        fig15.update_layout(showlegend= False)
        st.plotly_chart(fig15, use_container_width=True)
        st.divider() 
        
    elif case_study == "Insurance Transactions Analysis":

        st.subheader("Insurance Transactions Analysis")

        st.header("Correlation Between Transaction Count and Amount")

        df_corr = Aggre_insurance.groupby("States").agg({
            "Transaction_count": "sum",
            "Transaction_amount": "sum"
        }).reset_index()

        df_year = Aggre_insurance.groupby("Years").agg({
         "Transaction_count": "sum",
         "Transaction_amount": "sum"
        }).reset_index()

        fig19 = px.line(
        df_year,
        x="Years",
        y=["Transaction_count", "Transaction_amount"],
        markers=True,
        title="Transaction Count vs Amount Trend"
        )

        st.plotly_chart(fig19, use_container_width=True)

        st.header("Insurance Penetration vs Population Density")

        df_users = Map_users.groupby("States")["RegisteredUsers"].sum().reset_index()
        df_ins_txn = Aggre_insurance.groupby("States")["Transaction_count"].sum().reset_index()

        df_merge = pd.merge(df_users, df_ins_txn, on="States")

        fig20 = px.bar(
        df_merge.sort_values("RegisteredUsers", ascending=False).head(10),
            x="States",
            y=["RegisteredUsers", "Transaction_count"],
            barmode="group",
            title="User Base vs Insurance Transactions"
        )

        st.plotly_chart(fig20, use_container_width=True)

        st.header("Year-over-Year Insurance Growth")

        df_yoy = Aggre_insurance.groupby("Years")["Transaction_count"].sum().reset_index()
        df_yoy["Growth_%"] = df_yoy["Transaction_count"].pct_change() * 100

        fig_area = px.area(
            df_yoy,
            x="Years",
            y="Growth_%",
            title="Year-over-Year Insurance Growth (%)",
            markers=True,
            color_discrete_sequence=["#f0e40a"]
        )
        st.plotly_chart(fig_area, use_container_width=True)


        st.header("Market Concentration Analysis")

        df_conc = Aggre_insurance.groupby("States")["Transaction_count"].sum().reset_index()
        df_conc = df_conc.sort_values("Transaction_count", ascending=False)

        top5 = df_conc.head(5)["Transaction_count"].sum()
        others = df_conc["Transaction_count"].sum() - top5

        df_pie = pd.DataFrame({
        "Category": ["Top 5 States", "Other States"],
        "Value": [top5, others]
        })

        fig21 = px.pie(
            df_pie,
            names="Category",
            values="Value",
            title="Top 5 States vs Others"
        )

        st.plotly_chart(fig21, use_container_width=True)
        st.divider()

        st.header("Average Insurance Transaction Value by State")

        df_avg = Aggre_insurance.groupby("States").agg({
            "Transaction_amount": "sum",
            "Transaction_count": "sum"
        }).reset_index()

        df_avg["Avg_Value"] = df_avg["Transaction_amount"] / df_avg["Transaction_count"]

        fig22 = px.bar(
        df_avg.sort_values("Avg_Value", ascending=False),
            x="States",
            y="Avg_Value",
            title="Average Transaction Value by State",
            color="Avg_Value",
            color_continuous_scale=px.colors.sequential.Viridis
        )

        fig22.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig22, use_container_width=True)
        st.divider()
        

        
