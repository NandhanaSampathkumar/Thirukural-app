import streamlit as st
import pandas as pd
import random
from deep_translator import GoogleTranslator


# ✅ App Configuration
st.set_page_config(page_title="📖 Thirukkural App", layout="wide")

# ✅ Load Dataset
df = pd.read_excel("thirukural.xlsx")
df["Kural No"] = pd.to_numeric(df["Kural No"], errors='coerce').astype(int)

# ✅ Initialize session state
if "score" not in st.session_state:
    st.session_state.score = {"correct": 0, "total": 0}
if "quiz" not in st.session_state:
    st.session_state.quiz = {"question": "", "options": [], "answer": ""}
if "summary" not in st.session_state:
    st.session_state.summary = []

# ✅ Sidebar Menu
st.sidebar.title("📚 Menu")
menu = st.sidebar.radio(
    "Select Option",
    ["🔢 Kural Lookup", "📘 Urai", "🌐 Translation", "🔍 Topic Search", "🎮 Quiz", "🤖 Chatbot"]
)

# ✅ Kural Lookup
if menu == "🔢 Kural Lookup":
    st.subheader("🔢 Kural Lookup")
    kural_number = st.number_input("Enter Kural Number", min_value=1, max_value=1330, step=1)
    if st.button("Search"):
        kural = df[df["Kural No"] == kural_number]
        if kural.empty:
            st.error("❌ Kural not found.")
        else:
            k = kural.iloc[0]
            lines = k["Tamil kural"].split()
            line1 = ' '.join(lines[:4])
            line2 = ' '.join(lines[4:])
            result_text = f"""📜 {line1}\n{line2}

📝 {k['Tamil explanation']}

📚 Paal: {k['Paal']} | Adhigaram: {k['Adhigaram']}"""
            st.success(result_text)
            st.session_state.summary.append(result_text)

# ✅ Urai Lookup
elif menu == "📘 Urai":
    st.subheader("📘 Urai (Explanation)")
    num = st.number_input("Enter Kural Number", min_value=1, max_value=1330, step=1, key="urai_num")
    commentator = st.selectbox("Choose Urai", ["Kalaingar", "Parimezhalagar", "Varadharajanar", "Solomon"])

    if st.button("Get Urai"):
        kural = df[df["Kural No"] == num]
        if kural.empty:
            st.error("❌ Kural not found.")
        else:
            k = kural.iloc[0]
            urai_map = {
                "Kalaingar": "Kalaingar_Urai",
                "Parimezhalagar": "Parimezhalagar_Urai",
                "Varadharajanar": "M_Varadharajanar",
                "Solomon": "Solomon_Pappaiya"
            }
            urai = k.get(urai_map.get(commentator), "❌ Urai not available.")
            st.info(urai)
            st.session_state.summary.append(f"📘 Urai by {commentator} for Kural {num}:\n{urai}")

# ✅ Translation
elif menu == "🌐 Translation":
    st.subheader("🌐 Translation")
    num = st.number_input("Enter Kural Number", min_value=1, max_value=1330, step=1, key="trans_num")
    direction = st.radio(
        "Direction",
        ["Tamil to English", "English to Tamil", "English to Other Indian Language"]
    )

    if direction == "English to Other Indian Language":
        lang_code = st.selectbox(
            "Select Target Language",
            options=["hi", "ml", "te", "kn", "ta", "gu", "mr", "pa", "bn"],
            format_func=lambda x: {
                "hi": "Hindi",
                "ml": "Malayalam",
                "te": "Telugu",
                "kn": "Kannada",
                "ta": "Tamil",
                "gu": "Gujarati",
                "mr": "Marathi",
                "pa": "Punjabi",
                "bn": "Bengali"
            }[x]
        )

    if st.button("Translate"):
        kural = df[df["Kural No"] == num]
        if kural.empty:
            st.error("❌ Kural not found.")
        else:
            k = kural.iloc[0]
            try:
                if direction == "Tamil to English":
                    result = k["English explanation"]
                elif direction == "English to Tamil":
                    result = k["Tamil explanation"]
                else:
                    result = GoogleTranslator(source='en', target=lang_code).translate(k["English explanation"])

                st.success(result)
                st.session_state.summary.append(f"🌐 Translation for Kural {num} ({direction}):\n{result}")
            except Exception as e:
                st.error(f"❌ Translation Error: {e}")

