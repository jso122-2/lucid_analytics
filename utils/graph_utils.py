import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from lifelines import KaplanMeierFitter
import plotly.graph_objs as go
import plotly.offline as pyo
import json
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pickle
import io
import base64
import datetime # added to generate a variable seed if needed

def _generate_default_plot(message):
    plt.figure(figsize=(8, 6))
    plt.text(0.5, 0.5, message, horizontalalignment='center',
             verticalalignment='center', fontsize=14)
    plt.axis('off')
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', bbox_inches='tight', facecolor='white')
    img_stream.seek(0)
    default_img = base64.b64encode(img_stream.getvalue()).decode('utf-8')
    plt.close()
    img_stream.close()
    return default_img

def generate_heatmap(input_data):
    if len(input_data) < 2:
        return _generate_default_plot("Not enough data for heatmap")
    if input_data.isnull().any().any():
        input_data = input_data.fillna(0)
    if input_data.var().sum() == 0:
        return _generate_default_plot("Zero variance in data for heatmap")
    correlation_matrix = input_data.corr().fillna(0)
    correlation_percent = correlation_matrix.astype(float) * 100
    plt.figure(figsize=(8, 6))
    ax = sns.heatmap(correlation_percent, annot=True, cmap='coolwarm')
    plt.title("Feature Correlation Heatmap")
    for t in ax.texts:
        try:
            val = float(t.get_text())
            t.set_text(f"{int(round(val))}%")
        except Exception as e:
            pass
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', bbox_inches='tight')
    img_stream.seek(0)
    heatmap_img = base64.b64encode(img_stream.getvalue()).decode('utf-8')
    plt.close()
    img_stream.close()
    return heatmap_img

def generate_density_plot(data, column, highlight_value=None):
    if data.shape[0] < 2 or data[column].nunique() < 2:
        return _generate_default_plot(f"Not enough data for density plot of {column}")
    sns.set_style("whitegrid")
    sns.set_palette("bright")
    plt.figure(figsize=(8, 6), facecolor='white')
    ax = sns.histplot(
        data[column], kde=True, color='skyblue', stat='density',
        bins=20, edgecolor='black'
    )
    plt.title(f"Density Plot of {column}", color='black')
    plt.xlabel(column, color='black')
    plt.ylabel("Density", color='black')
    if highlight_value is not None:
        plt.axvline(highlight_value, color='red', linestyle='--', linewidth=2, label='User Input')
        plt.legend()
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', bbox_inches='tight', facecolor='white')
    img_stream.seek(0)
    density_img = base64.b64encode(img_stream.getvalue()).decode('utf-8')
    plt.close()
    img_stream.close()
    return density_img

def generate_bubble_chart(data, x_col, y_col, size_col, hue_col=None, highlight_point=None):
    sns.set_style("whitegrid")
    sns.set_palette("bright")
    plt.figure(figsize=(10, 8), facecolor='white')
    ax = sns.scatterplot(
        data=data,
        x=x_col, y=y_col, size=size_col,
        hue=hue_col,
        sizes=(20, 200),
        alpha=0.7,
        edgecolor='black'
    )
    plt.title(f"Bubble Chart: {x_col} vs {y_col}", color='black')
    plt.xlabel(x_col, color='black')
    plt.ylabel(y_col, color='black')
    if highlight_point:
        plt.scatter(
            highlight_point['x'],
            highlight_point['y'],
            color='red', s=250, marker='X', label='User Input'
        )
        plt.legend()
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', bbox_inches='tight', facecolor='white')
    img_stream.seek(0)
    bubble_img = base64.b64encode(img_stream.getvalue()).decode('utf-8')
    plt.close()
    img_stream.close()
    return bubble_img

