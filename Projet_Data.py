!apt-get update
!apt-get install -y chromium-chromedriver
!cp /usr/lib/chromium-browser/chromedriver /usr/bin
!pip install selenium

!pip install streamlit
%%writefile applicationDataCollection.py
import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options  # ne pas importer Options autrement

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = Service()  # ou Service('/usr/bin/chromedriver') si nécessaire
    driver = webdriver.Chrome(service=service, options=options)
    return driver

driver = get_driver()
driver.get("https://www.google.com")
print(driver.title)
driver.quit()

pip install pandas requests beautifulsoup4 matplotlib numpy streamlit
import pandas as pd
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
import streamlit as st
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import json
# --- Configuration initiale de Selenium ---
categories_data = {
    'https://sn.coinafrique.com/categorie/vetements-homme': 'habits',
    'https://sn.coinafrique.com/categorie/chaussures-homme': 'chaussures',
    'https://sn.coinafrique.com/categorie/vetements-enfants': 'habits',
    'https://sn.coinafrique.com/categorie/chaussures-enfants': 'chaussures'
}
path = r'C:\chrome-win64\chromedriver-win64\chromedriver.exe'

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
chrome_options.add_argument(f"user-agent={user_agent}")

service = Service(executable_path=path)

def scrape_coinafrique(url, item_type):
    driver = webdriver.Chrome(service=service, options=chrome_options)
    all_product_data = []
    try:
        print(f"Ouverture de la page principale : {url}")
        driver.get(url)
        time.sleep(3)

        links_elements = driver.find_elements(By.CSS_SELECTOR, "div.col.s6.m4.l3 a")
        urls_a_explorer = [link_element.get_attribute('href') for link_element in links_elements if link_element.get_attribute('href') and link_element.get_attribute('href').startswith('http')]

        print(f"Trouvé {len(urls_a_explorer)} URLs de produits à explorer.")

        for i, product_url in enumerate(urls_a_explorer):
            print(f"\n--- Scraping du produit {i+1} : {product_url} ---")
            driver.get(product_url)
            time.sleep(3)

            current_product_data = {'type habits': None, 'type chaussures': None, 'prix': 'N/A', 'adresse': 'N/A', 'image_lien': 'N/A', 'url': product_url}
            if item_type == 'habits':
                current_product_data['type habits'] = item_type
            else:
                current_product_data['type chaussures'] = item_type

            try:
                price_element = driver.find_element(By.CSS_SELECTOR, 'p.price')
                current_product_data['prix'] = price_element.text.strip()
                print(f"  Prix trouvé : {current_product_data['prix']}")
            except Exception as e:
                print(f"  Erreur lors de la récupération du prix : {e}")

            try:
                location_element = driver.find_element(By.CSS_SELECTOR, 'p.seller-city')
                current_product_data['adresse'] = location_element.text.strip()
                print(f"  Adresse trouvée : {current_product_data['adresse']}")
            except Exception as e:
                print(f"  Erreur lors de la récupération de l'adresse : {e}")

            try:
                image_container = driver.find_element(By.CSS_SELECTOR, 'div.product-image')
                image_element = image_container.find_element(By.TAG_NAME, 'img')
                current_product_data['image_lien'] = image_element.get_attribute('src')
                print(f"  Lien image trouvé : {current_product_data['image_lien']}")
            except Exception as e:
                print(f"  Erreur lors de la récupération du lien image : {e}")

            all_product_data.append(current_product_data)
            driver.back()
            time.sleep(2)
    except Exception as e:
        print(f"Une erreur s'est produite lors du scraping de {url}: {e}")
    finally:
        driver.quit()
    return pd.DataFrame(all_product_data)
st.title("Application de Web Scraping pour Coin Afrique")

st.header("Scraper et Nettoyer les Données (Selenium)")

dataframes = {}

