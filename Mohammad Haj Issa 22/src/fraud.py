import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tensorflow as tf

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (classification_report, confusion_matrix,
                             roc_auc_score, average_precision_score,
                             roc_curve, accuracy_score)

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv1D, MaxPooling1D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping

from imblearn.over_sampling import SMOTE



train_data = pd.read_csv("./data/fraudTrain.csv")
test_data = pd.read_csv("./data/fraudTest.csv")
df = pd.concat([train_data, test_data], ignore_index=True)



def clean_data(data):
    data['trans_date_trans_time'] = pd.to_datetime(data['trans_date_trans_time'])
    data['hour'] = data['trans_date_trans_time'].dt.hour
    data['day'] = data['trans_date_trans_time'].dt.day
    data['month'] = data['trans_date_trans_time'].dt.month
    data['dayofweek'] = data['trans_date_trans_time'].dt.dayofweek

    data = pd.get_dummies(data, columns=['category', 'gender'])

    drop_cols = ['trans_date_trans_time', 'merchant', 'first', 'last', 'street',
                 'city', 'state', 'job', 'dob', 'trans_num', 'unix_time']
    data.drop(columns=drop_cols, inplace=True)

    return data


df_processed = clean_data(df)

X = df_processed.drop('is_fraud', axis=1)
y = df_processed['is_fraud']


X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)


scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)


sm = SMOTE(random_state=42)
X_train_res, y_train_res = sm.fit_resample(X_train_scaled, y_train)


X_train_cnn = X_train_res.reshape(X_train_res.shape[0], X_train_res.shape[1], 1)
X_test_cnn = X_test_scaled.reshape(X_test_scaled.shape[0], X_test_scaled.shape[1], 1)

model = Sequential()
model.add(Conv1D(32, 3, activation='relu', input_shape=(X_train_cnn.shape[1], 1)))
model.add(MaxPooling1D(2))
model.add(Conv1D(64, 3, activation='relu'))
model.add(MaxPooling1D(2))
model.add(Conv1D(64, 3, activation='relu'))
model.add(Flatten())
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(32, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(1, activation='sigmoid'))

model.compile(optimizer=Adam(learning_rate=0.0001),
              loss='binary_crossentropy', metrics=['accuracy'])

stopper = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)


history = model.fit(X_train_cnn, y_train_res,
                    epochs=10,
                    batch_size=32,
                    validation_split=0.2,
                    callbacks=[stopper],
                    verbose=1)

y_train_pred = (model.predict(X_train_cnn) > 0.5).astype(int)
y_test_pred = (model.predict(X_test_cnn) > 0.5).astype(int)
y_pred_proba = model.predict(X_test_cnn)

train_acc = accuracy_score(y_train_res, y_train_pred)
test_acc = accuracy_score(y_test, y_test_pred)

print(f"Training Accuracy: {train_acc:.4f}")
print(f"Testing Accuracy: {test_acc:.4f}\n")

print("Classification Report:")
print(classification_report(y_test, y_test_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_test_pred))

print(f"\nAUC-ROC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
print(f"Average Precision Score: {average_precision_score(y_test, y_pred_proba):.4f}")

plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Val Loss')
plt.title('Loss over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(history.history['accuracy'], label='Train Acc')
plt.plot(history.history['val_accuracy'], label='Val Acc')
plt.title('Accuracy over Epochs')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend()
plt.tight_layout()
plt.show()

fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, label=f'ROC (AUC = {roc_auc_score(y_test, y_pred_proba):.4f})')
plt.plot([0, 1], [0, 1], linestyle='--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend()
plt.show()


def get_gradients(model, inputs, targets):
    inputs_tensor = tf.convert_to_tensor(inputs, dtype=tf.float32)
    targets_tensor = tf.convert_to_tensor(targets, dtype=tf.float32)

    with tf.GradientTape() as tape:
        tape.watch(inputs_tensor)
        preds = model(inputs_tensor)
        loss = tf.keras.losses.binary_crossentropy(targets_tensor, preds)

    return tape.gradient(loss, inputs_tensor)

n_samples = min(1000, X_test_cnn.shape[0])
idx = np.random.choice(X_test_cnn.shape[0], n_samples, replace=False)
sample_inputs = X_test_cnn[idx]
sample_targets = y_test.iloc[idx].values.reshape(-1, 1)

grads = get_gradients(model, sample_inputs, sample_targets)
importance_scores = np.mean(np.abs(grads.numpy()), axis=0).squeeze()

importance_df = pd.DataFrame({
    'feature': X.columns,
    'importance': importance_scores
}).sort_values('importance', ascending=False)

plt.figure(figsize=(10, 6))
sns.barplot(x='importance', y='feature', data=importance_df.head(15))
plt.title('Top 15 Important Features (CNN)')
plt.tight_layout()
plt.show()

print("Top 15 Most Important Features:")
print(importance_df.head(15).to_string(index=False))
