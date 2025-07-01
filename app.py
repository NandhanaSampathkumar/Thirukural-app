import streamlit as st
import pandas as pd
import random
from datetime import datetime
from deep_translator import GoogleTranslator


# ✅ App Config
st.set_page_config(page_title="📖 Thirukkural Explorer", layout="wide")

# ✅ Load Dataset
df = pd.read_excel("thirukural.xlsx")
df["Kural No"] = pd.to_numeric(df["Kural No"], errors="coerce").astype(int)

# ✅ Session State
if "score" not in st.session_state: st.session_state.score = []
if "quiz" not in st.session_state: st.session_state.quiz = {"question": "", "options": [], "answer": ""}
if "summary" not in st.session_state: st.session_state.summary = []
if "bookmarks" not in st.session_state: st.session_state.bookmarks = []
if "user_name" not in st.session_state: st.session_state.user_name = ""
if "current_kural" not in st.session_state: st.session_state.current_kural = None


# ✅ Sidebar Menu
st.sidebar.title("📚 Menu")
menu = st.sidebar.radio("Select Option", [
    "📅 Today's Kural", "🔢 Kural Lookup", "📘 Urai", "🌐 Translation",
    "🔍 Topic Search", "🎮 Quiz", "🤖 Chatbot", "🔖 Bookmarks"
])

# 📅 Today's Kural
if menu == "📅 Today's Kural":
    st.subheader("📅 Dhinam Oru Kural")
    kural_no = (datetime.now().day + datetime.now().month + datetime.now().year) % 1330 + 1
    k = df[df["Kural No"] == kural_no].iloc[0]
    st.markdown(f"### 📜 Kural {kural_no}")
    st.write(k["Tamil kural"])
    st.write(f"📝 {k['Tamil explanation']}")
    st.write(f"📚 Paal: {k['Paal']} | 🏷️ Adhigaram: {k['Adhigaram']}")


# 🔢 Kural Lookup with Improved Short Story
elif menu == "🔢 Kural Lookup":
    st.subheader("🔢 Kural Lookup")
    num = st.number_input("Enter Kural Number", 1, 1330, step=1)

    if st.button("Search"):
        k = df[df["Kural No"] == num].iloc[0]
        st.session_state.current_kural = {
            "number": num,
            "text": f"📜 {k['Tamil kural']}\n📝 {k['Tamil explanation']}\n📚 Paal: {k['Paal']} | 🏷️ Adhigaram: {k['Adhigaram']}"
        }

    if st.session_state.current_kural:
        kural_info = st.session_state.current_kural
        k_data = df[df["Kural No"] == kural_info["number"]].iloc[0]
        st.success(kural_info["text"])
        st.session_state.summary.append(kural_info["text"])

        if st.button("🔖 Bookmark this Kural"):
            if kural_info not in st.session_state.bookmarks:
                st.session_state.bookmarks.append(kural_info)
                st.success("✅ Bookmarked!")

        st.markdown("### 📖 Moral Story")

        adhigaram = k_data["Adhigaram"]
        explanation = k_data["English explanation"]

        if kural_info["number"] == 1:
            st.info("""
In a small village, an old sage taught his disciples that everything starts with the divine.
He pointed to the sunrise and said, "Just as light begins the day, the grace of God begins all success."
The villagers learned that acknowledging a higher power brings harmony in life.

✅ **Moral:** Everything starts with a divine foundation.
""")
        else:
            st.info(f"""
Once upon a time, in a peaceful town, lived a person named Arjun who believed in the importance of **{adhigaram.lower()}**.
Whenever challenges arose, he reminded himself, "{explanation.split('.')[0]}."
One day, he helped a stranger selflessly without expecting anything in return. Surprisingly, fortune smiled upon him soon after.

✅ **Moral:** {explanation.split('.')[0].strip()}.
""")


