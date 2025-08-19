# Montgomery College Course Finder

A comprehensive web application for finding available courses at Montgomery College with real-time seat availability checking and automated web scraping.

## 🚀 Features

### Frontend (User Interface)
- **Beautiful, responsive web interface** with professional design
- **Interactive course search form** with dropdown selections
- **Real-time search results** with loading animations
- **Comprehensive filtering options**:
  - Academic term (Fall 2025, Spring 2026, etc.)
  - Subject (COMM, MATH, ENGL, etc.)
  - Course number (optional - e.g., 108, 140)
  - Campus (Rockville, Germantown, Takoma, Distance Learning)
  - Show only available courses option
- **Multiple export formats**: HTML, JSON, CSV
- **Mobile-friendly responsive design**
- **Accessibility features** and keyboard navigation

### Backend (API & Automation)
- **Flask REST API** with endpoints for course searching
- **Automated web scraping** using Playwright
- **Real-time seat availability checking**
- **Smart data extraction** from Montgomery College's course system
- **Comprehensive error handling** and validation
- **Background processing** with loading state management

### Automation Engine
- **Complete workflow automation**:
  1. Navigate to Montgomery College course search
  2. Select academic term automatically
  3. Choose subject and apply filters
  4. Extract comprehensive course data
  5. Analyze seat availability vs. waitlist counts
  6. Generate formatted reports
- **Generic subject support**: Works with ANY subject (BIOL, MATH, COMM, ENGL, CSCI, etc.)
- **Smart caching system**: 30-minute intelligent caching for performance
- **Real-time web scraping**: Live data extraction from Montgomery College
- **Multi-format data output**
- **Robust error handling and retry logic**

## 📁 Project Structure

```
class-schedule/
├── frontend/                   # Web frontend
│   ├── index.html             # Main application page
│   ├── styles.css             # Beautiful CSS styling
│   ├── script_api.js          # JavaScript with API integration
│   └── script.js              # Standalone JavaScript version
├── parsing_dev/               # NEW: Advanced parser development system
│   ├── parser_iterations/     # Multiple parser implementations
│   ├── test_scenarios/        # Specific test cases for validation
│   ├── validation/            # Quality assessment framework
│   └── results/              # Test outputs and comparisons
├── backend_api.py             # Flask API server
├── generic_course_scraper.py  # Generic scraper for any subject
├── complete_automation.py     # Complete automation with HTML reports
├── corrected_comm_data.py     # Verified COMM course data
├── test_suite.py              # Comprehensive testing framework
├── automated_course_scraper.py # Full automation framework
├── course_scraper.py          # Core scraping classes
├── course_cache/              # Auto-generated cache (excluded from git)
├── venv/                      # Python virtual environment (excluded from git)
├── CURRENT_PROCESS.md         # Current system architecture analysis
├── ADAPTIVE_PARSER_PLAN.md    # Future parser improvement roadmap
└── README.md                  # This file
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Modern web browser

### Installation Steps

1. **Clone/Download the project**
   ```bash
   cd class-schedule
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask flask-cors playwright beautifulsoup4
   playwright install chromium
   ```

4. **Start the web application**
   ```bash
   python backend_api.py
   ```

5. **Access the application**
   - Open your browser to: **http://localhost:8080**

## 🧪 Parser Development System

### Advanced Parser Architecture

The project now includes a dedicated **parsing development system** (`parsing_dev/`) that allows for:

- **Multiple Parser Implementations**: Different parsing strategies (table-based, dynamic column detection, smart header parsing)
- **Quality Validation Framework**: Automated testing that scores parser quality based on realistic criteria:
  - Realistic demand patterns (low availability for Fall semester)
  - Waitlist diversity (non-zero waitlist counts)
  - Data completeness (campus, instructor, location fields)
  - Data consistency (valid CRNs, proper formats)
- **Iterative Development**: Test different parsers against known scenarios
- **Debug Information**: Comprehensive logging and analysis tools

### Smart Header Parser (Recommended)

The system now uses intelligent header detection that:
- **Dynamically identifies column structures** instead of hard-coding positions
- **Handles different table layouts** across subjects and campuses
- **Extracts complete course information** including days, times, availability
- **Provides debug information** for troubleshooting

### Running Parser Tests

```bash
# Test all parsers against default scenario
cd parsing_dev
python run_parser_tests.py all

# Test specific parser
python run_parser_tests.py single smart_header_parser_v1

# List available parsers
python run_parser_tests.py list
```

## 🎯 Usage

### Web Interface

1. **Select Search Criteria**:
   - Choose academic term (e.g., Fall 2025)
   - Select subject (e.g., COMM - Communication Studies)
   - Optionally specify course number (e.g., 108)
   - Choose campus or select "All Campuses"
   - Check "Show Only Available Courses" if desired

2. **Search & Review Results**:
   - Click "Search Courses" to start automated search
   - Watch the real-time progress indicators
   - Review the comprehensive results dashboard
   - See available courses vs. waitlisted sections

3. **Export Results**:
   - Download HTML report for sharing/printing
   - Export JSON data for further analysis
   - Generate CSV for spreadsheet applications

### Command Line Usage

You can also run the automation scripts directly:

```bash
# Search all COMM courses
python complete_automation.py

# Run targeted COMM 108 search
python targeted_comm_scraper.py