def generate_predicted_nps_bubble_chart_image(dynamic_input, prediction):
    # Parse baseline
    spend = float(dynamic_input.get("spend", 1000))
    revenue = float(dynamic_input.get("revenue", 3000))
    predicted_spend = float(prediction.get("predicted_spend", spend * 1.2))
    predicted_revenue = float(prediction.get("predicted_revenue", revenue * 1.2))

    n_samples = 100
    noise_multiplier = 0.5
    df = pd.DataFrame({
        "Spend": np.random.normal(spend, noise_multiplier * spend, n_samples),
        "Revenue": np.random.normal(revenue, noise_multiplier * revenue, n_samples)
    }).clip(lower=0)

    # Linear regression for trend line
    slope, intercept = np.polyfit(df["Spend"], df["Revenue"], 1)
    trend_x = np.linspace(df["Spend"].min(), df["Spend"].max(), 100)
    trend_y = slope * trend_x + intercept

    sns.set_style("dark")
    fig, ax = plt.subplots(figsize=(12, 9), facecolor='#1C1C1C')
    ax.set_facecolor('#1C1C1C')

    ax.scatter(df["Spend"], df["Revenue"], alpha=0.6, color="#008080", label="Synthetic Data")
    ax.plot(trend_x, trend_y, color="orange", linestyle="--", linewidth=2, label="Trend Line")
    ax.scatter(predicted_spend, predicted_revenue, color="magenta", s=250, marker='X', label="Predicted Campaign")
    ax.annotate(
        f"Predicted\n({predicted_spend:.1f}, {predicted_revenue:.1f})",
        xy=(predicted_spend, predicted_revenue),
        xytext=(predicted_spend * 1.05, predicted_revenue * 1.05),
        arrowprops=dict(facecolor='magenta', shrink=0.05),
        fontsize=12, color='magenta', fontweight='bold'
    )

    ax.set_xlabel("Spend", color='#E0E0E0', fontsize=12)
    ax.set_ylabel("Revenue", color='#E0E0E0', fontsize=12)
    ax.set_title("Enhanced Predicted NPS Bubble Chart", color='#E0E0E0', fontsize=14)
    ax.tick_params(colors='#E0E0E0')

    legend = ax.legend()
    for text in legend.get_texts():
        text.set_color("#E0E0E0")

    x_min, x_max = df["Spend"].min(), df["Spend"].max()
    y_min, y_max = df["Revenue"].min(), df["Revenue"].max()
    ax.set_xlim(x_min * 0.9, x_max * 1.1)
    ax.set_ylim(y_min * 0.9, y_max * 1.1)

    plt.tight_layout()
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png', bbox_inches='tight', facecolor='#1C1C1C', dpi=80)
    img_stream.seek(0)
    plt.close(fig)
    return img_stream

def generate_predicted_nps_density_plot_image(dynamic_input, prediction):
    import io
    import matplotlib.pyplot as plt
    import seaborn as sns
    import numpy as np
    import pandas as pd

    spend = float(dynamic_input.get("spend", 1000))
    predicted_spend = float(prediction.get("predicted_spend", spend * 1.2))

    n_samples = 100
    noise_multiplier = 0.5
    values = np.random.normal(spend, noise_multiplier * spend, n_samples)
    values = np.clip(values, 0, None)
    df = pd.DataFrame({"Spend": values})

    mean_val = df["Spend"].mean()
    median_val = df["Spend"].median()

    sns.set_style("dark")
    fig, ax = plt.subplots(figsize=(12, 9), facecolor='#1C1C1C')
    ax.set_facecolor('#1C1C1C')

    sns.histplot(
        df["Spend"], kde=True, color='#008080', edgecolor='white',
        bins=20, stat="density", alpha=0.6, ax=ax
    )

    ax.set_xlabel("Spend", color='#E0E0E0', fontsize=12)
    ax.set_ylabel("Density", color='#E0E0E0', fontsize=12)
    ax.set_title("Enhanced Predicted NPS Density Plot", color='#E0E0E0', fontsize=14)
    ax.tick_params(colors='#E0E0E0')

    ax.axvline(predicted_spend, color='magenta', linestyle='--', linewidth=2, label="Predicted Spend")
    ax.annotate(
        f"Predicted: {predicted_spend:.1f}",
        xy=(predicted_spend, ax.get_ylim()[1]*0.9),
        xytext=(predicted_spend, ax.get_ylim()[1]*0.95),
        arrowprops=dict(facecolor='magenta', arrowstyle='->'),
        fontsize=12, color='magenta', fontweight='bold'
    )

    ax.axvline(mean_val, color='orange', linestyle=':', linewidth=2, label="Mean")
    ax.axvline(median_val, color='white', linestyle='-.', linewidth=2, label="Median")
    ax.text(mean_val, ax.get_ylim()[1]*0.8, f"Mean: {mean_val:.1f}", color='orange', fontsize=12)
    ax.text(median_val, ax.get_ylim()[1]*0.7, f"Median: {median_val:.1f}", color='white', fontsize=12)

    legend = ax.legend()
    for text in legend.get_texts():
        text.set_color("#E0E0E0")

    x_min, x_max = df["Spend"].min(), df["Spend"].max()
    ax.set_xlim(x_min * 0.9, x_max * 1.1)

    plt.tight_layout()
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png', bbox_inches='tight', facecolor='#1C1C1C', dpi=80)
    img_stream.seek(0)
    plt.close(fig)
    return img_stream

