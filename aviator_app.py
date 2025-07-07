import streamlit as st
import pytesseract
from PIL import Image
import re
import matplotlib.pyplot as plt

# ✅ Your custom Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\mkhan\OneDrive\Desktop\ISE AFTER MIDS\tesseract.exe"

# ---------------------- UI Layout ----------------------
st.set_page_config(page_title="Aviator Predictor", layout="centered")
st.title("🎯 Smart Aviator Multiplier Predictor")
st.markdown("Upload your **screenshot** and let the app learn from the data to guide your decisions.")

uploaded_file = st.file_uploader("📸 Upload Screenshot", type=["jpg", "png", "jpeg"])

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Screenshot", use_column_width=True)
    image = Image.open(uploaded_file)

    # ---------------------- Step 1: OCR ----------------------
    with st.spinner("🔍 Reading numbers from image..."):
        text = pytesseract.image_to_string(image)
        numbers = re.findall(r"\d+\.\d+x", text)
        data = [float(n.replace("x", "")) for n in numbers]

    if data:
        st.success("✅ Data Extracted")
        st.write(f"📈 Total rounds: {len(data)}")
        st.write(data)

        # ---------------------- Step 2: Basic Analysis ----------------------
        st.markdown("### 🧮 Basic Stats")
        gt_2 = len([n for n in data if n > 2])
        gt_5 = len([n for n in data if n > 5])
        gt_7 = len([n for n in data if n > 7])

        st.write(f"🔹 Greater than 2x: `{gt_2}` ({gt_2/len(data)*100:.2f}%)")
        st.write(f"🔹 Greater than 5x: `{gt_5}` ({gt_5/len(data)*100:.2f}%)")
        st.write(f"🔹 Greater than 7x: `{gt_7}` ({gt_7/len(data)*100:.2f}%)")
        # ---------------------- Step 4: Predict Next Likely Multiplier Range ----------------------
        st.markdown("### 🎯 Prediction for Next Round")

        # Define ranges
        ranges = {
            "1x to 2x": (1.00, 2.00),
            "2x to 3x": (2.00, 3.00),
            "3x to 5x": (3.00, 5.00),
            "5x to 10x": (5.00, 10.00),
            "10x+": (10.00, float("inf"))
        }

        # Count frequency of each range
        range_counts = {label: 0 for label in ranges}
        for val in data:
            for label, (low, high) in ranges.items():
                if low <= val < high:
                    range_counts[label] += 1
                    break

        # Calculate percentage
        total = len(data)
        range_chances = {label: round((count / total) * 100, 2) for label, count in range_counts.items()}

        # Show chances
        for label, percent in range_chances.items():
            st.write(f"🔸 **{label}**: {percent}% of rounds")

        # Suggest most likely next category
        likely_range = max(range_chances.items(), key=lambda x: x[1])
        st.markdown(
            f"📢 Based on current data, most rounds end in **{likely_range[0]}**. Likely next value: **{likely_range[0]}**")
        # ---------------------- Step 5: Final Decision Suggestion ----------------------
        st.markdown("### 💡 Final Suggestion for This Round")

        recent = data[-5:] if len(data) >= 5 else data[-len(data):]
        low_streak = 0
        for val in reversed(recent):
            if val <= 2.0:
                low_streak += 1
            else:
                break

        # Rule-based suggestion logic (educational simulation only)
        if low_streak >= 3:
            st.success(
                "✅ Last 3+ rounds were low. Based on historical patterns, **high value may be next**. You may take the bet now.")
        elif recent[-1] > 7.0:
            st.warning(
                "⚠️ Last round was very high. Based on trends, next round may crash early. **Avoid betting now.**")
        elif low_streak == 2:
            st.info("⏳ There are 2 low rounds. High value might come, but not guaranteed. Wait and observe.")
        else:
            st.write("🤔 Not enough pattern to suggest a strong decision. Watch and collect more data.")


        # ---------------------- Step 3: Pattern Learning ----------------------
        st.markdown("### 🤖 Learned Pattern: After Low Multipliers")
        after_low_streaks = {}
        for streak_len in range(1, 6):
            hits, total_streaks = 0, 0
            i = 0
            while i < len(data) - streak_len - 1:
                if all(val <= 2.0 for val in data[i:i+streak_len]):
                    total_streaks += 1
                    if data[i + streak_len] > 2.0:
                        hits += 1
                    i += streak_len
                else:
                    i += 1
            if total_streaks > 0:
                after_low_streaks[streak_len] = round((hits / total_streaks) * 100, 2)

        for streak, chance in after_low_streaks.items():
            st.write(f"🔁 After `{streak}` low round(s): **{chance}%** chance of a >2x next")

        # ---------------------- Step 4: Smart Decision ----------------------
        st.markdown("### 📋 Smart Decision Suggestion")

        recent = data[-3:] if len(data) >= 3 else data[-len(data):]
        if all(x <= 2.0 for x in recent):
            st.info("📌 Recent rounds are low. Based on pattern, a **high value might come soon!**")
        elif data[-1] > 5.0:
            st.warning("⚠️ Last round was high. Might be followed by some low rounds.")
        else:
            st.write("🤔 No strong signal. Watch closely for streaks of low multipliers.")

        # ---------------------- Step 5: Chart ----------------------
        st.markdown("### 📊 Multiplier Chart")
        fig, ax = plt.subplots()
        ax.plot(data, marker='o', linewidth=2)
        ax.axhline(2.0, color='red', linestyle='--', label='2x')
        ax.axhline(5.0, color='purple', linestyle='--', label='5x')
        ax.axhline(7.0, color='green', linestyle='--', label='7x')
        ax.set_title("Multiplier History")
        ax.set_xlabel("Round")
        ax.set_ylabel("Multiplier")
        ax.legend()
        st.pyplot(fig)

    else:
        st.error("❌ No multipliers found. Please upload a clear screenshot with numbers like `2.64x`, `7.91x`, etc.")
