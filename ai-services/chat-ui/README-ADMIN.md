# Talentys AI Agent - Customizable Interface

## 🎨 Features

### ✅ Implemented
- **Talentys Brand Design**: Corporate colors (#0066CC primary blue)
- **Custom Logo Integration**: Displays Talentys logo throughout interface
- **Professional Look & Feel**: Modern, clean UI with smooth animations
- **Admin Interface**: Complete management console with authentication
- **Secure Login System**: User authentication with session management
- **Theme Customization**: Full control over colors, logos, and styling
- **User Management**: Create, modify, and delete user accounts
- **Settings Panel**: Configure AI models and integrations
- **Responsive Design**: Works on desktop, tablet, and mobile

### 🎯 Components

#### 1. **Main Chat UI** (`app.py`)
- Enhanced with Talentys branding
- Company logo in header
- Custom color scheme
- Professional footer with company info
- Smooth animations and transitions

#### 2. **Admin Console** (`admin.py`)
- **Login Page**: Secure authentication
  - Default credentials: `admin` / `talentys2025`
  - Company-branded login form
  - Session management

- **Dashboard**: Overview and quick actions
  - System status cards
  - User statistics
  - Quick navigation

- **Theme Customization**: Full branding control
  - Color picker for primary/secondary/accent colors
  - Logo URL configuration
  - Company name and tagline
  - Custom CSS editor
  - Live preview

- **User Management**: Complete user control
  - List all users
  - Create new users
  - Delete users (except admin)
  - Change passwords
  - Role assignment (user/admin)

- **Settings**: AI model configuration
  - Default model selection
  - Temperature and top-k settings
  - Integration URLs
  - Max tokens configuration

#### 3. **Theme System** (`config/talentys_theme.py`)
- 650+ lines of professional CSS
- Talentys color palette
- Gradient effects
- Smooth animations
- Responsive breakpoints
- Card layouts
- Button styles
- Form elements
- Alert components

#### 4. **Authentication** (`config/auth.py`)
- Secure password hashing (SHA-256)
- User credential management
- Session token generation
- Role-based access control
- User CRUD operations

## 🚀 Quick Start

### 1. Install Dependencies
```bash
cd ai-services/chat-ui
pip install -r requirements-admin.txt
```

### 2. Start Main Chat UI (Port 8501)
```bash
streamlit run app.py --server.port 8501
```

### 3. Start Admin Console (Port 8502)
```bash
streamlit run admin.py --server.port 8502
```

### 4. Access Interfaces
- **Chat UI**: http://localhost:8501
- **Admin Console**: http://localhost:8502

### 5. Login to Admin
- **Username**: `admin`
- **Password**: `talentys2025`

## 🎨 Customization Guide

### Change Brand Colors
1. Open Admin Console (http://localhost:8502)
2. Login with admin credentials
3. Go to **Theme** section
4. Use color pickers to select your colors:
   - **Primary**: Main brand color
   - **Secondary**: Complementary color  
   - **Accent**: Highlight color
5. Click **Save Theme Configuration**

### Change Logo
1. Go to Admin Console → **Theme**
2. Update **Logo URL** with your logo
3. Supports:
   - Direct URLs: `https://yourcompany.com/logo.png`
   - Local files: Place in `static/img/` folder
4. Logo automatically displays in:
   - Header
   - Login page
   - Sidebar
   - Footer

### Add Custom CSS
1. Go to Admin Console → **Theme**
2. Scroll to **Custom CSS** section
3. Add your CSS rules:
```css
.my-custom-class {
    background: #FF6B6B;
    color: white;
    padding: 1rem;
}
```
4. Save configuration

### Create New Users
1. Go to Admin Console → **Users**
2. Click **Add User** tab
3. Fill in details:
   - Username
   - Email
   - Password
   - Role (user/admin)
4. Click **Create User**

## 🔐 Security

### Change Default Password
**IMPORTANT**: Change default admin password immediately!

1. Login to Admin Console
2. Go to **Users** → **Change Password** tab
3. Enter current password: `talentys2025`
4. Enter new secure password
5. Confirm and save

### Password Requirements
- Minimum 8 characters
- Use strong passwords in production
- Stored as SHA-256 hashes

### User Roles
- **admin**: Full access to all features
- **user**: Limited access (can use chat, cannot access admin)

## 📁 File Structure

```
ai-services/chat-ui/
├── app.py                    # Main chat interface (port 8501)
├── admin.py                  # Admin console (port 8502)
├── requirements-admin.txt    # Python dependencies
├── config/
│   ├── __init__.py
│   ├── talentys_theme.py    # Theme system & CSS
│   ├── auth.py              # Authentication system
│   └── users.json           # User database (auto-created)
├── static/
│   ├── css/
│   │   └── custom.css       # Additional styles
│   ├── img/
│   │   └── talentys-logo.png
│   └── js/
│       └── custom.js
└── templates/
    └── (future HTML templates)
```

## 🎯 Usage Examples

### For End Users (Chat UI)
1. Open http://localhost:8501
2. See Talentys-branded interface
3. Ask questions or upload documents
4. View sources and AI responses

### For Administrators
1. Open http://localhost:8502
2. Login with credentials
3. Customize theme to match your brand
4. Manage users and permissions
5. Configure AI model settings
6. Monitor system status

## 🌈 Talentys Color Palette

```css
Primary: #0066CC   (Talentys Blue)
Secondary: #003D7A (Dark Blue)
Accent: #00A8E8    (Light Blue)
Success: #28A745   (Green)
Warning: #FFC107   (Amber)
Danger: #DC3545    (Red)
Light: #F8F9FA     (Light Gray)
Dark: #212529      (Dark Gray)
```

## 🔧 Configuration

### Environment Variables
```bash
# .env file
RAG_API_URL=http://rag-api:8002
SESSION_SECRET=your-secret-key-here
SESSION_DURATION_HOURS=8
```

### Theme Configuration
Edit `config/talentys_theme.py` to change:
- Brand colors
- Logo URLs
- Company information
- CSS styles

### Authentication Configuration
Edit `config/auth.py` to change:
- Password hashing method
- Session duration
- User roles

## 📊 Features Comparison

| Feature | Chat UI | Admin Console |
|---------|---------|---------------|
| Talentys Branding | ✅ | ✅ |
| AI Chat | ✅ | ❌ |
| Document Upload | ✅ | ❌ |
| Login Required | ❌ | ✅ |
| Theme Customization | ❌ | ✅ |
| User Management | ❌ | ✅ |
| Settings Management | ❌ | ✅ |
| Statistics Dashboard | ❌ | ✅ |

## 🚀 Production Deployment

### Docker Deployment
```yaml
version: '3.8'
services:
  chat-ui:
    build: ./ai-services/chat-ui
    ports:
      - "8501:8501"
    environment:
      - RAG_API_URL=http://rag-api:8002
    volumes:
      - ./ai-services/chat-ui/config:/app/config
    command: streamlit run app.py --server.port 8501
  
  admin-ui:
    build: ./ai-services/chat-ui
    ports:
      - "8502:8502"
    environment:
      - SESSION_SECRET=${SESSION_SECRET}
    volumes:
      - ./ai-services/chat-ui/config:/app/config
    command: streamlit run admin.py --server.port 8502
```

### Security Checklist
- [ ] Change default admin password
- [ ] Set strong SESSION_SECRET
- [ ] Use HTTPS in production
- [ ] Enable firewall rules
- [ ] Regular security updates
- [ ] Backup user database
- [ ] Monitor access logs

## 💡 Tips & Best Practices

1. **Logo Format**: Use PNG with transparent background
2. **Logo Size**: Recommended 200x50px for best results
3. **Colors**: Use hex codes for consistency
4. **CSS**: Test custom CSS in preview before saving
5. **Users**: Create separate accounts for team members
6. **Backup**: Regularly backup `config/users.json`
7. **Updates**: Keep dependencies up to date

## 🆘 Support

Need help?
- **Email**: support@talentys.eu
- **Website**: https://talentys.eu
- **Documentation**: This file!

## 📝 Changelog

### v2.0 (Current)
- ✅ Complete admin interface
- ✅ Talentys branding integration
- ✅ User authentication system
- ✅ Theme customization
- ✅ 650+ lines of custom CSS
- ✅ Responsive design

### v1.0
- Basic chat interface
- Document upload
- RAG integration

---

**Made with ❤️ by Talentys - Data Engineering & Analytics Excellence**
