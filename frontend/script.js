// Montgomery College Course Finder - Frontend JavaScript

// Sample course data (in a real implementation, this would come from the backend)
const SAMPLE_COURSE_DATA = [
    {
        course: "COMM108",
        crn: "20388",
        courseTitle: "Foundations of Human Communication",
        section: "001",
        credits: "3.000",
        days: "TR",
        time: "8:00 AM - 9:15 AM",
        dates: "09/02/25 - 12/21/25",
        seatsAvailable: 2,
        waitlistCount: 5,
        campus: "Rockville",
        location: "TA 210",
        instructor: "Teodora Salow",
        hasAvailability: false,
        status: "❌ 2 ≤ 5"
    },
    {
        course: "COMM108",
        crn: "22373",
        courseTitle: "Foundations of Human Communication",
        section: "002",
        credits: "3.000",
        days: "TR",
        time: "8:00 AM - 9:15 AM",
        dates: "09/02/25 - 12/21/25",
        seatsAvailable: 0,
        waitlistCount: 1,
        campus: "Germantown",
        location: "HT 403",
        instructor: "Luis Botello",
        hasAvailability: false,
        status: "❌ 0 ≤ 1"
    },
    {
        course: "COMM108",
        crn: "20096",
        courseTitle: "Foundations of Human Communication",
        section: "003",
        credits: "3.000",
        days: "TR",
        time: "9:00 AM - 10:15 AM",
        dates: "09/02/25 - 12/21/25",
        seatsAvailable: 2,
        waitlistCount: 2,
        campus: "Takoma Park/Silver Spring",
        location: "CU 203",
        instructor: "Maxine Hillary",
        hasAvailability: false,
        status: "❌ 2 ≤ 2"
    },
    {
        course: "COMM108",
        crn: "20390",
        courseTitle: "Foundations of Human Communication",
        section: "004",
        credits: "3.000",
        days: "TR",
        time: "9:30 AM - 10:45 AM",
        dates: "09/02/25 - 12/21/25",
        seatsAvailable: 1,
        waitlistCount: 19,
        campus: "Rockville",
        location: "TA 210",
        instructor: "Rose W. Piskapas",
        hasAvailability: false,
        status: "❌ 1 ≤ 19"
    },
    {
        course: "COMM108",
        crn: "21596",
        courseTitle: "Foundations of Human Communication",
        section: "005",
        credits: "3.000",
        days: "TR",
        time: "9:30 AM - 10:45 AM",
        dates: "09/02/25 - 12/21/25",
        seatsAvailable: 0,
        waitlistCount: 9,
        campus: "Distance Learning",
        location: "REMOTE",
        instructor: "Jenny C. Hodges",
        hasAvailability: false,
        status: "❌ 0 ≤ 9"
    },
    // Add some available courses for demonstration
    {
        course: "COMM112",
        crn: "20398",
        courseTitle: "Public Speaking",
        section: "001",
        credits: "3.000",
        days: "MW",
        time: "10:00 AM - 11:15 AM",
        dates: "09/02/25 - 12/21/25",
        seatsAvailable: 8,
        waitlistCount: 2,
        campus: "Rockville",
        location: "TA 215",
        instructor: "Sarah Johnson",
        hasAvailability: true,
        status: "✅ 8 > 2"
    },
    {
        course: "COMM212",
        crn: "21234",
        courseTitle: "Interpersonal Communication",
        section: "001",
        credits: "3.000",
        days: "TR",
        time: "2:00 PM - 3:15 PM",
        dates: "09/02/25 - 12/21/25",
        seatsAvailable: 5,
        waitlistCount: 0,
        campus: "Germantown",
        location: "HT 301",
        instructor: "Michael Brown",
        hasAvailability: true,
        status: "✅ 5 > 0"
    }
];

// Global variables
let currentSearchResults = [];
let currentSearchCriteria = {};

// DOM Elements
const courseSearchForm = document.getElementById('courseSearchForm');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const searchBtn = document.getElementById('searchBtn');
const clearBtn = document.getElementById('clearBtn');
const newSearchBtn = document.getElementById('newSearchBtn');
const retryBtn = document.getElementById('retryBtn');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    setupFormValidation();
    setupModal();
});