# 📘 Urai
elif menu == "📘 Urai":
    st.subheader("📘 Urai (Explanation)")
    num = st.number_input("Enter Kural Number", 1, 1330, key="urai_num")
    author = st.selectbox("Choose Urai", ["Kalaingar", "Parimezhalagar", "Varadharajanar", "Solomon"])
    lang = st.selectbox("Translate Urai to", ["en", "hi", "ml", "te", "kn", "gu", "mr", "pa", "bn"],
        format_func=lambda x: {
            "en": "English", "hi": "Hindi", "ml": "Malayalam", "te": "Telugu",
            "kn": "Kannada", "gu": "Gujarati", "mr": "Marathi", "pa": "Punjabi", "bn": "Bengali"
        }[x])
    if st.button("Get Urai"):
        k = df[df["Kural No"] == num].iloc[0]
        urai_map = {
            "Kalaingar": "Kalaingar_Urai",
            "Parimezhalagar": "Parimezhalagar_Urai",
            "Varadharajanar": "M_Varadharajanar",
            "Solomon": "Solomon_Pappaiya"
        }
        urai = k.get(urai_map[author], "Urai not available.")
        st.write(f"📜 {k['Tamil kural']}")
        st.write(f"📝 {urai}")
        try:
            translated = GoogleTranslator(source='auto', target=lang).translate(urai)
            st.info(f"🌐 Translated Urai: {translated}")
        except:
            st.warning("❌ Could not translate.")


# 🌐 Translation
elif menu == "🌐 Translation":
    st.subheader("🌐 Translate Kural + Explanation")
    num = st.number_input("Enter Kural Number", 1, 1330, key="trans_num")
    direction = st.radio("Translate", ["Tamil to English", "English to Tamil", "English to Other Indian Language"])
    lang = None
    if direction == "English to Other Indian Language":
        lang = st.selectbox("Choose Language", ["hindi", "malayalam", "telugu", "kannada", "gujarati", "marathi", "punjabi", "bengali"])
    if st.button("Translate"):
        k = df[df["Kural No"] == num].iloc[0]
        if direction == "Tamil to English":
            st.write("📜", k["Tamil kural"])
            st.write("📝", k["English explanation"])
        elif direction == "English to Tamil":
            st.write("📜", k["Tamil kural"])
            st.write("📝", k["Tamil explanation"])
        else:
            try:
                tk = GoogleTranslator(source='auto', target=lang).translate(k["Tamil kural"])
                te = GoogleTranslator(source='auto', target=lang).translate(k["English explanation"])
                st.write("📜", tk)
                st.write("📝", te)
            except:
                st.error("Translation failed.")


# 🔍 Topic Search
elif menu == "🔍 Topic Search":
    st.subheader("🔍 Search Kural by Topic")
    lang_code = st.selectbox("Translate Result To", ["english", "hindi", "malayalam", "telugu", "kannada", "gujarati", "marathi", "punjabi", "bengali"])
    topic = st.text_input("Enter keyword")
    if st.button("Search"):
        results = df[df["English explanation"].str.contains(topic, case=False, na=False)]
        for _, row in results.iterrows():
            try:
                explanation = GoogleTranslator(source='en', target=lang_code).translate(row["English explanation"])
                st.markdown(f"**📌 Kural {row['Kural No']}**")
                st.markdown(f"📜 {row['Tamil kural']}")
                st.markdown(f"📝 {explanation}")
                st.markdown(f"📚 Paal: {row['Paal']} | 🏷️ Adhigaram: {row['Adhigaram']}")
                st.markdown("---")
            except:
                continue


