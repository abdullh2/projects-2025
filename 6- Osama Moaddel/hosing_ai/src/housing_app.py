import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

# ------------------------------------------
# تحميل البيانات وتدريب النموذج
# ------------------------------------------

@st.cache_data
def load_data_and_train():
    df = pd.read_csv("data/real_estate_dataset.csv")

    # الأعمدة   
    df = df[['Num_Bedrooms', 'Num_Bathrooms', 'Square_Feet', 'Num_Floors', 'Location_Score', 'Distance_to_Center', 'Has_Garden', 'Has_Pool', 'Garage_Size', 'Price']]
    
    # تنظيف البيانات
    df = df.dropna()
    df = df[(df['Price'] > 10000) & (df['Price'] < 5000000)]

    X = df.drop('Price', axis=1)
    y = df['Price']

    model = LinearRegression()
    model.fit(X, y)

    return model, df

model, df = load_data_and_train()

# ------------------------------------------
# واجهة المستخدم
# ------------------------------------------

st.title("🏡 تقدير سعر العقار")
st.write("أدخل تفاصيل العقار وسنقوم بتقدير سعره المتوقع:")

bedrooms = st.slider("عدد الغرف ", 0, 10, 3)
bathrooms = st.slider("عدد الحمامات", 0, 10, 2)
sqft = st.number_input("المساحة (متر مربع)", min_value=100, max_value=10000, value=1500)
floors = st.slider("عدد الطوابق", 1, 5, 1)
location_score = st.slider("تقييم الموقع (0-10)", 0.0, 10.0, 5.0)
distance = st.slider("المسافة عن مركز المدينة (كم)", 0.0, 50.0, 10.0)
garden = st.selectbox("هل يوجد حديقة؟", ["نعم", "لا"])
pool = st.selectbox("هل يوجد مسبح؟", ["نعم", "لا"])
garage = st.slider("حجم الكراج (عدد السيارات)", 0, 5, 1)

# ------------------------------------------
# عند الضغط على زر التنبؤ
# ------------------------------------------

if st.button("🔮 تقدير السعر"):
    input_df = pd.DataFrame({
        'Num_Bedrooms': [bedrooms],
        'Num_Bathrooms': [bathrooms],
        'Square_Feet': [sqft],
        'Num_Floors': [floors],
        'Location_Score': [location_score],
        'Distance_to_Center': [distance],
        'Has_Garden': [1 if garden == "نعم" else 0],
        'Has_Pool': [1 if pool == "نعم" else 0],
        'Garage_Size': [garage],
    })

    prediction = model.predict(input_df)[0]
    st.success(f"✅ السعر المتوقع: {prediction:,.0f} دولار")
