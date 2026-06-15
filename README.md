# Bibliothèque Unikam

Application de gestion de bibliothèque développée avec Flask.

## Acteurs
- Étudiant : recherche et consultation de la disponibilité d'un livre
- Bibliothécaire : ajout, suppression, modification, emprunt, retour et gestion du stock
- Directeur : consultation du stock, rapports mensuels et consultation des emprunts

## Installation

1. Dans `c:\Users\Elizee Mbuya\bibliotheque_unikam`, créer un environnement virtuel :
   ```bash
   python -m venv venv
   ```
2. Activer l'environnement :
   - Windows : `venv\Scripts\activate`
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

## Configuration PostgreSQL

1. Installer PostgreSQL si ce n'est pas déjà fait.
2. Créer une base de données :
   ```bash
   psql -U postgres -c "CREATE DATABASE bibliotheque_unikam;"
   ```
3. Si nécessaire, créer l'utilisateur et lui donner les droits :
   ```bash
   psql -U postgres -c "CREATE USER bibliothecaire WITH PASSWORD 'votre_mot_de_passe';"
   psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE bibliotheque_unikam TO bibliothecaire;"
   ```
4. Définir la variable d'environnement `DATABASE_URL` :
   - Sur Render, utilise l'URL fournie :
     ```bash
     set DATABASE_URL=postgresql://martin_admin:Vj4EBZKu9NetAdILgoaxGV7roXmfLahi@dpg-d8mvl7ojs32c73d4uqcg-a.ohio-postgres.render.com/bibliotheque_db_pl37
     ```
   - Sur ton PC local, tu peux aussi utiliser cette URL si le réseau Render l'autorise.

> L'application est maintenant configurée pour utiliser cette base Render par défaut si `DATABASE_URL` n'est pas défini.

## Déploiement en ligne

Pour avoir à la fois l'application et la base de données accessibles depuis internet, utilise un service cloud.

### Base de données distante

- ElephantSQL, Railway, Heroku Postgres, Azure Database for PostgreSQL, Google Cloud SQL
- Ces services te fournissent une URL PostgreSQL du type :
  ```text
  postgresql://user:password@host:port/dbname
  ```
- Mets cette URL dans `DATABASE_URL` sur le serveur ou la plateforme d'hébergement.

### Hébergement de l'application

- Render, Railway, Heroku, Azure App Service, Fly.io, ou un VPS
- Dans l'environnement de déploiement, configure :
  - `DATABASE_URL`
  - `FLASK_SECRET`
- L'application utilisera la base distante automatiquement.

### Exemple de configuration sur le serveur

```bash
set DATABASE_URL=postgresql://monuser:monmdp@monsrv:5432/bibliotheque_unikam
set FLASK_SECRET=ma_clef_secrete
python app.py
```

## Lancement

1. Toujours dans l'environnement virtuel :
   ```bash
   python app.py
   ```
2. Ouvrir `http://127.0.0.1:5000`.

> Au premier démarrage, la base sera créée automatiquement et les livres par défaut seront ajoutés si la table est vide.
