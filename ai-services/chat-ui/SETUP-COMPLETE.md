# 🎨 Talentys AI Agent - Complete Setup

## ✅ What's Been Created

### 1. **Enhanced Chat UI** (`app.py`)
- ✅ Talentys branding integrated
- ✅ Company logo in header
- ✅ Custom color scheme (#0066CC)
- ✅ Professional footer
- ✅ Smooth animations

### 2. **Admin Console** (`admin.py`) - **NEW!**
```
🔐 Login System
   ↓
🏠 Dashboard (Stats, Quick Actions)
   ↓
🎨 Theme Customization
   ├── Color Picker (Primary, Secondary, Accent)
   ├── Logo Configuration
   ├── Company Info
   └── Custom CSS Editor
   ↓
👥 User Management
   ├── List Users
   ├── Create New Users
   ├── Delete Users
   └── Change Passwords
   ↓
⚙️ Settings
   ├── AI Model Config
   ├── Integration URLs
   └── System Parameters
```

### 3. **Theme System** (`config/talentys_theme.py`)
```css
• 650+ lines of professional CSS
• Talentys color palette
• Gradient effects
• Smooth animations
• Responsive design
• Card layouts
• Button styles
• Form elements
```

### 4. **Authentication** (`config/auth.py`)
```python
• SHA-256 password hashing
• User credential management
• Session tokens
• Role-based access (admin/user)
• User CRUD operations
```

### 5. **Launch Script** (`launch-talentys-agent.ps1`)
```powershell
• Auto-install dependencies
• Start both services
• Health checks
• Interactive menu
• Easy management
```

### 6. **Documentation** (`README-ADMIN.md`)
- Complete usage guide
- Customization instructions
- Security best practices
- Troubleshooting tips

## 🚀 How to Use

### Step 1: Navigate to Directory
```powershell
cd c:\projets\dremiodbt\ai-services\chat-ui
```

### Step 2: Install Dependencies (First Time Only)
```powershell
pip install -r requirements-admin.txt
```

### Step 3: Launch Services
```powershell
.\launch-talentys-agent.ps1
```

### Step 4: Access Interfaces

#### 🤖 Chat UI (Port 8501)
- **URL**: http://localhost:8501
- **Purpose**: End-user chat interface
- **Features**:
  - AI-powered Q&A
  - Document upload
  - Source citations
  - Talentys branding

#### 🎨 Admin Console (Port 8502)
- **URL**: http://localhost:8502
- **Login**: `admin` / `talentys2025`
- **Purpose**: Management & customization
- **Features**:
  - Theme customization
  - User management
  - Settings configuration
  - System dashboard

## 🎨 Customization Examples

### Change Brand Colors
1. Open http://localhost:8502
2. Login (admin/talentys2025)
3. Navigate to **Theme** section
4. Use color pickers:
   - Primary: `#0066CC` → Your color
   - Secondary: `#003D7A` → Your color
   - Accent: `#00A8E8` → Your color
5. Click **Save**

### Change Logo
1. In Admin → **Theme**
2. Update "Logo URL":
   - Use your company URL
   - Or upload to `static/img/` folder
3. Logo appears in:
   - Header
   - Login page
   - Sidebar
   - Footer

### Add Custom CSS
1. In Admin → **Theme**
2. Scroll to **Custom CSS** section
3. Add your styles:
```css
.my-button {
    background: linear-gradient(135deg, #FF6B6B 0%, #FF8E8E 100%);
    color: white;
    padding: 1rem 2rem;
    border-radius: 10px;
}
```
4. Save and refresh

## 🔐 Security Features

### Authentication
- ✅ Secure login required for admin
- ✅ Password hashing (SHA-256)
- ✅ Session management
- ✅ Role-based access control

### User Management
- ✅ Create/delete users
- ✅ Password changes
- ✅ Admin protection (can't delete admin)
- ✅ Role assignment

### Best Practices
1. **Change default password immediately**
   ```
   Admin → Users → Change Password
   Old: talentys2025
   New: Your secure password
   ```

2. **Use strong passwords**
   - Minimum 8 characters
   - Mix of letters, numbers, symbols

3. **Regular backups**
   - Backup `config/users.json`
   - Store securely

## 📊 Features Matrix

| Feature | Chat UI | Admin Console |
|---------|:-------:|:-------------:|
| **Branding** |
| Talentys Colors | ✅ | ✅ |
| Company Logo | ✅ | ✅ |
| Custom CSS | ✅ | ✅ |
| **Functionality** |
| AI Chat | ✅ | ❌ |
| Document Upload | ✅ | ❌ |
| Theme Editor | ❌ | ✅ |
| User Management | ❌ | ✅ |
| **Security** |
| Login Required | ❌ | ✅ |
| Password Protected | ❌ | ✅ |
| Role-Based Access | ❌ | ✅ |

## 🎯 Use Cases

### For End Users
1. Open Chat UI (http://localhost:8501)
2. Ask questions about data
3. Upload documents
4. Get AI-powered answers

### For Administrators
1. Open Admin Console (http://localhost:8502)
2. Login with credentials
3. Customize branding:
   - Change colors to match your brand
   - Upload your logo
   - Modify company info
4. Manage users:
   - Create accounts for team
   - Set permissions
   - Reset passwords
5. Configure settings:
   - AI model selection
   - Temperature/top-k
   - Integration URLs

### For Developers
1. Modify `config/talentys_theme.py` for CSS
2. Extend `admin.py` with new features
3. Add custom authentication in `config/auth.py`
4. Integrate with existing systems

## 🌈 Talentys Design System

### Color Palette
```
Primary:   #0066CC  (Talentys Blue)
Secondary: #003D7A  (Dark Blue)
Accent:    #00A8E8  (Light Blue)
Success:   #28A745  (Green)
Warning:   #FFC107  (Amber)
Danger:    #DC3545  (Red)
Light:     #F8F9FA  (Light Gray)
Dark:      #212529  (Dark Gray)
```

### Typography
- Headers: Bold, gradient text
- Body: Readable, clean fonts
- Code: Monospace for technical content

### Layout
- Cards with shadows
- Rounded corners (12px)
- Smooth transitions
- Responsive design

## 🆘 Troubleshooting

### Services Won't Start
```powershell
# Check if ports are in use
netstat -ano | findstr "8501 8502"

# Kill existing processes
Get-NetTCPConnection -LocalPort 8501,8502 | Select -ExpandProperty OwningProcess | Stop-Process
```

### Login Not Working
1. Check if `config/users.json` exists
2. Try default credentials: `admin` / `talentys2025`
3. Delete `config/users.json` to reset

### Theme Not Applying
1. Hard refresh browser (Ctrl+F5)
2. Clear browser cache
3. Check console for CSS errors

### Import Errors
```powershell
# Reinstall dependencies
pip install -r requirements-admin.txt --force-reinstall
```

## 📚 File Reference

```
ai-services/chat-ui/
│
├── app.py                      # Main chat interface
├── admin.py                    # Admin console (NEW!)
├── launch-talentys-agent.ps1   # Launcher script (NEW!)
├── README-ADMIN.md             # This documentation (NEW!)
├── requirements-admin.txt      # Dependencies (NEW!)
│
├── config/
│   ├── __init__.py            # Package init (NEW!)
│   ├── talentys_theme.py      # 650+ lines CSS theme (NEW!)
│   ├── auth.py                # Authentication system (NEW!)
│   └── users.json             # User database (auto-created)
│
├── static/
│   ├── css/
│   ├── img/
│   └── js/
│
└── templates/
```

## 🎓 Next Steps

### Immediate
1. ✅ Launch the services
2. ✅ Login to admin console
3. ✅ Change default password
4. ✅ Customize theme with your branding

### Short-term
1. Create user accounts for team
2. Test all features
3. Customize CSS to match your brand
4. Add your company logo

### Long-term
1. Integrate with production systems
2. Add custom features
3. Deploy to production
4. Monitor and maintain

## 💡 Pro Tips

1. **Logo Best Practices**
   - Use PNG with transparent background
   - Recommended size: 200x50px
   - Keep file size < 100KB

2. **Color Selection**
   - Use your brand's primary color
   - Ensure good contrast for readability
   - Test on different screens

3. **User Management**
   - Create role-specific accounts
   - Use email addresses for usernames
   - Document password policies

4. **Performance**
   - Clear old chat sessions
   - Limit concurrent users initially
   - Monitor resource usage

## 🎉 Success!

You now have a **fully customizable AI agent** with:
- ✅ Professional Talentys branding
- ✅ Secure admin interface
- ✅ Complete theme customization
- ✅ User management system
- ✅ Easy deployment
- ✅ Comprehensive documentation

**Ready to make it yours!** 🚀

---

**Made with ❤️ by Talentys**  
Data Engineering & Analytics Excellence  
support@talentys.eu | https://talentys.eu
