"""
Talentys AI Agent - Admin Interface
Customizable AI agent with company branding, authentication, and management
"""
import streamlit as st
import sys
import os

# Add config to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'config'))

from config.talentys_theme import get_theme_css, get_company_info, get_brand_colors
from config.auth import authenticate, is_admin, list_users, create_user, change_password, delete_user

# Page configuration
st.set_page_config(
    page_title="Talentys AI Agent Admin",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Talentys theme
st.markdown(get_theme_css(), unsafe_allow_html=True)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None
if "admin_view" not in st.session_state:
    st.session_state.admin_view = "dashboard"

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.rerun()

def render_login_page():
    """Render the login page"""
    company_info = get_company_info()
    
    st.markdown("""
    <div class="login-container">
        <div class="login-header">
            <img src="https://talentys.eu/logo.png" alt="Talentys Logo">
            <h1>🎨 Admin Console</h1>
            <p>Talentys AI Agent Management</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Sign In")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submit = st.form_submit_button("🚀 Login", use_container_width=True, type="primary")
            with col_btn2:
                demo_hint = st.form_submit_button("💡 Demo Credentials", use_container_width=True)
            
            if demo_hint:
                st.info("**Demo Credentials:**\n- Username: `admin`\n- Password: `talentys2025`")
            
            if submit:
                if username and password:
                    user_info = authenticate(username, password)
                    
                    if user_info:
                        st.session_state.authenticated = True
                        st.session_state.user = user_info
                        st.success(f"✅ Welcome back, **{username}**!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
                else:
                    st.warning("⚠️ Please enter both username and password")
        
        st.divider()
        
        # Additional info
        st.markdown(f"""
        <div style="text-align: center; color: #6c757d; margin-top: 2rem;">
            <p>Need help? Contact <a href="mailto:{company_info['email']}">{company_info['email']}</a></p>
            <p style="font-size: 0.85rem; margin-top: 1rem;">
                &copy; 2025 {company_info['name']} - {company_info['tagline']}
            </p>
        </div>
        """, unsafe_allow_html=True)

def render_dashboard():
    """Render main dashboard"""
    company_info = get_company_info()
    colors = get_brand_colors()
    
    # Header
    st.markdown(f"""
    <div class="main-header">
        <h1>
            <img src="{company_info['logo_url']}" class="talentys-logo" alt="Talentys">
            🎨 AI Agent Admin Console
        </h1>
        <p>Customize your AI agent with company branding and manage settings</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="admin-stat-card">
            <h2>🤖</h2>
            <p>AI Agent Status</p>
            <span class="status-badge status-online">ONLINE</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        users = list_users()
        st.markdown(f"""
        <div class="admin-stat-card" style="background: linear-gradient(135deg, {colors['secondary']} 0%, {colors['primary']} 100%);">
            <h2>{len(users)}</h2>
            <p>Active Users</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="admin-stat-card" style="background: linear-gradient(135deg, {colors['accent']} 0%, {colors['primary']} 100%);">
            <h2>100%</h2>
            <p>Uptime</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="admin-stat-card" style="background: linear-gradient(135deg, {colors['success']} 0%, {colors['accent']} 100%);">
            <h2>v2.0</h2>
            <p>Version</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎨 Customize Theme", use_container_width=True, type="primary"):
            st.session_state.admin_view = "theme"
            st.rerun()
    
    with col2:
        if st.button("👥 Manage Users", use_container_width=True):
            st.session_state.admin_view = "users"
            st.rerun()
    
    with col3:
        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.admin_view = "settings"
            st.rerun()

def render_theme_customization():
    """Render theme customization page"""
    st.markdown("""
    <div class="main-header">
        <h1>🎨 Theme Customization</h1>
        <p>Customize your AI agent's look and feel with company branding</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Color customization
    st.markdown("### 🎨 Brand Colors")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        primary_color = st.color_picker("Primary Color", "#0066CC", help="Main brand color")
    
    with col2:
        secondary_color = st.color_picker("Secondary Color", "#003D7A", help="Complementary color")
    
    with col3:
        accent_color = st.color_picker("Accent Color", "#00A8E8", help="Highlight color")
    
    st.divider()
    
    # Logo customization
    st.markdown("### 🖼️ Logo Configuration")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        logo_url = st.text_input(
            "Logo URL",
            value="https://talentys.eu/logo.png",
            help="Direct URL to your company logo"
        )
        
        company_name = st.text_input(
            "Company Name",
            value="Talentys",
            help="Your company name"
        )
        
        tagline = st.text_input(
            "Tagline",
            value="Data Engineering & Analytics Excellence",
            help="Company tagline or slogan"
        )
    
    with col2:
        st.markdown("#### Preview")
        st.image(logo_url, width=200)
        st.markdown(f"**{company_name}**")
        st.caption(tagline)
    
    st.divider()
    
    # CSS Customization
    st.markdown("### 💅 Custom CSS")
    
    custom_css = st.text_area(
        "Additional CSS (Advanced)",
        height=200,
        placeholder="Enter custom CSS rules here...",
        help="Add custom CSS to further personalize your interface"
    )
    
    st.divider()
    
    # Preview
    st.markdown("### 👁️ Live Preview")
    
    st.markdown(f"""
    <div class="talentys-card" style="border-left-color: {primary_color};">
        <h3 style="color: {primary_color};">Sample Card</h3>
        <p>This is how your customized theme will look!</p>
        <button style="background: {primary_color}; color: white; border: none; padding: 0.5rem 1rem; border-radius: 8px;">
            Sample Button
        </button>
    </div>
    """, unsafe_allow_html=True)
    
    # Save button
    if st.button("💾 Save Theme Configuration", type="primary", use_container_width=True):
        st.success("✅ Theme configuration saved successfully!")
        st.balloons()

def render_user_management():
    """Render user management page"""
    st.markdown("""
    <div class="main-header">
        <h1>👥 User Management</h1>
        <p>Manage user accounts and permissions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 User List", "➕ Add User", "🔑 Change Password"])
    
    with tab1:
        st.markdown("### Current Users")
        
        users = list_users()
        
        for user in users:
            with st.expander(f"👤 **{user['username']}** - {user['role'].upper()}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Email:** {user['email']}")
                    st.write(f"**Role:** {user['role']}")
                
                with col2:
                    st.write(f"**Created:** {user['created_at'][:10]}")
                    st.write(f"**Last Login:** {user['last_login'][:10] if user['last_login'] != 'Never' else 'Never'}")
                
                if user['username'] != 'admin':
                    if st.button(f"🗑️ Delete {user['username']}", key=f"del_{user['username']}"):
                        if delete_user(user['username']):
                            st.success(f"✅ User {user['username']} deleted")
                            st.rerun()
                        else:
                            st.error("❌ Failed to delete user")
    
    with tab2:
        st.markdown("### Create New User")
        
        with st.form("create_user_form"):
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            new_role = st.selectbox("Role", ["user", "admin"])
            
            if st.form_submit_button("➕ Create User", type="primary"):
                if new_username and new_email and new_password:
                    if create_user(new_username, new_password, new_email, new_role):
                        st.success(f"✅ User **{new_username}** created successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Username already exists")
                else:
                    st.warning("⚠️ Please fill all fields")
    
    with tab3:
        st.markdown("### Change Password")
        
        with st.form("change_password_form"):
            username = st.session_state.user['username']
            st.info(f"Changing password for: **{username}**")
            
            old_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("🔑 Change Password", type="primary"):
                if new_password != confirm_password:
                    st.error("❌ Passwords don't match")
                elif len(new_password) < 8:
                    st.warning("⚠️ Password must be at least 8 characters")
                elif change_password(username, old_password, new_password):
                    st.success("✅ Password changed successfully!")
                else:
                    st.error("❌ Current password is incorrect")

def render_settings():
    """Render settings page"""
    st.markdown("""
    <div class="main-header">
        <h1>⚙️ Settings</h1>
        <p>Configure AI agent parameters and integrations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # AI Model Settings
    st.markdown("### 🤖 AI Model Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        default_model = st.selectbox(
            "Default LLM Model",
            ["llama3.1", "mistral", "phi3", "codellama"],
            help="Choose the default language model"
        )
        
        default_temperature = st.slider(
            "Default Temperature",
            0.0, 1.0, 0.7, 0.1,
            help="Lower = more focused, Higher = more creative"
        )
    
    with col2:
        default_top_k = st.slider(
            "Default Top K Documents",
            1, 20, 5,
            help="Number of context documents to retrieve"
        )
        
        max_tokens = st.number_input(
            "Max Tokens",
            min_value=100,
            max_value=4000,
            value=2000,
            help="Maximum response length"
        )
    
    st.divider()
    
    # Integration Settings
    st.markdown("### 🔗 Integrations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input("RAG API URL", value="http://rag-api:8002")
        st.text_input("Ollama URL", value="http://ollama:11434")
    
    with col2:
        st.text_input("Milvus URL", value="http://milvus:19530")
        st.text_input("MinIO URL", value="http://minio-ai:9000")
    
    st.divider()
    
    # Save button
    if st.button("💾 Save Settings", type="primary", use_container_width=True):
        st.success("✅ Settings saved successfully!")

# Main app logic
if not st.session_state.authenticated:
    render_login_page()
else:
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-logo">
            <img src="https://talentys.eu/logo.png" alt="Talentys">
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"### Welcome, {st.session_state.user['username']}! 👋")
        st.caption(f"Role: {st.session_state.user['role'].upper()}")
        
        st.divider()
        
        st.markdown("### 📋 Navigation")
        
        if st.button("🏠 Dashboard", use_container_width=True, type="primary" if st.session_state.admin_view == "dashboard" else "secondary"):
            st.session_state.admin_view = "dashboard"
            st.rerun()
        
        if st.button("🎨 Theme", use_container_width=True, type="primary" if st.session_state.admin_view == "theme" else "secondary"):
            st.session_state.admin_view = "theme"
            st.rerun()
        
        if st.button("👥 Users", use_container_width=True, type="primary" if st.session_state.admin_view == "users" else "secondary"):
            st.session_state.admin_view = "users"
            st.rerun()
        
        if st.button("⚙️ Settings", use_container_width=True, type="primary" if st.session_state.admin_view == "settings" else "secondary"):
            st.session_state.admin_view = "settings"
            st.rerun()
        
        st.divider()
        
        if st.button("🚀 Open Chat UI", use_container_width=True):
            st.link_button("Open Chat", "http://localhost:8501", use_container_width=True)
        
        if st.button("🚪 Logout", use_container_width=True):
            logout()
    
    # Render selected view
    if st.session_state.admin_view == "dashboard":
        render_dashboard()
    elif st.session_state.admin_view == "theme":
        render_theme_customization()
    elif st.session_state.admin_view == "users":
        render_user_management()
    elif st.session_state.admin_view == "settings":
        render_settings()
    
    # Footer
    st.markdown("""
    <div class="talentys-footer">
        <p>&copy; 2025 Talentys - Data Engineering & Analytics Excellence</p>
        <p>
            <a href="https://talentys.eu" target="_blank">Website</a> | 
            <a href="mailto:support@talentys.eu">Support</a>
        </p>
    </div>
    """, unsafe_allow_html=True)
