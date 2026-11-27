import pandas as pd
import matplotlib.pylab as plt

dim_journey = pd.read_csv("data/star/dim_journey.csv")
dim_railcard = pd.read_csv("data/star/dim_railcard.csv")
dim_routes = pd.read_csv("data/star/dim_routes.csv")
dim_sale_details = pd.read_csv("data/star/dim_sale_details.csv")
fact_ticket = pd.read_csv("data/star/fact_ticket.csv")

df = pd.merge(fact_ticket, dim_journey, on="journey_id", how="left")
journey_status_counts = df["journey_status"].value_counts()

df = pd.merge(fact_ticket, dim_routes, on="route_id", how="left").merge(dim_journey, on="journey_id", how="left")
df["route"] = df["departure_station"] + " → " + df["arrival_station"]
df = df.drop(columns=["departure_station", "arrival_station"])
worst_routes_crosstab = pd.crosstab(df["route"], df["journey_status"], normalize="index").sort_values("Delayed", ascending=False).head(10)

df = pd.merge(fact_ticket, dim_journey, on="journey_id", how="left")
filter = (df["reason_for_delay"] != "No Delay")
delay_reasons = df[filter]["reason_for_delay"].value_counts()

df = pd.merge(fact_ticket, dim_journey, on="journey_id", how="left")
filter = (df["refund_request"] == "Yes")
refund_by_status = (
    df[df["refund_request"] == "Yes"]
    .groupby("journey_status")["refund_request"]
    .count()
    .reindex(df["journey_status"].unique(), fill_value=0)
)

df = pd.merge(fact_ticket, dim_journey, on="journey_id", how="left")
travel_by_hour = pd.to_datetime(df["departure_time"], format="%H:%M:%S").dt.hour.value_counts().sort_index()

travel_by_hour.index = pd.to_datetime(
    travel_by_hour.index.astype(str),
    format="%H"
).strftime("%I %p").str.lstrip("0")

df = fact_ticket
df["purchase_date"] = pd.to_datetime(df["purchase_date"])
sales_per_month = df.groupby(
    df["purchase_date"].dt.to_period("M")
)["price"].sum()

colors = ["#BF4342", "#735751", "#A78A7F"] 
height = 0.4
width = 0.8

figure, axes = plt.subplots(3, 2, figsize=(16, 16))

figure.suptitle(
    "UK Train Journey Analysis",
    fontsize=48,
    fontweight="bold",
    color="#8C1C13"
)

# axes[0, 0]
wedges, texts, autotexts = axes[0, 0].pie(
    journey_status_counts.values,
    labels=journey_status_counts.index,
    autopct="%1.1f%%",
    colors=colors
)


# axes[0, 1]
axes[0, 1].barh(worst_routes_crosstab["Delayed"].index ,worst_routes_crosstab["Delayed"].values, color=colors, height=0.25)
axes[0, 1].set_xlabel("Delay Rate", fontsize=12, fontweight="bold", color="#8C1C13")

# axes[1, 0]
axes[1, 0].barh(delay_reasons.index ,delay_reasons.values, color=colors, height=height)
axes[1, 0].set_xlabel("Number of Delays", fontsize=12, fontweight="bold", color="#8C1C13")
axes[1, 0].set_ylabel("Reasons for Delay", fontsize=12, fontweight="bold", color="#8C1C13")

# axes[1, 1]
axes[1, 1].bar(refund_by_status.index ,refund_by_status.values, color=colors, width=width)
axes[1, 1].set_xlabel("Journey Status", fontsize=12, fontweight="bold", color="#8C1C13")
axes[1, 1].set_ylabel("Number of Refunds", fontsize=12, fontweight="bold", color="#8C1C13")

# axes[2, 0]
axes[2, 0].hist(
    travel_by_hour.index,
    bins=24,
    weights=travel_by_hour.values,
    color=colors[0],
    edgecolor="#8C1C13", 
)
axes[2, 0].set_xlabel("Journey Status", fontsize=12, fontweight="bold", color="#8C1C13")
axes[2, 0].set_ylabel("Number of Refunds", fontsize=12, fontweight="bold", color="#8C1C13")

axes[2, 0].set_xticks(range(0, 24, 3))
axes[2, 0].set_yticks(range(0, 5000, 1000))

# axes[2, 1]
axes[2, 1].plot(sales_per_month.index.astype(str), sales_per_month.values,
         marker=".",
         markersize=20,
         markerfacecolor=colors[2],
         linewidth=3,
         color=colors[0])
axes[2, 1].grid()
axes[2, 1].set_xlabel("Year / Month", fontsize=12, fontweight="bold", color="#8C1C13")
axes[2, 1].set_ylabel("Sales", fontsize=12, fontweight="bold", color="#8C1C13")

plt.show()