# �� KICKAI - AI-Powered Football Team Management

KICKAI is a comprehensive football team management system that integrates Telegram bots, Supabase backend, and AI agents to streamline team operations.

## ✨ Features

### 🤖 **Telegram Bot Integration**
- **Dual-chat architecture**: Leadership group + Main team group
- **Role-based command system**: Admin, Captain, Secretary, Manager, Player
- **Natural language processing**: Players can use natural language for availability and payments
- **Smart command validation**: Comprehensive input validation and error handling

### 📅 **Fixture Management** *(NEW)*
- **Create fixtures**: `/newfixture` with smart validation
- **List fixtures**: `/listfixtures` with filtering (upcoming/past/all)
- **Automatic announcements**: Dual-chat announcements from leadership to main team
- **Flexible input formats**: Multiple date/time format support
- **Comprehensive validation**: Missing field detection and helpful error messages

### 🗄️ **Database Management**
- **Supabase integration**: Real-time database with Row Level Security
- **Complete schema**: Teams, members, bots, fixtures, command logs
- **Performance optimized**: Proper indexing and relationships
- **Sample data included**: Ready-to-use test data

### 🤖 **AI Integration**
- **CrewAI agents**: AI-powered team management
- **Google Gemini**: Production-ready AI model
- **Hybrid configuration**: Local development + Production deployment
- **Natural language processing**: Smart command interpretation

## 🚀 Quick Start

### 1. **Database Setup**
Run the complete database setup script in your Supabase SQL Editor:
```sql
-- Copy and paste setup_database.sql
```

### 2. **Environment Variables**
Create a `.env` file with:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
TELEGRAM_BOT_TOKEN=your_bot_token
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=dummy_key_for_crewai
```

### 3. **Deploy to Railway**
```bash
git push origin main
# Railway will auto-deploy from GitHub
```

### 4. **Test Commands**
In your **Leadership Telegram chat**:
```
/newfixture Thunder FC 2024-07-15 14:00 "Home - Central Park"
/listfixtures
/help
/status
```

## 📋 Available Commands

### **Fixture Management**
- `/newfixture` - Create new fixture with validation
- `/listfixtures` - List fixtures with filtering
- `/deletefixture` - Delete fixture (coming soon)
- `/updatefixture` - Update fixture (coming soon)

### **Team Management**
- `/addmember` - Add team member (coming soon)
- `/listmembers` - List team members (coming soon)
- `/updaterole` - Update member role (coming soon)

### **Help & Status**
- `/help` - Show available commands
- `/status` - Show team status

## 🏗️ Architecture

### **Dual-Chat System**
- **Leadership Chat**: Admin commands, fixture management, team operations
- **Main Team Chat**: Natural language, player interactions, announcements

### **Database Schema**
- **teams**: Team information
- **team_members**: Member roles and contact info
- **team_bots**: Bot configuration and chat mapping
- **fixtures**: Match scheduling and details
- **command_logs**: Audit trail for all commands

### **AI Integration**
- **CrewAI**: Multi-agent system for team management
- **Google Gemini**: Production AI model
- **Natural Language**: Smart command interpretation

## 🔧 Development

### **Local Development**
```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python run_telegram_bot.py
```

### **Database Validation**
The system includes comprehensive database validation and error handling.

### **Testing**
- **Command validation**: All inputs are validated
- **Error handling**: Graceful error messages
- **Dual-chat testing**: Verify announcements work
- **Role-based access**: Test permission system

## 📊 Current Status

### ✅ **Implemented & Working**
- Complete fixture management system
- Dual-chat Telegram bot architecture
- Supabase database integration
- Role-based command system
- Natural language processing
- Comprehensive error handling
- Railway deployment ready

### 🚧 **Coming Soon**
- Availability management
- Squad selection
- Payment integration
- Member management
- Advanced AI features

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Check the documentation in the `/docs` folder
- Review the testing guides
- Check Railway deployment logs

---

**KICKAI** - Making football team management smarter with AI! ⚽🤖
