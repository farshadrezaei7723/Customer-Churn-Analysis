import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


print("Python version:", sys.version)


# 1. Set file paths and create the output folder if needed.
file_path = Path(__file__).parent / "Data" / "Telco-Customer-Churn.csv"
output_dir = Path(__file__).parent / "outputs"
output_dir.mkdir(exist_ok=True)


# 2. Load the dataset and inspect its size, columns, and data types.
df = pd.read_csv(file_path)

print(df.head())
print("Rows and columns:", df.shape)
df.info()


# 3. Convert TotalCharges to numbers.
# Keep missing or non-numeric values as NaN without removing customers.
total_charge_numeric = pd.to_numeric(df["TotalCharges"], errors="coerce")
invalid_charges = total_charge_numeric.isna()

df["TotalCharges"] = total_charge_numeric

# Inspect affected customers and their tenure.
print(df.loc[
    invalid_charges,
    ["customerID", "tenure", "TotalCharges"]
])


# 4. Check for repeated customer IDs before counting customers.
duplicated_customers = df["customerID"].duplicated().sum()
print("Duplicate customer IDs:", duplicated_customers)


# 5. Calculate overall churn: customers who left divided by all customers.
# Customer IDs are unique, so each row represents one customer.
churn_count = df["Churn"].value_counts(dropna=False)

churned_customers = churn_count["Yes"]
total_customers = len(df)

churn_rate = (churned_customers / total_customers) * 100
print(f"Churn rate: {churn_rate:.2f}%")


# 6. Count customers by contract type and churn status.
contract_count = df["Contract"].value_counts(dropna=False)
contract_churn_counts = pd.crosstab(df["Contract"], df["Churn"])

# Calculate churn within each contract group because group sizes differ.
contract_total = contract_churn_counts.sum(axis=1)
contract_churn_rate = (
    contract_churn_counts["Yes"] / contract_total
) * 100

# Plot and save churn rates by contract type.
plt.figure()
contract_churn_rate.plot(kind="bar", color="blue")
plt.title("Customer Churn Rate by Contract")
plt.xlabel("Contract Type")
plt.ylabel("Churn Rate (%)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(output_dir / "churn_by_contract.png", dpi=300)
plt.show()


# 7. Calculate average tenure for customers who stayed and those who left.
tenure_by_churn = df.groupby("Churn")["tenure"].mean()


# 8. Group tenure into month ranges while keeping the original column.
# Include zero-month customers in the first group.
df["tenure_group"] = pd.cut(
    df["tenure"],
    bins=[0, 12, 24, 48, float("inf")],
    labels=[
        "0–12 months",
        "13–24 months",
        "25–48 months",
        "49+ months"
    ],
    include_lowest=True
)

# Calculate churn as a percentage of customers in each tenure group.
tenure_churn_counts = pd.crosstab(df["tenure_group"], df["Churn"])
print(tenure_churn_counts)

tenure_total = tenure_churn_counts.sum(axis=1)
tenure_churn_rate = (
    tenure_churn_counts["Yes"] / tenure_total
) * 100

print(tenure_churn_rate.round(2))

# Plot and save churn rates by tenure group.
plt.figure()
tenure_churn_rate.plot(kind="bar", color="steelblue")
plt.title("Customer Churn Rate by Tenure")
plt.xlabel("Tenure Group")
plt.ylabel("Churn Rate (%)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(output_dir / "churn_by_tenure.png", dpi=300)
plt.show()


# 9. Compare average monthly charges between churn groups.
monthly_charges_by_churn = (
    df.groupby("Churn")["MonthlyCharges"].mean()
)
print("Average monthly charges by churn:", monthly_charges_by_churn)

# Plot and save the comparison.
plt.figure()
monthly_charges_by_churn.plot(kind="bar", color="blue")
plt.title("Average Monthly Charges by Churn")
plt.xlabel("Churn Status")
plt.ylabel("Average Monthly Charges ($)")
plt.xticks(rotation=0)
plt.tight_layout()
plt.savefig(output_dir / "monthly_charges_by_churn.png", dpi=300)


# 10. Export the prepared data without adding a row-index column.
# Missing TotalCharges values remain blank in the CSV.
df.to_csv(
    output_dir / "customer_churn_cleaned.csv",
    index=False
)

print("Cleaned data saved successfully.")

plt.show()