# ✅ Topic Search
elif menu == "🔍 Topic Search":
    st.subheader("🔍 Search Kural by Topic")
    topic = st.text_input("Enter keyword (English)")
    if st.button("Search"):
        result = df[df["English explanation"].str.contains(topic, case=False, na=False)]
        if result.empty:
            st.error("❌ No Kural found matching this topic.")
        else:
            output = ""
            for _, row in result.iterrows():
                lines = row["Tamil kural"].split()
                line1 = ' '.join(lines[:4])
                line2 = ' '.join(lines[4:])
                entry = f"""### 📌 Kural {row['Kural No']}
📜 {line1}\n{line2}

📝 {row["Tamil explanation"]}
📚 Paal: {row["Paal"]} | 🏷️ Adhigaram: {row["Adhigaram"]}
---
"""
                output += entry
            st.markdown(output)
            st.session_state.summary.append(f"🔍 Topic Search for '{topic}':\n{output}")

# ✅ Quiz Game
elif menu == "🎮 Quiz":
    st.subheader("🎮 Kural Quiz")
    game_type = st.radio(
        "Select Game Type",
        ["Missing Word", "Match Kural Number", "Identify Adhigaram"]
    )

    if st.button("Start Quiz"):
        kural = df.sample(1).iloc[0]
        if game_type == "Missing Word":
            words = kural["Tamil kural"].split()
            idx = random.randint(0, len(words) - 1)
            answer = words[idx]
            words[idx] = "____"
            question = ' '.join(words)
            all_words = sum(df["Tamil kural"].dropna().str.split().tolist(), [])
            options = random.sample(list(set(all_words)), 3) + [answer]

        elif game_type == "Match Kural Number":
            question = kural["Tamil kural"]
            answer = str(kural["Kural No"])
            options = random.sample(list(df["Kural No"].astype(str)), 3) + [answer]
        elif game_type == "Identify Adhigaram":
            question = kural["Tamil kural"]
            answer = kural["Adhigaram"]
            options = random.sample(list(df["Adhigaram"].unique()), 3) + [answer]

        random.shuffle(options)
        st.session_state.quiz = {"question": question, "options": options, "answer": answer}

    if st.session_state.quiz["question"]:
        st.write(f"### ❓ {st.session_state.quiz['question']}")
        user_choice = st.radio("Options", st.session_state.quiz["options"])

        if st.button("Submit"):
            st.session_state.score["total"] += 1
            if user_choice == st.session_state.quiz["answer"]:
                st.session_state.score["correct"] += 1
                result = f"✅ Correct! Score: {st.session_state.score['correct']}/{st.session_state.score['total']}"
                st.success(result)
            else:
                result = f"❌ Wrong! Correct: {st.session_state.quiz['answer']} | Score: {st.session_state.score['correct']}/{st.session_state.score['total']}"
                st.error(result)
            st.session_state.summary.append(f"🎮 Quiz ({game_type}) Result:\n{result}")

# ✅ Chatbot
elif menu == "🤖 Chatbot":
    st.subheader("🤖 Emotion-Based Kural Chatbot")
    chat_input = st.text_input("Say something (e.g., I'm sad, I'm happy, I love...)")
    emotions = {
        "happy": ["happy", "joy", "smile"],
        "sad": ["sad", "cry", "unhappy"],
        "love": ["love", "miss", "like"],
        "anger": ["angry", "mad", "furious"]
    }

    if st.button("Chat"):
        emotion = None
        for emo, words in emotions.items():
            if any(word in chat_input.lower() for word in words):
                emotion = emo
                break

        if not emotion:
            st.warning("🤖 I couldn't detect your mood.")
        else:
            result = df[df["English explanation"].str.contains(emotion, case=False, na=False)]
            if result.empty:
                st.error("❌ No matching Kural found.")
            else:
                row = result.sample(1).iloc[0]
                lines = row["Tamil kural"].split()
                line1 = ' '.join(lines[:4])
                line2 = ' '.join(lines[4:])
                response = f"""📜 {line1}\n{line2}

📝 {row["Tamil explanation"]}"""
                st.success(response)
                st.session_state.summary.append(f"🤖 Chatbot ({emotion} mood):\n{response}")

# ✅ Download Summary as TXT Only
st.sidebar.subheader("📥 Download Summary")

if st.sidebar.button("🗒️ Download as TXT"):
    summary_text = "\n\n".join(st.session_state.summary)
    st.sidebar.download_button(
        label="📥 Download TXT",
        data=summary_text,
        file_name="Thirukkural_Summary.txt",
        mime="text/plain"
    )
