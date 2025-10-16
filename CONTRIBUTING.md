# Contributing to OpenMetadata Dremio Connector

[English](#english) | [Français](#français)

---

## English

### How to Contribute

We welcome contributions from the community! Here's how you can help:

#### Reporting Issues

1. Check existing issues to avoid duplicates
2. Use the issue template
3. Include:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, Dremio version, OpenMetadata version)
   - Relevant logs or screenshots

#### Submitting Changes

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/openmetadata-dremio-connector.git
   cd openmetadata-dremio-connector
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the existing code style
   - Add tests if applicable
   - Update documentation

4. **Test your changes**
   ```bash
   # Run dbt tests
   cd dbt
   dbt test
   
   # Test Python scripts
   python -m pytest tests/
   ```

5. **Commit with clear messages**
   ```bash
   git add .
   git commit -m "feat: add support for additional data types"
   ```

6. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

#### Commit Message Format

Use conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

#### Code Style

- **Python**: Follow PEP 8
- **SQL/dbt**: Use lowercase with underscores
- **YAML**: 2-space indentation
- **Comments**: Write clear, concise comments

#### Testing

- Add unit tests for new Python functions
- Add dbt tests for new models
- Ensure all existing tests pass

#### Documentation

- Update README.md for new features
- Add inline comments for complex logic
- Update SETUP_COMPLETE.md if setup process changes

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/openmetadata-dremio-connector.git
cd openmetadata-dremio-connector

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt

# Start services
cd docker
docker compose up -d

# Run tests
cd ../dbt
dbt test
```

### Review Process

1. Maintainers will review your PR
2. Address feedback and requested changes
3. Once approved, your PR will be merged
4. You'll be added to contributors list

### Questions?

- Open a discussion on GitHub
- Contact maintainers via email

---

## Français

### Comment Contribuer

Nous accueillons les contributions de la communauté ! Voici comment vous pouvez aider :

#### Signaler des Problèmes

1. Vérifiez les issues existantes pour éviter les doublons
2. Utilisez le template d'issue
3. Incluez :
   - Description claire du problème
   - Étapes pour reproduire
   - Comportement attendu vs réel
   - Détails de l'environnement (OS, version Python, version Dremio, version OpenMetadata)
   - Logs ou captures d'écran pertinents

#### Soumettre des Modifications

1. **Forker le dépôt**
   ```bash
   git clone https://github.com/yourusername/openmetadata-dremio-connector.git
   cd openmetadata-dremio-connector
   ```

2. **Créer une branche feature**
   ```bash
   git checkout -b feature/nom-de-votre-feature
   ```

3. **Effectuer vos modifications**
   - Suivre le style de code existant
   - Ajouter des tests si applicable
   - Mettre à jour la documentation

4. **Tester vos modifications**
   ```bash
   # Exécuter les tests dbt
   cd dbt
   dbt test
   
   # Tester les scripts Python
   python -m pytest tests/
   ```

5. **Commit avec des messages clairs**
   ```bash
   git add .
   git commit -m "feat: ajout du support pour types de données additionnels"
   ```

6. **Push et créer une Pull Request**
   ```bash
   git push origin feature/nom-de-votre-feature
   ```

#### Format des Messages de Commit

Utiliser les commits conventionnels :
- `feat:` Nouvelle fonctionnalité
- `fix:` Correction de bug
- `docs:` Modifications de documentation
- `style:` Changements de style de code (formatage)
- `refactor:` Refactorisation du code
- `test:` Ajout de tests
- `chore:` Tâches de maintenance

#### Style de Code

- **Python** : Suivre PEP 8
- **SQL/dbt** : Utiliser minuscules avec underscores
- **YAML** : Indentation de 2 espaces
- **Commentaires** : Écrire des commentaires clairs et concis

#### Tests

- Ajouter des tests unitaires pour les nouvelles fonctions Python
- Ajouter des tests dbt pour les nouveaux modèles
- S'assurer que tous les tests existants passent

#### Documentation

- Mettre à jour README.md pour les nouvelles fonctionnalités
- Ajouter des commentaires inline pour la logique complexe
- Mettre à jour SETUP_COMPLETE.md si le processus de setup change

### Configuration de Développement

```bash
# Cloner le dépôt
git clone https://github.com/yourusername/openmetadata-dremio-connector.git
cd openmetadata-dremio-connector

# Créer l'environnement virtuel
python -m venv venv
source venv/bin/activate

# Installer les dépendances
pip install -r requirements-dev.txt

# Démarrer les services
cd docker
docker compose up -d

# Exécuter les tests
cd ../dbt
dbt test
```

### Processus de Revue

1. Les mainteneurs examineront votre PR
2. Adressez les feedbacks et modifications demandées
3. Une fois approuvée, votre PR sera mergée
4. Vous serez ajouté à la liste des contributeurs

### Questions ?

- Ouvrir une discussion sur GitHub
- Contacter les mainteneurs par email

---

**Thank you for contributing! / Merci pour votre contribution !**