def generate_dynamic_churn_funnel_chart(dynamic_input):
    n_samples = 100
    try:
        customer_tenure = float(dynamic_input.get("Customer_Tenure", 50))
        last_engagement_days = float(dynamic_input.get("Last_Engagement_Days", 30))
        total_interactions = float(dynamic_input.get("Total_Interactions", 500))
    except Exception as e:
        return _generate_default_plot("Invalid input data")
    noise_multiplier = 0.5
    synthetic_data = {
        "Customer_Tenure": np.random.normal(customer_tenure, noise_multiplier * customer_tenure, n_samples),
        "Last_Engagement_Days": np.random.normal(last_engagement_days, noise_multiplier * last_engagement_days, n_samples),
        "Total_Interactions": np.random.normal(total_interactions, noise_multiplier * total_interactions, n_samples)
    }
    df_dynamic = pd.DataFrame(synthetic_data)
    df_dynamic["Engagement_Score"] = 0.5
    df_dynamic["Review_Count"] = 10
    df_dynamic["Payment_Stability"] = 1.0
    df_dynamic["Subscription_Loyalty"] = 1.0
    df_dynamic["Engagement_Score_Change"] = df_dynamic["Engagement_Score"] / (df_dynamic["Last_Engagement_Days"] + 1)
    df_dynamic["Social_Media_Engagement"] = df_dynamic["Total_Interactions"]
    feature_order = [
        "Engagement_Score_Change",
        "Payment_Stability",
        "Subscription_Loyalty",
        "Customer_Tenure",
        "Last_Engagement_Days",
        "Review_Count",
        "Social_Media_Engagement"
    ]
    df_features = df_dynamic[feature_order]
    try:
        from utils.tasks import get_churn_artifacts
        churn_model, churn_scaler = get_churn_artifacts()
    except Exception as e:
        return _generate_default_plot("Error loading churn model")
    X = churn_scaler.transform(df_features)
    probs = churn_model.predict_proba(X)
    churn_probs = probs[:, 1]
    active_percentage = 100 - (churn_probs * 100)
    total_customers = n_samples
    median_active = np.median(active_percentage)
    at_risk_customers = int(np.sum(active_percentage < median_active))
    churned_customers = int(np.sum(active_percentage < 50))
    stages = ["Total Customers", "At Risk Customers", "Churned Customers"]
    values = [total_customers, at_risk_customers, churned_customers]
    plt.figure(figsize=(8, 6), facecolor='none')
    ax = sns.barplot(x=values, y=stages, palette="viridis", orient="h")
    plt.xlabel("Count")
    plt.title("Dynamic Churn Funnel Chart")
    for i, v in enumerate(values):
        ax.text(v + max(values)*0.01, i, f"{v}", color='white', va='center')
        if i > 0:
            prev = values[i-1]
            drop = ((prev - v) / prev * 100) if prev != 0 else 0
            ax.text(v + max(values)*0.05, i, f"(-{drop:.0f}%)", color='red', va='center')
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', bbox_inches='tight', transparent=True)
    img_stream.seek(0)
    funnel_img = base64.b64encode(img_stream.getvalue()).decode('utf-8')
    plt.close()
    img_stream.close()
    return funnel_img