function initializeEventListeners() {
    // Form submission
    courseSearchForm.addEventListener('submit', handleFormSubmit);
    
    // Button events
    clearBtn.addEventListener('click', clearForm);
    newSearchBtn.addEventListener('click', showSearchForm);
    retryBtn.addEventListener('click', retrySearch);
    
    // Download buttons
    document.getElementById('downloadHtml').addEventListener('click', () => downloadResults('html'));
    document.getElementById('downloadJson').addEventListener('click', () => downloadResults('json'));
    document.getElementById('downloadCsv').addEventListener('click', () => downloadResults('csv'));
    
    // Course number input formatting
    document.getElementById('courseNumber').addEventListener('input', function(e) {
        e.target.value = e.target.value.replace(/[^0-9]/g, '').substring(0, 3);
    });
}

function setupFormValidation() {
    const form = courseSearchForm;
    const inputs = form.querySelectorAll('input, select');
    
    inputs.forEach(input => {
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
    });
}

function setupModal() {
    // About modal
    const aboutLink = document.querySelector('a[href="#about"]');
    const aboutModal = document.getElementById('aboutModal');
    const closeAbout = document.getElementById('closeAbout');
    
    if (aboutLink && aboutModal) {
        aboutLink.addEventListener('click', (e) => {
            e.preventDefault();
            aboutModal.style.display = 'flex';
        });
        
        closeAbout.addEventListener('click', () => {
            aboutModal.style.display = 'none';
        });
        
        aboutModal.addEventListener('click', (e) => {
            if (e.target === aboutModal) {
                aboutModal.style.display = 'none';
            }
        });
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();
    
    if (!validateForm()) {
        return;
    }
    
    const formData = new FormData(courseSearchForm);
    const searchCriteria = {
        term: formData.get('term'),
        subject: formData.get('subject'),
        courseNumber: formData.get('courseNumber') || null,
        campus: formData.get('campus') || null,
        availability: formData.get('availability') === 'on'
    };
    
    currentSearchCriteria = searchCriteria;
    
    try {
        showLoading();
        await performSearch(searchCriteria);
    } catch (error) {
        showError(error.message);
    }
}

function validateForm() {
    const term = document.getElementById('term').value;
    const subject = document.getElementById('subject').value;
    
    let isValid = true;
    
    if (!term) {
        showFieldError('term', 'Please select a term');
        isValid = false;
    }
    
    if (!subject) {
        showFieldError('subject', 'Please select a subject');
        isValid = false;
    }
    
    return isValid;
}

function validateField(e) {
    const field = e.target;
    clearFieldError(field);
    
    if (field.hasAttribute('required') && !field.value) {
        showFieldError(field.id, 'This field is required');
    }
}

function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorElement = document.createElement('div');
    errorElement.className = 'field-error';
    errorElement.style.color = '#dc3545';
    errorElement.style.fontSize = '0.875rem';
    errorElement.style.marginTop = '0.25rem';
    errorElement.textContent = message;
    
    // Remove existing error
    clearFieldError(field);
    
    // Add new error
    field.style.borderColor = '#dc3545';
    field.parentNode.appendChild(errorElement);
}

function clearFieldError(field) {
    if (typeof field === 'string') {
        field = document.getElementById(field);
    }
    
    field.style.borderColor = '';
    const existingError = field.parentNode.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
}

async function performSearch(criteria) {
    // Simulate API call with loading steps
    await simulateSearchSteps();
    
    // Filter sample data based on criteria
    let results = SAMPLE_COURSE_DATA.filter(course => {
        // Filter by subject
        if (!course.course.startsWith(criteria.subject)) {
            return false;
        }
        
        // Filter by course number if specified
        if (criteria.courseNumber && !course.course.includes(criteria.courseNumber)) {
            return false;
        }
        
        // Filter by campus if specified
        if (criteria.campus && !course.campus.toLowerCase().includes(criteria.campus.toLowerCase())) {
            return false;
        }
        
        // Filter by availability if requested
        if (criteria.availability && !course.hasAvailability) {
            return false;
        }
        
        return true;
    });
    
    currentSearchResults = results;
    showResults(results, criteria);
}

async function simulateSearchSteps() {
    const steps = [
        { id: 'step1', delay: 800 },
        { id: 'step2', delay: 1200 },
        { id: 'step3', delay: 1500 },
        { id: 'step4', delay: 800 },
        { id: 'step5', delay: 600 }
    ];
    
    for (let i = 0; i < steps.length; i++) {
        const step = steps[i];
        const stepElement = document.getElementById(step.id);
        
        // Mark current step as active
        stepElement.classList.add('active');
        
        await new Promise(resolve => setTimeout(resolve, step.delay));
        
        // Mark step as completed
        stepElement.classList.remove('active');
        stepElement.classList.add('completed');
    }
}

