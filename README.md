# Export du Volume d'Impression des Utilisateurs - Application GESPAGE

Ce projet contient un script Python automatisé conçu pour extraire les rapports de volume d'impression de chaque utilisateur à partir de l'application GESPAGE. Le script utilise **Selenium** pour simuler la navigation sur l'interface de GESPAGE, se connecter, configurer les dates, et générer les rapports souhaités. Les rapports sont ensuite téléchargés et sauvegardés localement, facilitant ainsi la gestion et l'analyse des volumes d'impression des utilisateurs.

## Fonctionnalités du Script

1. **Automatisation de la Connexion :** Le script se connecte automatiquement à l'interface administrateur de GESPAGE en utilisant les identifiants fournis dans le code.
2. **Configuration des Dates :** Il détermine automatiquement la période du mois précédent et ajuste les champs de date sur l'interface pour générer les rapports correspondants.
3. **Téléchargement Automatique :** Les rapports générés sont téléchargés automatiquement et sauvegardés dans un dossier spécifique, basé sur l'année en cours.
4. **Gestion des Fichiers et des Logs :** Le script gère les journaux d'activité pour garder une trace des actions effectuées et des éventuelles erreurs. Les fichiers téléchargés sont enregistrés de manière organisée.

## Technologies Utilisées

- **Python 3**
- **Selenium WebDriver** : Pour automatiser la navigation sur l'application GESPAGE.
- **Google Chrome (en mode Headless)** : Pour simuler la navigation web sans interface graphique.
- **Git** : Pour le suivi des versions et la gestion de code source.

## Prérequis

- **Python 3.x** installé sur votre machine.
- **Google Chrome** et **ChromeDriver** compatibles avec la version de Chrome installée.
- **Selenium** installé via pip :
  ```bash
  pip install selenium
  ```
- **Clé SSH ou Token d'accès personnel (PAT)** si vous souhaitez pousser des changements vers le dépôt GitHub.

## Configuration et Utilisation

1. **Cloner le dépôt :**
   ```bash
   git clone https://github.com/maheanuu/export_gespage.git
   cd export_gespage
   ```

2. **Configurer les Identifiants et Chemins :**
   Assurez-vous que les identifiants de connexion et les chemins vers ChromeDriver sont correctement configurés dans le script `download_gespage_report.py`.

3. **Exécuter le Script :**
   ```bash
   python3 download_gespage_report.py
   ```

4. **Gestion des Logs :**
   Les logs des opérations seront enregistrés dans le dossier `logs` à la racine du projet. Ils fournissent des informations sur les actions effectuées et aident à diagnostiquer les éventuels problèmes.

## Exemple de Fonctionnement

Lorsque le script est exécuté, voici ce qui se passe :

1. **Connexion Automatique :** Le script se connecte à l'interface administrateur de GESPAGE en utilisant des identifiants prédéfinis.
2. **Configuration des Dates :** Il ajuste automatiquement les dates pour définir la période du mois précédent (par exemple, du 1er au 30 septembre 2024).
3. **Génération du Rapport :** Le script lance la génération du rapport de volume d'impression pour chaque utilisateur.
4. **Téléchargement et Sauvegarde :** Le fichier rapport est téléchargé et sauvegardé dans un dossier nommé par l'année (ex: `2024`).

## Notes Techniques

- Le script utilise des **options de navigation en mode headless**, ce qui signifie qu'il fonctionne en arrière-plan sans afficher de fenêtre de navigateur.
- Il prend également en charge la gestion de la langue pour s'assurer que le navigateur est configuré en français, facilitant l'interaction avec l'interface en cas de détection de langue spécifique.
- Les fichiers journaux sont sauvegardés dans un dossier nommé `logs` à la racine du projet pour faciliter la surveillance et le débogage.

## Contributions

Les contributions sont les bienvenues ! Si vous souhaitez améliorer le script, ajoutez de nouvelles fonctionnalités, ou corriger des bugs, veuillez soumettre une **pull request** ou ouvrir une **issue**.

1. **Fork** le projet.
2. Créez une **branche** pour votre fonctionnalité (`git checkout -b feature/ma-nouvelle-fonctionnalite`).
3. **Commit** vos changements (`git commit -am 'Ajout d'une nouvelle fonctionnalité'`).
4. **Push** vers la branche (`git push origin feature/ma-nouvelle-fonctionnalite`).
5. Créez une **pull request** pour que nous puissions réviser votre contribution.

---

### Contact

Pour toute question ou assistance, vous pouvez me contacter directement via GitHub.