def generate_churn_funnel_chart_from_prediction(predicted_percentage):
    total = 100
    churned = float(predicted_percentage)
    active = total - churned
    stages = ["Total Customers", "Active Customers", "Churned Customers"]
    values = [total, active, churned]
    plt.figure(figsize=(8, 6), facecolor='none')
    ax = sns.barplot(x=values, y=stages, palette="viridis", orient="h")
    plt.xlabel("Count")
    plt.title("Churn Funnel Chart")
    for i, v in enumerate(values):
        ax.text(v + total * 0.01, i, f"{v:.0f}", color='white', va='center')
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', bbox_inches='tight', transparent=True)
    img_stream.seek(0)
    funnel_img = base64.b64encode(img_stream.getvalue()).decode('utf-8')
    plt.close()
    img_stream.close()
    return funnel_img

from utils.logger_config import logger  # import our logger

def generate_km_survival_curve_image(derived_data=None, input_data=None):
    """
    Generates a Kaplan–Meier survival curve as a PNG image.
    """
    import io
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from config import CHURN_COX_MODEL_PATH, CHURN_SURVIVAL_SCALER_PATH, INFERENCE_FEATURES_SURVIVAL_PATH
    import pickle
    import joblib

    # Build the DataFrame from derived_data or input_data
    if derived_data is not None:
        df = pd.DataFrame(derived_data) if not isinstance(derived_data, pd.DataFrame) else derived_data
        if 'T' not in df.columns or ('E' not in df.columns and 'Survival' not in df.columns):
            raise ValueError("Provided derived data must have 'T' and either 'E' or 'Survival'.")
    elif input_data is not None:
        with open(CHURN_COX_MODEL_PATH, "rb") as f:
            survival_model = pickle.load(f)
        survival_scaler = joblib.load(CHURN_SURVIVAL_SCALER_PATH)
        pruned_features = [
            "Engagement_Score_Change",
            "Payment_Stability",
            "Subscription_Loyalty",
            "Customer_Tenure",
            "Last_Engagement_Days",
            "Review_Count",
            "Social_Media_Engagement"
        ]
        df_input = pd.DataFrame({feat: input_data.get(feat, 0) for feat in pruned_features}, index=[0])
        df_input_scaled = pd.DataFrame(survival_scaler.transform(df_input), columns=pruned_features)
        survival_function = survival_model.predict_survival_function(df_input_scaled)
        df = pd.DataFrame({
            "T": survival_function.index,
            "Survival": survival_function.iloc[:, 0]
        })
    else:
        raise ValueError("No survival data provided and no input data for model inference.")

    # Debug prints to check ranges
    t_min, t_max = df["T"].min(), df["T"].max()
    if "Survival" in df.columns:
        surv_min, surv_max = df["Survival"].min(), df["Survival"].max()
    else:
        surv_min, surv_max = 0, 1  # For observed data

    print("Time (T) range:", t_min, "to", t_max)
    print("Survival range:", surv_min, "to", surv_max)

    # Set up the main plot with updated styling.
    sns.set_style("dark")
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#1C1C1C')
    ax.set_facecolor('#1C1C1C')

    # Plot the survival curve
    if 'E' in df.columns:
        from lifelines import KaplanMeierFitter
        kmf = KaplanMeierFitter()
        kmf.fit(df['T'], event_observed=df['E'])
        ax.step(kmf.survival_function_.index,
                kmf.survival_function_['KM_estimate'],
                where='post',
                color='#4A90E2',
                label='Observed Survival')
    elif 'Survival' in df.columns:
        ax.plot(df['T'], df['Survival'], color='#4A90E2', label='Predicted Survival')

    # Set axis labels, title, and tick colors
    ax.set_xlabel("Time (Days)", fontsize=12, color='#E0E0E0')
    ax.set_ylabel("Survival Probability", fontsize=12, color='#E0E0E0')
    ax.set_title("Time-to-Churn Survival Curve", fontsize=14, color='#E0E0E0')
    ax.tick_params(colors='#E0E0E0')

    # Optionally add vertical reference lines
    if t_max >= 30:
        ax.axvline(30, color='orange', linestyle='--', linewidth=2, label='30 Days')
    if t_max >= 60:
        ax.axvline(60, color='magenta', linestyle='--', linewidth=2, label='60 Days')

    # Create legend with white text.
    leg = ax.legend(facecolor='#1C1C1C', edgecolor='white')
    for text in leg.get_texts():
        text.set_color("white")
    
    ax.grid(True)

    # Save figure to buffer with the specified dark background
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png', bbox_inches='tight', facecolor='#1C1C1C', dpi=100)
    img_stream.seek(0)
    plt.close(fig)

    print("Generated PNG size (bytes):", len(img_stream.getvalue()))
    return img_stream