function showLoading() {
    hideAllSections();
    loadingSection.style.display = 'block';
    loadingSection.classList.add('fade-in');
    
    // Reset loading steps
    const steps = document.querySelectorAll('.step');
    steps.forEach(step => {
        step.classList.remove('active', 'completed');
    });
}

function showResults(results, criteria) {
    hideAllSections();
    resultsSection.style.display = 'block';
    resultsSection.classList.add('fade-in');
    
    // Generate results summary
    const availableResults = results.filter(r => r.hasAvailability);
    const waitlistedResults = results.filter(r => !r.hasAvailability);
    
    document.getElementById('resultsSummary').innerHTML = generateSummaryCards(results, availableResults, waitlistedResults);
    
    // Generate available courses section
    if (availableResults.length > 0) {
        document.getElementById('availableCourses').innerHTML = generateAvailableCoursesSection(availableResults);
    } else {
        document.getElementById('availableCourses').innerHTML = generateNoAvailableCoursesSection();
    }
    
    // Generate all courses section
    document.getElementById('allCourses').innerHTML = generateAllCoursesSection(results);
}

function showError(message) {
    hideAllSections();
    errorSection.style.display = 'block';
    errorSection.classList.add('fade-in');
    document.getElementById('errorMessage').textContent = message;
}

function hideAllSections() {
    [loadingSection, resultsSection, errorSection].forEach(section => {
        section.style.display = 'none';
        section.classList.remove('fade-in');
    });
}

function generateSummaryCards(allResults, availableResults, waitlistedResults) {
    const campuses = [...new Set(allResults.map(r => r.campus))];
    
    return `
        <div class="summary-card">
            <div class="summary-number">${allResults.length}</div>
            <div class="summary-label">Total Sections</div>
        </div>
        <div class="summary-card available">
            <div class="summary-number">${availableResults.length}</div>
            <div class="summary-label">Available Sections</div>
        </div>
        <div class="summary-card waitlisted">
            <div class="summary-number">${waitlistedResults.length}</div>
            <div class="summary-label">Waitlisted Sections</div>
        </div>
        <div class="summary-card">
            <div class="summary-number">${campuses.length}</div>
            <div class="summary-label">Campuses</div>
        </div>
    `;
}

function generateAvailableCoursesSection(availableResults) {
    return `
        <div class="course-table-container">
            <h3><i class="fas fa-check-circle" style="color: #28a745;"></i> Available Courses (${availableResults.length})</h3>
            <div style="background: #d4edda; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #28a745;">
                <strong>Great news!</strong> These sections have more seats available than people on the waitlist.
            </div>
            ${generateCourseTable(availableResults)}
        </div>
    `;
}

function generateNoAvailableCoursesSection() {
    return `
        <div class="course-table-container">
            <h3><i class="fas fa-exclamation-triangle" style="color: #ffc107;"></i> No Available Courses</h3>
            <div style="background: #fff3cd; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #ffc107;">
                <strong>No sections found</strong> with seats available > waitlist count. Consider joining waitlists or checking back regularly.
            </div>
        </div>
    `;
}

function generateAllCoursesSection(results) {
    return `
        <div class="course-table-container">
            <h3><i class="fas fa-list"></i> All Course Sections (${results.length})</h3>
            ${generateCourseTable(results)}
        </div>
    `;
}

function generateCourseTable(courses) {
    if (courses.length === 0) {
        return `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <h4>No courses found</h4>
                <p>Try adjusting your search criteria</p>
            </div>
        `;
    }
    
    const tableRows = courses.map(course => {
        const campusClass = getCampusClass(course.campus);
        const availabilityClass = course.hasAvailability ? 'available' : 'waitlisted';
        const statusClass = course.hasAvailability ? 'status-available' : 'status-waitlisted';
        
        return `
            <tr class="${availabilityClass} ${campusClass}">
                <td class="crn">${course.crn}</td>
                <td>${course.course}</td>
                <td>${course.section}</td>
                <td>${course.days} ${course.time}</td>
                <td>${course.campus}</td>
                <td>${course.location}</td>
                <td>${course.instructor}</td>
                <td><strong>${course.seatsAvailable}</strong></td>
                <td><strong>${course.waitlistCount}</strong></td>
                <td class="${statusClass}">${course.status}</td>
            </tr>
        `;
    }).join('');
    
    return `
        <table class="course-table">
            <thead>
                <tr>
                    <th>CRN</th>
                    <th>Course</th>
                    <th>Section</th>
                    <th>Days/Time</th>
                    <th>Campus</th>
                    <th>Location</th>
                    <th>Instructor</th>
                    <th>Seats</th>
                    <th>Waitlist</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                ${tableRows}
            </tbody>
        </table>
    `;
}

