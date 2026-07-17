import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pickle
import os

# Create sample dataset for training
def create_sample_dataset():
    """
    Generate synthetic student data for placement prediction
    Features: cgpa, skills_count, internships, projects, certifications
    Target: placed (1 = placed, 0 = not placed)
    """
    np.random.seed(42)
    n_samples = 500
    
    data = {
        'cgpa': np.random.uniform(6.0, 10.0, n_samples).round(2),
        'skills_count': np.random.randint(2, 15, n_samples),
        'internships': np.random.randint(0, 5, n_samples),
        'projects': np.random.randint(0, 12, n_samples),
        'certifications': np.random.randint(0, 8, n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Create placement target based on realistic criteria
    # Higher CGPA, more skills, internships, projects increase placement probability
    placement_score = (
        (df['cgpa'] - 6) * 15 +  # CGPA contribution (0-60)
        df['skills_count'] * 2 +  # Skills contribution
        df['internships'] * 8 +    # Internships contribution
        df['projects'] * 3 +       # Projects contribution
        df['certifications'] * 4   # Certifications contribution
    )
    
    # Add some randomness to make it realistic
    noise = np.random.normal(0, 10, n_samples)
    placement_score = placement_score + noise
    
    # Convert to binary (threshold around 70)
    df['placed'] = (placement_score > 70).astype(int)
    
    return df

def train_placement_model():
    """
    Train Logistic Regression model for placement prediction
    """
    print("=" * 60)
    print("Student Placement Prediction Model Training")
    print("=" * 60)
    
    # Create dataset
    print("\n1. Creating sample dataset...")
    df = create_sample_dataset()
    print(f"   Dataset created with {len(df)} samples")
    print(f"   Placement rate: {df['placed'].mean()*100:.2f}%")
    
    # Display sample data
    print("\n2. Sample data:")
    print(df.head(10))
    
    # Display statistics
    print("\n3. Dataset statistics:")
    print(df.describe())
    
    print("\n4. Placement distribution:")
    print(df['placed'].value_counts())
    
    # Prepare features and target
    X = df[['cgpa', 'skills_count', 'internships', 'projects', 'certifications']]
    y = df['placed']
    
    # Split data
    print("\n5. Splitting data (80% train, 20% test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"   Training samples: {len(X_train)}")
    print(f"   Testing samples: {len(X_test)}")
    
    # Feature scaling
    print("\n6. Scaling features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model
    print("\n7. Training Logistic Regression model...")
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X_train_scaled, y_train)
    print("   Model training completed!")
    
    # Evaluate model
    print("\n8. Model evaluation:")
    y_pred = model.predict(X_test_scaled)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"   Accuracy: {accuracy*100:.2f}%")
    
    print("\n   Classification Report:")
    print(classification_report(y_test, y_pred, target_names=['Not Placed', 'Placed']))
    
    print("\n   Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(f"   True Negatives: {cm[0][0]}, False Positives: {cm[0][1]}")
    print(f"   False Negatives: {cm[1][0]}, True Positives: {cm[1][1]}")
    
    # Feature importance
    print("\n9. Feature importance (coefficients):")
    feature_names = ['CGPA', 'Skills Count', 'Internships', 'Projects', 'Certifications']
    for name, coef in zip(feature_names, model.coef_[0]):
        print(f"   {name}: {coef:.4f}")
    
    # Save model and scaler
    print("\n10. Saving model and scaler...")
    models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, 'placement_model.pkl')
    scaler_path = os.path.join(models_dir, 'scaler.pkl')
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"   Model saved to: {model_path}")
    
    with open(scaler_path, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"   Scaler saved to: {scaler_path}")
    
    # Test predictions with sample students
    print("\n11. Testing predictions on sample students:")
    test_students = [
        {'cgpa': 9.2, 'skills_count': 10, 'internships': 3, 'projects': 7, 'certifications': 5},
        {'cgpa': 7.5, 'skills_count': 5, 'internships': 1, 'projects': 3, 'certifications': 2},
        {'cgpa': 8.8, 'skills_count': 8, 'internships': 2, 'projects': 6, 'certifications': 4},
        {'cgpa': 6.8, 'skills_count': 3, 'internships': 0, 'projects': 2, 'certifications': 1},
    ]
    
    for i, student in enumerate(test_students, 1):
        features = np.array([[
            student['cgpa'],
            student['skills_count'],
            student['internships'],
            student['projects'],
            student['certifications']
        ]])
        features_scaled = scaler.transform(features)
        probability = model.predict_proba(features_scaled)[0][1] * 100
        prediction = model.predict(features_scaled)[0]
        
        print(f"\n   Student {i}:")
        print(f"   - CGPA: {student['cgpa']}, Skills: {student['skills_count']}, "
              f"Internships: {student['internships']}, Projects: {student['projects']}, "
              f"Certifications: {student['certifications']}")
        print(f"   - Placement Probability: {probability:.2f}%")
        print(f"   - Prediction: {'PLACED' if prediction == 1 else 'NOT PLACED'}")
    
    print("\n" + "=" * 60)
    print("Training completed successfully!")
    print("=" * 60)
    
    return model, scaler, df

if __name__ == '__main__':
    model, scaler, dataset = train_placement_model()
    
    # Save dataset for reference
    dataset_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'training_data.csv')
    os.makedirs(os.path.dirname(dataset_path), exist_ok=True)
    dataset.to_csv(dataset_path, index=False)
    print(f"\nTraining dataset saved to: {dataset_path}")