def generate_spend_vs_roi_curve_image(dynamic_input, prediction):
    """
    Generates a Spend vs. ROI curve using a logistic function:
      ROI(spend) = L / (1 + exp(-k*(spend - optimal_spend)))
    where L is the maximum ROI, optimal_spend is the spend at which ROI peaks,
    and k controls steepness.
    
    Uses model-predicted values if provided; otherwise, defaults.
    Returns a BytesIO stream containing the PNG image.
    """
    import io
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from scipy.optimize import fsolve

    ad_spend = float(dynamic_input.get("ad_spend", 1000))
    optimal_spend = float(prediction.get("optimal_spend", float(dynamic_input.get("ad_spend", 1000)) * 0.5))
    L = float(prediction.get("max_roi", 3.0))
    k = float(prediction.get("k", 0.005))
    
    optimal_spend = np.clip(optimal_spend, 0, 10000)
    L = np.clip(L, 1, 10)
    k = np.clip(k, 0.001, 0.02)
    
    roi_function = lambda spend: L / (1 + np.exp(-k * (spend - optimal_spend)))
    
    x_max = max(1200, ad_spend * 1.2, optimal_spend * 1.2)
    spend_vals = np.linspace(0, x_max, 300)
    roi_vals = roi_function(spend_vals)
    
    def break_even_eq(x):
        return roi_function(x) - 1.0
    try:
        break_even, = fsolve(break_even_eq, optimal_spend)
    except Exception:
        break_even = optimal_spend

    fixed_ymax = max(5, L * 1.1)
    
    sns.set_style("dark")
    fig, ax = plt.subplots(figsize=(12, 9), facecolor='#1C1C1C')
    ax.set_facecolor('#1C1C1C')
    
    ax.plot(spend_vals, roi_vals, color="#008080", linewidth=2, label="ROI Curve")
    ax.axvline(optimal_spend, color="#4A90E2", linestyle="--", linewidth=2, label="Optimal Spend")
    ax.annotate(f"Optimal Spend: {optimal_spend:.0f}",
                xy=(optimal_spend, roi_function(optimal_spend)),
                xytext=(optimal_spend + 50, roi_function(optimal_spend) - 0.3),
                arrowprops=dict(facecolor="#4A90E2", shrink=0.05),
                fontsize=12, color="#E0E0E0")
    ax.axvline(break_even, color="red", linestyle=":", linewidth=2, label="Break-even")
    ax.text(break_even, 1.05, f"{break_even:.0f}", color="#E0E0E0", fontsize=12, ha="right")
    
    ax.set_xlabel("Ad Spend", color="#E0E0E0", fontsize=14)
    ax.set_ylabel("ROI", color="#E0E0E0", fontsize=14)
    ax.set_title("Spend vs. ROI Curve", color="#E0E0E0", fontsize=16)
    ax.tick_params(colors="#E0E0E0")
    
    legend = ax.legend(facecolor="#1C1C1C", edgecolor="#1C1C1C", fontsize=12)
    for text in legend.get_texts():
        text.set_color("#E0E0E0")
    
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, fixed_ymax)
    
    plt.tight_layout()
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png', bbox_inches='tight', facecolor='#1C1C1C', dpi=80)
    img_stream.seek(0)
    plt.close(fig)
    return img_stream