# 🎮 Quiz
elif menu == "🎮 Quiz":
    st.subheader("🎮 Kural Quiz")
    game = st.radio("Game Type", ["Missing Word", "Match Kural Number", "Identify Adhigaram"])
    def load_quiz():
        k = df.sample(1).iloc[0]
        if game == "Missing Word":
            words = k["Tamil kural"].split()
            if len(words) < 2: return
            idx = random.randint(0, len(words) - 1)
            answer = words[idx]
            words[idx] = "____"
            q = " ".join(words)
            all_words = sum(df["Tamil kural"].dropna().str.split().tolist(), [])
            opts = random.sample(list(set(all_words) - {answer}), 3) + [answer]
        elif game == "Match Kural Number":
            q = k["Tamil kural"]
            answer = str(k["Kural No"])
            opts = random.sample(list(df["Kural No"].astype(str)), 3) + [answer]
        else:
            q = k["Tamil kural"]
            answer = k["Adhigaram"]
            opts = random.sample(list(df["Adhigaram"].unique()), 3) + [answer]
        random.shuffle(opts)
        st.session_state.quiz = {"question": q, "options": opts, "answer": answer}
    if st.button("Start Quiz") or not st.session_state.quiz["question"]:
        load_quiz()
    if st.session_state.quiz["question"]:
        st.write(f"### ❓ {st.session_state.quiz['question']}")
        user_ans = st.radio("Options", st.session_state.quiz["options"])
        if st.button("Submit"):
            correct = user_ans == st.session_state.quiz["answer"]
            st.session_state.score.append(correct)
            st.success("✅ Correct!" if correct else f"❌ Wrong! Answer: {st.session_state.quiz['answer']}")
        if st.button("Next"):
            load_quiz()
        st.info(f"Total Score: {sum(st.session_state.score)} / {len(st.session_state.score)}")


# 🤖 Chatbot
elif menu == "🤖 Chatbot":
    st.subheader("🤖 Kural-Chatbot")

    if not st.session_state.user_name:
        name = st.text_input("👋 What's your name?")
        if st.button("Start Chat"):
            st.session_state.user_name = name
    else:
        st.write(f"Hi **{st.session_state.user_name}**, welcome to the Kural Chatbot! 👋")
        st.write("I’m here to suggest you a Thirukkural based on how you're feeling today.")

        mood = st.text_input("💬 Tell me how you're feeling ")

        if st.button("Send"):
            emotions = {
                "sad": ["sad", "upset", "depressed", "unhappy", "gloomy"],
                "happy": ["happy", "joyful", "excited", "cheerful"],
                "angry": ["angry", "mad", "furious", "annoyed"],
                "love": ["love", "romantic", "affection", "beloved"],
                "fear": ["fear", "afraid", "scared", "worried"],
                "peace": ["calm", "peaceful", "relaxed", "serene"],
                "grateful": ["thankful", "grateful", "blessed", "appreciate"],
                "hunger": ["hungry", "starving", "food", "thirsty"]
            }

            matched = next((e for e, words in emotions.items() if any(w in mood.lower() for w in words)), None)

            if matched:
                results = df[df["English explanation"].str.contains(matched, case=False, na=False)]
                if not results.empty:
                    k = results.sample(1).iloc[0]
                    st.markdown(f"""
### 💡 Here's a Kural for you:
📜 **{k['Tamil kural']}**  
📝 **Explanation**: {k['Tamil explanation']}  
📚 **Moral**: {k['English explanation']}
""")
                else:
                    st.warning("🤔 I couldn't find a Kural that matches your emotion. Try a simpler word.")
            else:
                st.info("🔍 Hmm... I didn’t recognize that emotion. Try describing it differently.")


# 🔖 Bookmarks
elif menu == "🔖 Bookmarks":
    st.subheader("🔖 Your Bookmarked Kurals")
    if st.session_state.bookmarks:
        for i, b in enumerate(st.session_state.bookmarks, 1):
            st.markdown(f"**{i}. Kural {b['number']}**\n{b['text']}")
    else:
        st.info("You haven’t bookmarked any Kural yet.")


# 📥 Download Summary
st.sidebar.subheader("📥 Download Summary")
if st.sidebar.button("🗒️ Download as TXT"):
    text = "\n\n".join(st.session_state.summary)
    st.sidebar.download_button("📥 Download TXT", data=text, file_name="Thirukkural_Summary.txt", mime="text/plain")
