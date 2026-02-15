# train_model.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib

# 1. Load dataset
data = pd.read_csv("../dataset/security_data.csv")

# 2. Separate features (X) and label (y)
X = data.drop("risk_label", axis=1)
y = data["risk_label"]

# 3. Split dataset into training and testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 4. Create model
model = LogisticRegression()

# 5. Train model
model.fit(X_train, y_train)

# 6. Make predictions
y_pred = model.predict(X_test)

# 7. Check accuracy
accuracy = accuracy_score(y_test, y_pred)
print("Model Accuracy:", accuracy)

# 8. Save trained model
joblib.dump(model, "model.pkl")

print("Model saved successfully!")