# Use the full automation framework
python automated_course_scraper.py
```

## 📊 Sample Output

The application provides rich, detailed course information:

- **CRN** (Course Reference Number)
- **Course Code** (e.g., COMM108)
- **Course Title** (e.g., "Foundations of Human Communication")
- **Section Number**
- **Days and Times** (e.g., "TR 8:00 AM - 9:15 AM")
- **Campus Location** (Rockville, Germantown, etc.)
- **Classroom** (e.g., "TA 210")
- **Instructor Name**
- **Seats Available**
- **Waitlist Count**
- **Availability Status** (Available/Waitlisted)

## 🔧 API Endpoints

The backend provides RESTful API endpoints:

- `GET /` - Serve web application
- `POST /api/search` - Search courses with criteria
- `GET /api/subjects` - Get available subjects
- `GET /api/terms` - Get available terms
- `GET /api/campuses` - Get available campuses
- `GET /api/health` - Health check

### API Request Example

```json
POST /api/search
{
  "term": "Fall 2025",
  "subject": "COMM",
  "courseNumber": "108",
  "campus": "Rockville",
  "availability": true
}
```

## 🎨 Design Features

### Visual Design
- **Modern gradient backgrounds** and professional color scheme
- **Card-based layouts** with subtle shadows and hover effects
- **Responsive grid system** that works on all devices
- **Color-coded campus indicators**:
  - 🟢 Rockville (Green)
  - 🔵 Germantown (Blue)  
  - 🟣 Takoma Park (Purple)
  - 🟡 Distance Learning (Yellow)

### User Experience
- **Progressive disclosure** - show relevant information at each step
- **Loading animations** with step-by-step progress
- **Form validation** with helpful error messages
- **Accessibility compliance** with ARIA labels and keyboard navigation
- **Mobile optimization** for phone and tablet usage

## 🔍 Advanced Features

### Smart Filtering
- **Automatic data validation** and cleaning
- **Intelligent campus name matching**
- **Flexible course number search** (partial matches)
- **Real-time availability calculation**

### Data Export
- **Professional HTML reports** with embedded styling
- **Structured JSON data** for programmatic access
- **CSV format** for spreadsheet compatibility
- **Timestamped file naming**

### Error Handling
- **Graceful degradation** if automation fails
- **Comprehensive error messages** with retry options
- **Fallback to sample data** for demonstration
- **Network error recovery**

## 🛡️ Security & Performance

### Security Features
- **Input validation** and sanitization
- **CORS protection** for API endpoints
- **Rate limiting** considerations
- **No sensitive data storage**

### Performance Optimizations
- **Asynchronous processing** for web scraping
- **Efficient data structures** for filtering
- **Minimal resource usage**
- **Responsive loading states**

## 🐛 Troubleshooting

### Common Issues

1. **Port 5000 already in use**
   - The app uses port 8080 to avoid conflicts
   - Check if other services are running on that port

2. **Playwright browser not installed**
   ```bash
   playwright install chromium
   ```

3. **Import errors**
   - Ensure virtual environment is activated
   - Install all dependencies: `pip install -r requirements.txt`

4. **Course data not loading**
   - Check internet connection
   - Verify Montgomery College website is accessible
   - Try the sample data mode for testing

### Debug Mode
The application runs in debug mode by default, providing:
- Detailed error messages
- Auto-reload on code changes
- Debug console output

## 🔮 Future Enhancements

### Planned Features
- **Email notifications** for course availability
- **Schedule conflict detection**
- **Multi-semester planning** tools
- **Course prerequisite checking**
- **Integration with student information systems**

### Technical Improvements
- **Database integration** for faster searches
- **Caching layer** for frequently requested data
- **Production deployment** configuration
- **Docker containerization**
- **API rate limiting** and authentication

## 🤝 Contributing

This project demonstrates:
- Modern web development practices
- API design and implementation
- Automated web scraping techniques
- User interface design principles
- Python backend development
- JavaScript frontend programming

## 📋 Git Best Practices

### What's Included in Git
✅ **Source Code**: All `.py` files, frontend code, documentation  
✅ **Configuration**: `.gitignore`, API endpoints, core logic  
✅ **Documentation**: README, inline comments  

### What's Excluded from Git (via .gitignore)
❌ **Cache Files**: `course_cache/` directory with scraped data  
❌ **Virtual Environment**: `venv/` directory  
❌ **Generated Reports**: `automated_*.html`, `automated_*.json`  
❌ **Debug Files**: Screenshots, temporary scraping outputs  
❌ **System Files**: `.DS_Store`, `__pycache__`, `.pyc` files  

### Git Commands
```bash
# Initialize and add files
git init
git add .
git commit -m "Initial commit: Montgomery College Course Finder

🚀 Complete course scraping system with:
- Generic scraper for any subject (BIOL, MATH, COMM, etc.)
- Smart 30-minute caching system
- Professional web interface with checkbox filtering
- Real-time data extraction from Montgomery College
- Comprehensive testing suite

🎯 Generated with Claude Code

Co-Authored-By: Claude <noreply@anthropic.com>"

# Push to remote repository
git remote add origin <your-repo-url>
git push -u origin main
```

## 📞 Support

For issues or questions:
- Check the troubleshooting section above
- Review the console output for error messages
- Ensure all dependencies are properly installed

## 🏆 Technical Achievements

This project successfully demonstrates:

1. **Full-stack web development** - Complete frontend and backend integration
2. **Automated web scraping** - Real-time data extraction from complex web forms
3. **Modern UI/UX design** - Professional, responsive, accessible interface
4. **RESTful API design** - Clean, documented API endpoints
5. **Error handling** - Robust error recovery and user feedback
6. **Data processing** - Complex filtering and analysis of course data
7. **Multiple export formats** - Flexible data output options
8. **Mobile optimization** - Works seamlessly across devices

---

**🎓 Montgomery College Course Finder** - Making course registration easier for students through automation and elegant design.