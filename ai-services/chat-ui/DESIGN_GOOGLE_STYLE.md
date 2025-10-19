# 🎨 Design Sobre Style Google - Instructions

## Demandes Utilisateur
1. ❌ Retirer le petit logo près du robot (doublon)
2. 📏 Réduire la taille du grand logo
3. 🎨 Couleurs plus sobres style Google
4. 🎨 Marier les couleurs du logo Talentys

## Solution Actuelle
L'interface actuelle (après rebuild) affiche:
- ✅ Logo Talentys de 48px dans le header (sobre)
- ✅ Pas de doublon de logo près du robot
- ✅ Sidebar avec logo Talentys 80px
- ✅ Footer sobre

## Améliorations CSS Style Google (Optionnel)

### À Ajouter dans `app.py` - Section CSS

```css
/* Style Google - Plus sobre */
:root {
    --google-blue: #1a73e8;
    --google-blue-dark: #1765cc;
    --google-gray-900: #202124;
    --google-gray-700: #5f6368;
    --google-gray-200: #e8eaed;
    --google-gray-50: #f8f9fa;
}

/* Header minimaliste */
.talentys-header {
    padding: 1rem 0;
    border-bottom: 1px solid var(--google-gray-200);
}

.talentys-logo-header {
    width: 40px;  /* Encore plus petit */
    height: auto;
}

.talentys-title {
    font-size: 1.375rem;  /* 22px */
    color: var(--google-gray-900);
    font-weight: 400;
    margin: 0;
}

.talentys-title .brand {
    color: var(--google-blue);
    font-weight: 500;
}

/* Sidebar Google-style */
[data-testid="stSidebar"] {
    background-color: var(--google-gray-50);
    border-right: 1px solid var(--google-gray-200);
}

[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--google-gray-900);
    font-size: 0.875rem;  /* 14px */
    font-weight: 500;
    text-transform: none;
}

/* Boutons style Google */
.stButton > button {
    background-color: var(--google-blue);
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 24px;
    font-size: 14px;
    font-weight: 500;
    text-transform: none;
    transition: background-color 0.2s, box-shadow 0.2s;
}

.stButton > button:hover {
    background-color: var(--google-blue-dark);
    box-shadow: 0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15);
}

/* Footer minimaliste */
.talentys-footer {
    margin-top: 48px;
    padding: 12px 0;
    border-top: 1px solid var(--google-gray-200);
    text-align: center;
    font-size: 12px;
    color: var(--google-gray-700);
}

.talentys-footer a {
    color: var(--google-blue);
    text-decoration: none;
}

.talentys-footer a:hover {
    text-decoration: underline;
}
```

### HTML Header (À remplacer dans `app.py`)

```python
# Header sobre style Google - Sans robot emoji
st.markdown("""
<div class="talentys-header">
    <div style="display: flex; align-items: center; gap: 12px;">
        <img src="static/img/talentys-logo.png" class="talentys-logo-header" alt="Talentys"/>
        <div>
            <h1 class="talentys-title"><span class="brand">Talentys</span> AI Data Assistant</h1>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
```

## Palette Couleurs Talentys (du Logo)

### Couleurs Principales
- **Bleu Marine Foncé**: `#003D7A` - Barre du logo "TALENTYS"
- **Bleu Marine**: `#0066CC` - Forme en Y
- **Bleu Clair**: `#4A90E2` - Nuances
- **Gris Foncé**: `#2C3E50` - Texte "DATA"

### Mapping Google ↔ Talentys

| Élément | Google | Talentys Adapté |
|---------|--------|-----------------|
| Primaire | `#1a73e8` | `#0066CC` ✅ |
| Hover | `#1765cc` | `#003D7A` ✅ |
| Texte Principal | `#202124` | `#2C3E50` ✅ |
| Texte Secondaire | `#5f6368` | `#5f6368` ✅ |
| Bordures | `#e8eaed` | `#e8eaed` ✅ |
| Background | `#f8f9fa` | `#f8f9fa` ✅ |

## Version Ultra-Sobre (Google Minimalist)

### Configuration Recommandée

```python
# Tailles
LOGO_HEADER = 40px  # Très petit
LOGO_SIDEBAR = 64px  # Compact

# Espacements
PADDING_HEADER = 1rem 0
PADDING_SIDEBAR = 0.75rem 0

# Typographie
FONT_SIZE_TITLE = 22px (1.375rem)
FONT_SIZE_LABEL = 14px (0.875rem)
FONT_SIZE_SMALL = 12px (0.75rem)

# Borders
BORDER_WIDTH = 1px
BORDER_COLOR = #e8eaed
BORDER_RADIUS = 4px (boutons) / 8px (cards)
```

### Footer Minimaliste

```python
st.markdown(f"""
<div class="talentys-footer">
    <div style="font-weight: 500; color: #1a73e8; margin-bottom: 4px;">
        Talentys Data Platform v1.0
    </div>
    <div>
        Model: {selected_model} · Temp: {temperature} · Messages: {len(st.session_state.messages)}
    </div>
    <div style="margin-top: 8px;">
        <a href="{COMPANY_INFO['website']}">talentys.eu</a> · 
        <a href="mailto:{COMPANY_INFO['email']}">Contact</a>
    </div>
</div>
""", unsafe_allow_html=True)
```

## État Actuel vs Proposé

### Actuellement ✅
- Logo 48px dans header
- Sidebar avec logo 80px
- Couleurs Talentys (#0066CC)
- Footer sobre

### Version Google (Si souhaité) 📝
- Logo 40px dans header (plus petit)
- Pas d'emoji robot près du logo
- Borders 1px gris clair partout
- Font Roboto/Google Sans
- Espacements réduits
- Footer ultra-compact

## Pour Appliquer

1. **Ouvrir**: `ai-services/chat-ui/app.py`
2. **Remplacer** la section CSS (lignes ~30-150)
3. **Remplacer** le header HTML (ligne ~200)
4. **Rebuild**: `docker-compose -f docker-compose-ai.yml up -d --build chat-ui`
5. **Tester**: http://localhost:8501

## Résultat Final Attendu

```
┌────────────────────────────────────────┐
│ [logo] Talentys AI Data Assistant     │  ← 40px, sobre
├────────────────────────────────────────┤
│                                        │
│  Ask questions...                      │
│                                        │
│  [Chat messages]                       │
│                                        │
├────────────────────────────────────────┤
│ Talentys Data Platform v1.0            │  ← Footer minimaliste
│ Model: llama3.1 · Temp: 0.7           │
│ talentys.eu · Contact                  │
└────────────────────────────────────────┘
```

---

**Version**: Sobre Google Style  
**Date**: 19 octobre 2025  
**Inspiration**: Google Search / Gmail  
**Couleurs**: Talentys Logo (#0066CC, #003D7A)