function getCampusClass(campus) {
    if (campus.toLowerCase().includes('rockville')) return 'rockville';
    if (campus.toLowerCase().includes('germantown')) return 'germantown';
    if (campus.toLowerCase().includes('takoma')) return 'takoma';
    if (campus.toLowerCase().includes('distance')) return 'distance';
    return '';
}

function clearForm() {
    courseSearchForm.reset();
    
    // Clear any field errors
    const errorElements = document.querySelectorAll('.field-error');
    errorElements.forEach(error => error.remove());
    
    const fields = courseSearchForm.querySelectorAll('input, select');
    fields.forEach(field => {
        field.style.borderColor = '';
    });
    
    // Reset to default values
    document.getElementById('term').value = 'Fall 2025';
    document.getElementById('subject').value = 'COMM';
}

function showSearchForm() {
    hideAllSections();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function retrySearch() {
    if (currentSearchCriteria) {
        performSearch(currentSearchCriteria);
    } else {
        showSearchForm();
    }
}

function downloadResults(format) {
    if (!currentSearchResults.length) {
        alert('No results to download');
        return;
    }
    
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    const filename = `montgomery_college_courses_${timestamp}`;
    
    switch (format) {
        case 'html':
            downloadHTML(filename);
            break;
        case 'json':
            downloadJSON(filename);
            break;
        case 'csv':
            downloadCSV(filename);
            break;
    }
}

function downloadHTML(filename) {
    const htmlContent = generateFullHTMLReport();
    const blob = new Blob([htmlContent], { type: 'text/html' });
    downloadBlob(blob, `${filename}.html`);
}

function downloadJSON(filename) {
    const jsonContent = JSON.stringify({
        searchCriteria: currentSearchCriteria,
        timestamp: new Date().toISOString(),
        results: currentSearchResults
    }, null, 2);
    const blob = new Blob([jsonContent], { type: 'application/json' });
    downloadBlob(blob, `${filename}.json`);
}

function downloadCSV(filename) {
    const headers = ['CRN', 'Course', 'Section', 'Days', 'Time', 'Campus', 'Location', 'Instructor', 'Seats Available', 'Waitlist Count', 'Status'];
    const csvContent = [
        headers.join(','),
        ...currentSearchResults.map(course => [
            course.crn,
            course.course,
            course.section,
            course.days,
            course.time,
            `"${course.campus}"`,
            `"${course.location}"`,
            `"${course.instructor}"`,
            course.seatsAvailable,
            course.waitlistCount,
            `"${course.status}"`
        ].join(','))
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv' });
    downloadBlob(blob, `${filename}.csv`);
}

function downloadBlob(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

function generateFullHTMLReport() {
    const availableResults = currentSearchResults.filter(r => r.hasAvailability);
    
    return `
<!DOCTYPE html>
<html>
<head>
    <title>Montgomery College Course Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #2c5aa0; color: white; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 20px; }
        .summary { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th { background: #2c5aa0; color: white; padding: 12px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #ddd; }
        .available { background-color: #d4edda; }
        .waitlisted { background-color: #f8d7da; }
        .status-available { color: #28a745; font-weight: bold; }
        .status-waitlisted { color: #dc3545; font-weight: bold; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Montgomery College Course Report</h1>
        <p>Generated on ${new Date().toLocaleString()}</p>
    </div>
    
    <div class="summary">
        <h3>Search Criteria</h3>
        <ul>
            <li><strong>Term:</strong> ${currentSearchCriteria.term}</li>
            <li><strong>Subject:</strong> ${currentSearchCriteria.subject}</li>
            <li><strong>Course Number:</strong> ${currentSearchCriteria.courseNumber || 'All'}</li>
            <li><strong>Campus:</strong> ${currentSearchCriteria.campus || 'All'}</li>
            <li><strong>Available Only:</strong> ${currentSearchCriteria.availability ? 'Yes' : 'No'}</li>
        </ul>
        
        <h3>Results Summary</h3>
        <ul>
            <li>Total sections: ${currentSearchResults.length}</li>
            <li>Available sections: ${availableResults.length}</li>
            <li>Waitlisted sections: ${currentSearchResults.length - availableResults.length}</li>
        </ul>
    </div>
    
    <h2>Course Results</h2>
    ${generateCourseTable(currentSearchResults)}
</body>
</html>
    `;
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}