import streamlit as st
import pandas as pd
import gspread
from gspread_dataframe import set_with_dataframe
import random
from roue_component import roue_interactive
import time


# ========================= Connexion Google Sheets =========================

@st.cache_resource(show_spinner=False)
def get_sheet():
    gc = gspread.service_account_from_dict(
        st.secrets["gcp_service_account"]
    )

    sheet_name = st.secrets["app"]["SHEET_NAME"]

    return gc.open(sheet_name)


def get_worksheet():
    sh = get_sheet()

    ws_name = st.secrets["app"]["WORKSHEET"]

    try:
        ws = sh.worksheet(ws_name)

    except gspread.WorksheetNotFound:

        ws = sh.add_worksheet(
            title=ws_name,
            rows=1000,
            cols=10
        )

        ws.update(
            "A1:F1",
            [[
                "Titre",
                "Auteur",
                "Lu ?",
                "Prêté ?",
                "étoiles",
                "Information"
            ]]
        )

    return ws


@st.cache_data(ttl=15)
def charger_livres():

    ws = get_worksheet()

    records = ws.get_all_records()

    colonnes = [
        "Titre",
        "Auteur",
        "Lu ?",
        "Prêté ?",
        "étoiles",
        "Information"
    ]

    if not records:
        return pd.DataFrame(columns=colonnes)

    df = pd.DataFrame(records)

    for col in colonnes:
        if col not in df.columns:
            df[col] = ""

    df = df[colonnes]

    df["Titre"] = df["Titre"].astype(str).str.strip()

    df["Auteur"] = df["Auteur"].astype(str).str.strip()

    df["Lu ?"] = df["Lu ?"].astype(str).str.strip()

    df["Lu ?"] = df["Lu ?"].replace("", "Non")

    return df


def sauvegarder_livres(df):

    ws = get_worksheet()

    ws.clear()

    set_with_dataframe(
        ws,
        df,
        include_index=False
    )

    st.cache_data.clear()


def tirer_livre(liste):

    if not liste:
        return None

    return random.choice(liste)


def supprimer_livre(df, titre):

    df.loc[
        df["Titre"] == titre,
        "Lu ?"
    ] = "Oui"

    sauvegarder_livres(df)


def reinitialiser_liste(df):

    df["Lu ?"] = "Non"

    sauvegarder_livres(df)

# ================ Initialisation de l'application Streamlit ================
st.set_page_config(page_title="🎡 Angie's reading wheel", layout="centered")

st.markdown(
    """
    <link rel="apple-touch-icon" href="/app/static/apple-touch-icon.png">
    <link rel="icon" href="/app/static/apple-touch-icon.png">
    """,
    unsafe_allow_html=True
)

data = charger_livres()

livres_a_lire = data[
    data["Lu ?"] == "Non"
]["Titre"].dropna().tolist()

livres_lus = data[
    data["Lu ?"] == "Oui"
]["Titre"].dropna().tolist()

livres_a_lire_details = data[
    data["Lu ?"] == "Non"
].apply(
    lambda row: f"{row['Titre']} — {row['Auteur']}" if row["Auteur"] else row["Titre"],
    axis=1
).tolist()

livres_lus_details = data[
    data["Lu ?"] == "Oui"
].apply(
    lambda row: f"{row['Titre']} — {row['Auteur']}" if row["Auteur"] else row["Titre"],
    axis=1
).tolist()

# Initialiser la mémoire temporaire pour le livre tiré
if "livre_tire" not in st.session_state:
    st.session_state.livre_tire = None

if "spin_id" not in st.session_state:
    st.session_state.spin_id = 0