for url, item_type in categories_data.items():
    if st.button(f"Scraper {item_type.capitalize()} de {url.split('/')[-1].replace('-', ' ').capitalize()}"):
        with st.spinner(f"Scraping des {item_type.capitalize()} de {url.split('/')[-1].replace('-', ' ').capitalize()}..."):
            dataframes[item_type] = scrape_coinafrique(url, item_type)
            st.subheader(f"Données des {item_type.capitalize()} de {url.split('/')[-1].replace('-', ' ').capitalize()}:")
            st.dataframe(dataframes[item_type])

st.header("Télécharger les Données Scrapées avec Web Scraper (Non Nettoyées)")

fichier_telecharge = st.file_uploader("Téléchargez ici votre fichier de données JSON Web Scraper", type="json")

if fichier_telecharge is not None:
    try:
        donnees_web_scraper = json.load(fichier_telecharge)
        st.subheader("Données Brutes de Web Scraper:")
        st.write(donnees_web_scraper)

        @st.cache_data
        def convertir_df_en_csv(data):
            df = pd.DataFrame(data)
            return df.to_csv(index=False).encode('utf-8')

        if donnees_web_scraper:
            if isinstance(donnees_web_scraper, list):
                csv_data = convertir_df_en_csv(donnees_web_scraper)
                st.download_button(
                    label="Télécharger les Données Web Scraper au format CSV",
                    data=csv_data,
                    file_name="donnees_web_scraper.csv",
                    mime='text/csv',
                )
            else:
                st.warning("Le fichier JSON téléchargé ne semble pas être une liste.")

    except json.JSONDecodeError:
        st.error("Fichier JSON invalide téléchargé.")

st.header("Tableau de Bord des Données Nettoyées (provenant de Web Scraper)")
st.info("Veuillez télécharger vos données *nettoyées* de Web Scraper (par exemple, sous forme de fichier CSV) pour afficher le tableau de bord.")

fichier_nettoye_telecharge = st.file_uploader("Téléchargez vos données Web Scraper nettoyées (CSV) pour le tableau de bord", type="csv")

if fichier_nettoye_telecharge is not None:
    try:
        df_tableau_bord = pd.read_csv(fichier_nettoye_telecharge)
        st.subheader("Tableau de Bord:")
        st.dataframe(df_tableau_bord)

        if not df_tableau_bord.empty:
            st.subheader("Répartition par Type")
            type_counts = df_tableau_bord['type habits'].fillna(df_tableau_bord['type chaussures']).value_counts()
            st.bar_chart(type_counts)

            if 'prix' in df_tableau_bord.columns and pd.api.types.is_numeric_dtype(df_tableau_bord['prix']):
                st.subheader("Distribution des Prix")
                st.hist_chart(df_tableau_bord['prix'])

            if 'adresse' in df_tableau_bord.columns:
                st.subheader("Répartition par Adresse (Top 5)")
                address_counts = df_tableau_bord['adresse'].value_counts().nlargest(5)
                st.bar_chart(address_counts)

    except pd.errors.EmptyDataError:
        st.error("Le fichier CSV téléchargé est vide.")
    except pd.errors.ParserError:
        st.error("Erreur lors de l'analyse du fichier CSV téléchargé.")

st.header("Formulaire d'Évaluation de l'Application")
your_kobo_link = "https://ee.kobotoolbox.org/x/aHTKbU2G"
with st.form("formulaire_evaluation"):
    evaluation = st.slider("Évaluez cette application :", 1, 5, 3)
    commentaires = st.text_area("Des commentaires ou suggestions ?", max_chars=500)
    st.markdown(f"Ou remplissez notre formulaire détaillé sur [https://ee.kobotoolbox.org/x/aHTKbU2G]({your_kobo_link})", unsafe_allow_html=True)
    soumis = st.form_submit_button("Soumettre l'Évaluation")
    if soumis:
        st.write(f"Merci pour votre feedback ! Vous avez évalué l'application avec : {evaluation} étoiles.")
        if commentaires:
            st.write(f"Vos commentaires : {commentaires}")