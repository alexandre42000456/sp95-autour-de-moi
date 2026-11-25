# SP95 autour de moi

Carte web qui affiche instantanément les stations proposant du **SP95 (sans plomb 95)** et leur prix dans un rayon réglable (2,5 km par défaut) autour de la position de l'appareil.

- Données : [Prix des carburants en France – Flux instantané – v2](https://www.data.gouv.fr/fr/datasets/prix-des-carburants-en-france-flux-instantane-v2-amelioree/) (Ministère de l'Économie, Licence Ouverte), interrogées en direct via l'API Explore v2.1 de data.economie.gouv.fr (filtre `within_distance`).
- Fond de carte : Plan IGN (Géoplateforme) avec Leaflet.
- Recherche d'adresse : service de géocodage de la Géoplateforme.

Fonctions : géolocalisation, rayon modifiable (curseur ou saisie), position déplaçable (clic sur la carte ou glisser le point bleu), tri par prix ou distance, stations en rupture en option, liens d'itinéraire (Google Maps, Waze, Plans), actualisation automatique toutes les 5 minutes.

Une seule page statique (`index.html`), sans compilation ni clé d'API. La géolocalisation nécessite HTTPS (GitHub Pages) ou `localhost`.
