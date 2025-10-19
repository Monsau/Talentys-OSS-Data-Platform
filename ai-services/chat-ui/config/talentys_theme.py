"""
Talentys Design System - Theme Configuration
Corporate colors, branding, and styling for AI Agent Interface
"""

# Talentys Brand Colors
TALENTYS_PRIMARY = "#0066CC"      # Talentys Blue
TALENTYS_SECONDARY = "#003D7A"    # Dark Blue
TALENTYS_ACCENT = "#00A8E8"       # Light Blue
TALENTYS_SUCCESS = "#28A745"      # Green
TALENTYS_WARNING = "#FFC107"      # Amber
TALENTYS_DANGER = "#DC3545"       # Red
TALENTYS_LIGHT = "#F8F9FA"        # Light Gray
TALENTYS_DARK = "#212529"         # Dark Gray

# Logo Configuration
TALENTYS_LOGO_URL = "https://talentys.eu/logo.png"
TALENTYS_LOGO_LOCAL = "static/img/talentys-logo.png"

# Company Information
COMPANY_NAME = "Talentys"
COMPANY_TAGLINE = "Data Engineering & Analytics Excellence"
COMPANY_EMAIL = "support@talentys.eu"
COMPANY_WEBSITE = "https://talentys.eu"

# Custom CSS Theme
TALENTYS_CSS = """
<style>
    /* ========================================
       TALENTYS GLOBAL THEME
       ======================================== */
    
    :root {
        --talentys-primary: #0066CC;
        --talentys-secondary: #003D7A;
        --talentys-accent: #00A8E8;
        --talentys-success: #28A745;
        --talentys-warning: #FFC107;
        --talentys-danger: #DC3545;
        --talentys-light: #F8F9FA;
        --talentys-dark: #212529;
        
        --gradient-primary: linear-gradient(135deg, #0066CC 0%, #00A8E8 100%);
        --gradient-dark: linear-gradient(135deg, #003D7A 0%, #0066CC 100%);
        
        --shadow-sm: 0 2px 4px rgba(0, 102, 204, 0.1);
        --shadow-md: 0 4px 12px rgba(0, 102, 204, 0.15);
        --shadow-lg: 0 8px 24px rgba(0, 102, 204, 0.2);
        
        --border-radius: 12px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* ========================================
       MAIN LAYOUT
       ======================================== */
    
    .stApp {
        background: linear-gradient(135deg, #F8F9FA 0%, #E8F4F8 100%);
    }
    
    /* Header */
    .main-header {
        background: var(--gradient-primary);
        color: white;
        padding: 2rem 3rem;
        border-radius: var(--border-radius);
        margin-bottom: 2rem;
        box-shadow: var(--shadow-lg);
        animation: slideDown 0.5s ease-out;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.95;
        margin: 0.5rem 0 0 0;
    }
    
    /* Logo */
    .talentys-logo {
        height: 50px;
        width: auto;
        filter: brightness(0) invert(1);
        animation: fadeIn 0.8s ease-in;
    }
    
    /* ========================================
       SIDEBAR STYLING
       ======================================== */
    
    [data-testid="stSidebar"] {
        background: white;
        box-shadow: var(--shadow-md);
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background: var(--gradient-dark);
        padding-top: 2rem;
    }
    
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: var(--talentys-primary);
        font-weight: 600;
    }
    
    /* Sidebar Logo */
    .sidebar-logo {
        text-align: center;
        padding: 1rem;
        background: white;
        border-radius: var(--border-radius);
        margin-bottom: 1rem;
    }
    
    .sidebar-logo img {
        max-width: 80%;
        height: auto;
    }
    
    /* ========================================
       CARDS & CONTAINERS
       ======================================== */
    
    .talentys-card {
        background: white;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-md);
        margin: 1rem 0;
        border-left: 4px solid var(--talentys-primary);
        transition: var(--transition);
        animation: fadeInUp 0.5s ease-out;
    }
    
    .talentys-card:hover {
        box-shadow: var(--shadow-lg);
        transform: translateY(-2px);
    }
    
    .source-card {
        background: var(--talentys-light);
        padding: 1.2rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        border-left: 3px solid var(--talentys-accent);
        transition: var(--transition);
    }
    
    .source-card:hover {
        background: white;
        box-shadow: var(--shadow-sm);
        border-left-color: var(--talentys-primary);
    }
    
    /* Upload Section */
    .upload-section {
        background: linear-gradient(135deg, #E8F4F8 0%, #D0E8F7 100%);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        border: 2px dashed var(--talentys-accent);
        margin: 1rem 0;
        text-align: center;
        transition: var(--transition);
    }
    
    .upload-section:hover {
        border-color: var(--talentys-primary);
        background: linear-gradient(135deg, #D0E8F7 0%, #B8DDF5 100%);
    }
    
    /* ========================================
       BUTTONS
       ======================================== */
    
    .stButton > button {
        background: var(--gradient-primary);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
    }
    
    .stButton > button:hover {
        background: var(--gradient-dark);
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Primary Button */
    button[kind="primary"] {
        background: var(--talentys-primary) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    button[kind="primary"]:hover {
        background: var(--talentys-secondary) !important;
        box-shadow: var(--shadow-lg) !important;
    }
    
    /* ========================================
       BADGES & LABELS
       ======================================== */
    
    .score-badge {
        background: var(--talentys-primary);
        color: white;
        padding: 0.25rem 0.7rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        box-shadow: var(--shadow-sm);
    }
    
    .status-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .status-online {
        background: var(--talentys-success);
        color: white;
    }
    
    .status-offline {
        background: var(--talentys-danger);
        color: white;
    }
    
    /* ========================================
       CHAT INTERFACE
       ======================================== */
    
    .stChatMessage {
        background: white;
        border-radius: var(--border-radius);
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: var(--shadow-sm);
        animation: fadeInUp 0.3s ease-out;
    }
    
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, #E8F4F8 0%, #D0E8F7 100%);
        border-left: 4px solid var(--talentys-primary);
    }
    
    .stChatMessage[data-testid="assistant-message"] {
        background: white;
        border-left: 4px solid var(--talentys-accent);
    }
    
    /* Chat Input */
    .stChatInputContainer {
        border-top: 2px solid var(--talentys-light);
        background: white;
        padding: 1rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-md);
    }
    
    /* ========================================
       FORM ELEMENTS
       ======================================== */
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > select {
        border: 2px solid var(--talentys-light);
        border-radius: 8px;
        transition: var(--transition);
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stSelectbox > div > div > select:focus {
        border-color: var(--talentys-primary);
        box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1);
    }
    
    /* Sliders */
    .stSlider > div > div > div > div {
        background: var(--talentys-primary);
    }
    
    /* File Uploader */
    [data-testid="stFileUploader"] {
        border: 2px dashed var(--talentys-accent);
        border-radius: var(--border-radius);
        padding: 1.5rem;
        background: var(--talentys-light);
        transition: var(--transition);
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: var(--talentys-primary);
        background: white;
    }
    
    /* ========================================
       EXPANDERS
       ======================================== */
    
    .streamlit-expanderHeader {
        background: var(--talentys-light);
        border-radius: 8px;
        padding: 0.8rem 1.2rem;
        font-weight: 600;
        color: var(--talentys-primary);
        transition: var(--transition);
    }
    
    .streamlit-expanderHeader:hover {
        background: var(--talentys-accent);
        color: white;
    }
    
    /* ========================================
       ALERTS & MESSAGES
       ======================================== */
    
    .stSuccess {
        background: linear-gradient(135deg, #D4EDDA 0%, #C3E6CB 100%);
        border-left: 4px solid var(--talentys-success);
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stError {
        background: linear-gradient(135deg, #F8D7DA 0%, #F5C6CB 100%);
        border-left: 4px solid var(--talentys-danger);
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stWarning {
        background: linear-gradient(135deg, #FFF3CD 0%, #FFE8A1 100%);
        border-left: 4px solid var(--talentys-warning);
        border-radius: 8px;
        padding: 1rem;
    }
    
    .stInfo {
        background: linear-gradient(135deg, #D1ECF1 0%, #BEE5EB 100%);
        border-left: 4px solid var(--talentys-accent);
        border-radius: 8px;
        padding: 1rem;
    }
    
    /* ========================================
       FOOTER
       ======================================== */
    
    .talentys-footer {
        background: var(--gradient-dark);
        color: white;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        text-align: center;
        margin-top: 2rem;
        box-shadow: var(--shadow-md);
    }
    
    .talentys-footer a {
        color: var(--talentys-accent);
        text-decoration: none;
        font-weight: 600;
        transition: var(--transition);
    }
    
    .talentys-footer a:hover {
        color: white;
        text-decoration: underline;
    }
    
    /* ========================================
       ANIMATIONS
       ======================================== */
    
    @keyframes fadeIn {
        from {
            opacity: 0;
        }
        to {
            opacity: 1;
        }
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
    
    /* Loading Animation */
    .loading-spinner {
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    /* ========================================
       RESPONSIVE DESIGN
       ======================================== */
    
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 1.8rem;
        }
        
        .talentys-card {
            padding: 1rem;
        }
    }
    
    /* ========================================
       ADMIN INTERFACE SPECIFIC
       ======================================== */
    
    .admin-panel {
        background: white;
        border-radius: var(--border-radius);
        padding: 2rem;
        box-shadow: var(--shadow-lg);
        margin: 1rem 0;
    }
    
    .admin-stat-card {
        background: var(--gradient-primary);
        color: white;
        padding: 1.5rem;
        border-radius: var(--border-radius);
        text-align: center;
        box-shadow: var(--shadow-md);
        transition: var(--transition);
    }
    
    .admin-stat-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
    }
    
    .admin-stat-card h2 {
        font-size: 2.5rem;
        margin: 0;
        font-weight: 700;
    }
    
    .admin-stat-card p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Login Form */
    .login-container {
        max-width: 450px;
        margin: 5rem auto;
        background: white;
        padding: 3rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow-lg);
        animation: fadeInUp 0.5s ease-out;
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-header img {
        max-width: 200px;
        margin-bottom: 1rem;
    }
    
    .login-header h1 {
        color: var(--talentys-primary);
        font-size: 1.8rem;
        margin-bottom: 0.5rem;
    }
    
    .login-header p {
        color: #6c757d;
    }
    
    /* ========================================
       UTILITIES
       ======================================== */
    
    .text-primary {
        color: var(--talentys-primary);
    }
    
    .text-secondary {
        color: var(--talentys-secondary);
    }
    
    .text-accent {
        color: var(--talentys-accent);
    }
    
    .bg-primary {
        background: var(--talentys-primary);
    }
    
    .bg-gradient {
        background: var(--gradient-primary);
    }
    
    .shadow-sm {
        box-shadow: var(--shadow-sm);
    }
    
    .shadow-md {
        box-shadow: var(--shadow-md);
    }
    
    .shadow-lg {
        box-shadow: var(--shadow-lg);
    }
    
    .rounded {
        border-radius: var(--border-radius);
    }
</style>
"""

def get_theme_css():
    """Return the complete Talentys CSS theme"""
    return TALENTYS_CSS

def get_brand_colors():
    """Return Talentys brand colors as dict"""
    return {
        "primary": TALENTYS_PRIMARY,
        "secondary": TALENTYS_SECONDARY,
        "accent": TALENTYS_ACCENT,
        "success": TALENTYS_SUCCESS,
        "warning": TALENTYS_WARNING,
        "danger": TALENTYS_DANGER,
        "light": TALENTYS_LIGHT,
        "dark": TALENTYS_DARK,
    }

def get_company_info():
    """Return company information"""
    return {
        "name": COMPANY_NAME,
        "tagline": COMPANY_TAGLINE,
        "email": COMPANY_EMAIL,
        "website": COMPANY_WEBSITE,
        "logo_url": TALENTYS_LOGO_URL,
        "logo_local": TALENTYS_LOGO_LOCAL,
    }