def generate_impressions_vs_engagement_bubble_chart_image(dynamic_input, prediction):
    """
    Generates an Impressions vs. Engagement bubble chart as a PNG image and returns a BytesIO stream.
    """
    try:
        impressions_baseline = float(dynamic_input.get("impressions", 5000))
    except:
        impressions_baseline = 5000.0
    try:
        engagement_baseline = float(dynamic_input.get("engagement", 300))
    except:
        engagement_baseline = 300.0
    try:
        interactions_baseline = float(dynamic_input.get("interactions", 150))
    except:
        interactions_baseline = 150.0

    predicted_impressions = float(prediction.get("predicted_impressions", impressions_baseline))
    predicted_engagement = float(prediction.get("predicted_engagement", engagement_baseline))
    predicted_interactions = float(prediction.get("predicted_interactions", interactions_baseline))

    n_samples = 100
    np.random.seed(42)
    impressions = np.random.normal(impressions_baseline, 0.2 * impressions_baseline, n_samples)
    engagement = np.random.normal(engagement_baseline, 0.2 * engagement_baseline, n_samples)
    interactions = np.random.normal(interactions_baseline, 0.3 * interactions_baseline, n_samples)

    impressions = np.clip(impressions, 0, None)
    engagement = np.clip(engagement, 0, None)
    interactions = np.clip(interactions, 0, None)

    df = pd.DataFrame({
        "Impressions": impressions,
        "Engagement": engagement,
        "Interactions": interactions
    })

    slope, intercept = np.polyfit(df["Impressions"], df["Engagement"], 1)
    trend_x = np.linspace(df["Impressions"].min(), df["Impressions"].max(), 100)
    trend_y = slope * trend_x + intercept

    sns.set_style("dark")
    fig, ax = plt.subplots(figsize=(12, 9), facecolor='#1C1C1C')
    ax.set_facecolor('#1C1C1C')

    scatter = ax.scatter(df["Impressions"], df["Engagement"],
                         s=df["Interactions"]*3, alpha=0.6, color="#008080", label="Campaigns")
    
    ax.plot(trend_x, trend_y, color="#4A90E2", linestyle="--", linewidth=2, label="Trend Line")
    ax.scatter(predicted_impressions, predicted_engagement, color="magenta",
               s=predicted_interactions*3, marker='X', label="Predicted Campaign")
    ax.annotate(f"Predicted\n({predicted_impressions:.0f}, {predicted_engagement:.0f})",
                xy=(predicted_impressions, predicted_engagement),
                xytext=(predicted_impressions*1.05, predicted_engagement*1.05),
                arrowprops=dict(facecolor="magenta", shrink=0.05),
                fontsize=12, color="magenta", fontweight="bold")
    
    ax.set_xlabel("Impressions", color="#E0E0E0", fontsize=14)
    ax.set_ylabel("Engagement", color="#E0E0E0", fontsize=14)
    ax.set_title("Impressions vs. Engagement Bubble Chart", color="#E0E0E0", fontsize=16)
    ax.tick_params(colors="#E0E0E0")
    
    legend = ax.legend(facecolor="#1C1C1C", edgecolor="#1C1C1C", fontsize=12)
    for text in legend.get_texts():
        text.set_color("#E0E0E0")
    
    ax.set_xlim(df["Impressions"].min()*0.9, df["Impressions"].max()*1.1)
    ax.set_ylim(df["Engagement"].min()*0.9, df["Engagement"].max()*1.1)
    
    plt.tight_layout()
    img_stream = io.BytesIO()
    fig.savefig(img_stream, format='png', bbox_inches='tight', facecolor='#1C1C1C', dpi=80)
    img_stream.seek(0)
    plt.close(fig)
    return img_stream

def generate_churn_funnel_chart_from_prediction(predicted_percentage):
    total = 100
    churned = float(predicted_percentage)
    active = total - churned
    stages = ["Total Customers", "Active Customers", "Churned Customers"]
    values = [total, active, churned]
    plt.figure(figsize=(8, 6), facecolor='none')
    ax = sns.barplot(x=values, y=stages, palette="viridis", orient="h")
    plt.xlabel("Count")
    plt.title("Churn Funnel Chart")
    for i, v in enumerate(values):
        ax.text(v + total * 0.01, i, f"{v:.0f}", color='white', va='center')
    img_stream = io.BytesIO()
    plt.savefig(img_stream, format='png', bbox_inches='tight', transparent=True)
    img_stream.seek(0)
    funnel_img = base64.b64encode(img_stream.getvalue()).decode('utf-8')
    plt.close()
    img_stream.close()
    return funnel_img
