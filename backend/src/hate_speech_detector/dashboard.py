"""Streamlit dashboard for the hate speech detector.

Design constraints:
- Light mode only.
- No Unicode emojis anywhere in the UI.
- French output for end users.
- Automatic translation to English before classification.
"""
import joblib
import numpy as np
import pandas as pd
import shap
import streamlit as st

from hate_speech_detector.config import CLASS_LABELS, MODELS_DIR
from hate_speech_detector.data import clean_text, count_aae_markers
from hate_speech_detector.utils import predict_text, translate_if_needed

st.set_page_config(page_title="Détecteur de discours haineux", layout="wide")

# Force light theme via custom HTML (Streamlit default is already light; this reinforces it).
st.markdown(
    """
    <style>
    body { background-color: #ffffff; color: #1a1a1a; }
    .stApp { background-color: #ffffff; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def load_artifacts():
    vectorizer = joblib.load(MODELS_DIR / "tfidf_vectorizer.joblib")
    lr = joblib.load(MODELS_DIR / "logistic_regression.joblib")
    rf = joblib.load(MODELS_DIR / "random_forest.joblib")
    feature_names = vectorizer.get_feature_names_out()
    shap_explainer = shap.TreeExplainer(rf)
    return vectorizer, lr, rf, feature_names, shap_explainer


vectorizer, lr, rf, feature_names, shap_explainer = load_artifacts()


def top_features(text: str, model_name: str, pred_class: int, n: int = 6):
    """Return the most influential words for a prediction."""
    cleaned = clean_text(text)
    X = vectorizer.transform([cleaned])
    if model_name == "logistic_regression":
        coefs = lr.coef_[pred_class]
        vals = X.toarray()[0] * coefs
    else:
        raw_sv = shap_explainer.shap_values(X.toarray())  # list of (n_features, n_classes)
        sv = np.stack(raw_sv, axis=0)
        vals = sv[0, :, pred_class]
    top = sorted(zip(feature_names, vals), key=lambda x: abs(x[1]), reverse=True)[:n]
    return [(w, round(float(v), 4)) for w, v in top if abs(v) > 1e-6]


def display_result(result: dict):
    pred = result["predicted_class"]
    conf = result["confidence"]
    labels_fr = {
        "hate_speech": "Discours haineux",
        "offensive_language": "Langage offensant",
        "neither": "Ni haineux ni offensant",
    }
    st.subheader("Conclusion")
    st.markdown(f"**Classe prédite :** {labels_fr[pred]}")
    st.markdown(f"**Score de confiance :** {conf:.1%}")

    if result["was_translated"]:
        st.info(f"Texte détecté en langue '{result['detected_language']}'. "
                f"Traduction utilisée pour la prédiction : {result['translated_text']}")

    if result["aae_marker_count"] > 0:
        st.warning(
            "Alerte : le texte contient des marqueurs du proxy dialectal AAE. "
            "Ceci est un indicateur de prudence, pas une preuve d'erreur. "
            "Le modèle peut être plus incertain sur des variantes linguistiques sous-représentées "
            "ou faussement associer certains marqueurs à la toxicité."
        )

    with st.expander("Détail technique"):
        st.write("Probabilités par classe")
        probs = result["probabilities"]
        prob_df = pd.DataFrame(
            {"Classe": [labels_fr[k] for k in CLASS_LABELS],
             "Probabilité": [probs[k] for k in CLASS_LABELS]}
        )
        st.dataframe(prob_df, hide_index=True, use_container_width=True)

        st.write("Mots les plus influents")
        pred_idx = CLASS_LABELS.index(pred)
        influents = top_features(result["translated_text"], result["model_used"], pred_idx)
        if influents:
            st.table(pd.DataFrame(influents, columns=["Mot / bigramme", "Poids"]))
        else:
            st.write("Aucun mot fortement influent détecté.")


st.title("Détecteur de discours haineux")
st.caption("Prototype éducatif avec audit de biais dialectal. Ne pas utiliser pour modérer automatiquement.")

mode = st.radio("Mode", ["Analyse simple", "Comparaison côte à côte"], horizontal=True)

model_choice = st.selectbox("Modèle", ["random_forest", "logistic_regression"],
                            format_func=lambda x: "Forêt aléatoire" if x == "random_forest" else "Régression logistique")

if mode == "Analyse simple":
    user_text = st.text_area("Saisissez un texte (toute langue acceptée)", height=120)
    if st.button("Analyser"):
        if not user_text.strip():
            st.error("Veuillez saisir un texte.")
        else:
            result = predict_text(user_text, model_name=model_choice)
            display_result(result)
else:
    col1, col2 = st.columns(2)
    with col1:
        text_a = st.text_area("Phrase A", height=120, key="text_a")
    with col2:
        text_b = st.text_area("Phrase B", height=120, key="text_b")
    if st.button("Comparer"):
        if not text_a.strip() or not text_b.strip():
            st.error("Veuillez saisir les deux phrases.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("**Phrase A**")
                res_a = predict_text(text_a, model_name=model_choice)
                display_result(res_a)
            with c2:
                st.markdown("**Phrase B**")
                res_b = predict_text(text_b, model_name=model_choice)
                display_result(res_b)

st.divider()
st.markdown(
    "**Gouvernance :** ce modèle est un outil d'aide à la décision. "
    "Toute sanction (bannissement, suppression) doit être confirmée par un humain et offrir un recours."
)
