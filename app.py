import streamlit as st
import json
import os
import random
import streamlit.components.v1 as components
from roue_component import roue_interactive
import time

FICHIER_LIVRES = "livres.json"

def charger_livres():
    if os.path.exists(FICHIER_LIVRES): 
        with open(FICHIER_LIVRES, "r", encoding="utf-8") as f:  
            return json.load(f)  
    else:
        return {"liste_tirage": [], "livres_supprimes": []}

def sauvegarder_livres(data):
    with open(FICHIER_LIVRES, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def tirer_livre(liste):
    if not liste:
        return None
    return random.choice(liste)

def ajouter_livre(data, nouveau_livre):
    nouveau_livre = nouveau_livre.strip()
    if nouveau_livre and nouveau_livre not in data["liste_tirage"] and nouveau_livre not in data["livres_supprimes"]:
        data["liste_tirage"].append(nouveau_livre)
        sauvegarder_livres(data)
        return True
    return False

def supprimer_livre(data, livre):
    if livre in data["liste_tirage"]:
        data["liste_tirage"].remove(livre) 
        data["livres_supprimes"].append(livre)  
        sauvegarder_livres(data)

def reinitialiser_liste(data):
    data["liste_tirage"] += data["livres_supprimes"]
    data["livres_supprimes"] = []
    sauvegarder_livres(data)

# ================ Initialisation de l'application Streamlit ================
st.set_page_config(page_title="🎡 Angie's reading wheel", layout="centered")

# Charger les données depuis le JSON
data = charger_livres()

# Initialiser la mémoire temporaire pour le livre tiré
if "livre_tire" not in st.session_state:
    st.session_state.livre_tire = None

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
        if data["liste_tirage"]:
            st.session_state.lancer_roue = True
        else:
            st.warning("Aucun livre dans la roue 🥲")



# Affichage de la roue avec le nouveau composant
if data["liste_tirage"]:
    roue_interactive(
        livres=data["liste_tirage"], 
        lancer=st.session_state.get("lancer_roue", False),
        height=600
    )
    
    # Si la roue vient d'être lancée, faire le tirage immédiatement
    if st.session_state.get("lancer_roue", False):
        livre_tire = tirer_livre(data["liste_tirage"])
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

st.markdown(f"<p style='text-align:center;'>Il reste {len(data['liste_tirage'])} livres dans la roue.</p>", unsafe_allow_html=True)

st.markdown("<p style='font-size:18px;'>➕ Ajouter un nouveau livre</p>", unsafe_allow_html=True)

with st.form("Ajouter un nouveau livre"):
    nouveau_livre_form = st.text_input("Titre du livre à ajouter ✍️")
    
    if st.form_submit_button("Ajouter ce livre"):
        if ajouter_livre(data, nouveau_livre_form):
            st.success(f"✅ Livre '{nouveau_livre_form}' ajouté à la liste.")
            st.rerun()
        else:
            st.warning("⚠️ Impossible d'ajouter ce livre, déjà présent ou déjà tiré.")

st.markdown("<p style='font-size:18px;'>🗑️ Supprimer un livre manuellement</p>", unsafe_allow_html=True)

if data["liste_tirage"]:
    with st.form("suppression_formulaire"):
        livre_a_supprimer_form = st.selectbox("Choisis un livre à supprimer de la roue :", data["liste_tirage"])
        supprimer = st.form_submit_button("Supprimer ce livre")
        
        if supprimer:
            supprimer_livre(data, livre_a_supprimer_form)
            st.success(f"📤 Livre '{livre_a_supprimer_form}' supprimé de la roue.")
            st.rerun()
else:
    st.info("🎉 Aucun livre dans la roue actuellement.")

st.markdown("<p style='font-size:18px;'>🔄 Réinitialiser la roue</p>", unsafe_allow_html=True)

if st.button("Remettre tous les livres dans la roue"):
    reinitialiser_liste(data)
    st.success("🔁 Tous les livres ont été réintégrés dans la roue.")
    st.session_state.livre_tire = None
    st.rerun()

with st.expander("📖 Voir les livres encore dans la roue"):
    if data["liste_tirage"]:
        st.markdown("• " + "<br>• ".join(data["liste_tirage"]), unsafe_allow_html=True)
    else:
        st.info("Aucun livre dans la roue.")

with st.expander("✅ Voir les livres déjà tirés/retirés"):
    if data["livres_supprimes"]:
        st.markdown("• " + "<br>• ".join(data["livres_supprimes"]), unsafe_allow_html=True)
    else:
        st.info("Aucun livre encore tiré.")