st.markdown("""
<div style='text-align: center;'>
    <h1 style='font-size: 48px;'>🎡 Angie's reading wheel</h1>
    <h2 style='font-size: 26px; margin-top: -10px;'>Quelle sera ta prochaine lecture ?</h2>
    <h3 style='font-size: 22px; margin-top: 50px;'>🎲 Tirage au sort</h3>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([2, 1, 2])

with col2:
    if st.button("Tirer un livre"):
        if livres_a_lire:
            st.session_state.lancer_roue = True
            st.session_state.spin_id += 1

        else:
            st.warning("Aucun livre dans la roue 🥲")


# Affichage de la roue avec le nouveau composant
if livres_a_lire:
    roue_interactive(
        livres=livres_a_lire, 
        lancer=st.session_state.get("lancer_roue", False),
        spin_id=st.session_state.spin_id,
        height=600
    )

    # Si la roue vient d'être lancée, faire le tirage immédiatement
    if st.session_state.get("lancer_roue", False):
        livre_tire = tirer_livre(livres_a_lire)
        st.session_state.livre_tire = livre_tire
        time.sleep(3.5)

else:
    st.info("🎉 Aucun livre dans la roue actuellement.")


# Réinitialise la commande pour ne pas relancer en boucle
if "lancer_roue" in st.session_state:
    st.session_state.lancer_roue = False


# Afficher le livre tiré
if st.session_state.livre_tire:
    st.markdown(f"""
        <div style="text-align: center; margin-top: 30px;">
            <h3 style="font-size: 28px;">🏆 Livre sélectionné : <em>{st.session_state.livre_tire}</em></h3>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        if st.button("✅ Valider ce tirage et supprimer ce livre de la roue"):
            supprimer_livre(data, st.session_state.livre_tire)
            st.success(f"✅ Le livre '{st.session_state.livre_tire}' a été retiré de la roue.")
            st.session_state.livre_tire = None
            st.rerun()

st.markdown(f"<p style='text-align:center;'>Il reste {len(livres_a_lire)} livres dans la roue.</p>", unsafe_allow_html=True)

st.markdown("<p style='font-size:18px;'>➕ Ajouter un nouveau livre</p>", unsafe_allow_html=True)


with st.form("Ajouter un nouveau livre"):

    nouveau_titre = st.text_input("Titre du livre ✍️")
    nouvel_auteur = st.text_input("Auteur.ice ✍️")

    if st.form_submit_button("Ajouter ce livre"):
        nouveau_titre = nouveau_titre.strip()
        nouvel_auteur = nouvel_auteur.strip()
        titres_existants = (data["Titre"].astype(str).str.strip().tolist())
        if nouveau_titre:
            if nouveau_titre not in titres_existants:
                nouvelle_ligne = {
                    "Titre": nouveau_titre,
                    "Auteur": nouvel_auteur,
                    "Lu ?": "Non",
                    "Prêté ?": "",
                    "étoiles": "",
                    "Information": ""
                }

                data = pd.concat([data, pd.DataFrame([nouvelle_ligne])], ignore_index=True)

                sauvegarder_livres(data)

                st.success(f"✅ Livre '{nouveau_titre}' ajouté.")
                st.rerun()

            else:
                st.warning("⚠️ Impossible d'ajouter ce livre, déjà présent ou déjà tiré.")


st.markdown("<p style='font-size:18px;'>🗑️ Supprimer un livre manuellement</p>", unsafe_allow_html=True)


if livres_a_lire:
    with st.form("suppression_formulaire"):
        livres_selectionnes = st.multiselect(
            "Recherche un livre à supprimer de la roue :",
            livres_a_lire,
            max_selections=1
        )

        supprimer = st.form_submit_button("Supprimer ce livre")

        if supprimer:
            if livres_selectionnes:
                livre_selectionne = livres_selectionnes[0]

                supprimer_livre(data, livre_selectionne)

                st.success(f"📤 Livre '{livre_selectionne}' supprimé de la roue.")
                st.rerun()

            else:
                st.warning("⚠️ Sélectionne d'abord un livre.")
else:
    st.info("🎉 Aucun livre dans la roue actuellement.")

st.markdown("<p style='font-size:18px;'>🔄 Réinitialiser la roue</p>", unsafe_allow_html=True)

if st.button("Remettre tous les livres dans la roue"):
    reinitialiser_liste(data)
    st.success("🔁 Tous les livres ont été réintégrés dans la roue.")
    st.session_state.livre_tire = None
    st.rerun()

with st.expander("📖 Voir les livres encore dans la roue"):
    if livres_a_lire:
        st.markdown("• " + "<br>• ".join(livres_a_lire_details), unsafe_allow_html=True)
    else:
        st.info("Aucun livre dans la roue.")

with st.expander("✅ Voir les livres déjà tirés/retirés"):
    if livres_lus:
        st.markdown("• " + "<br>• ".join(livres_lus_details), unsafe_allow_html=True)
    else:
        st.info("Aucun livre encore tiré.")