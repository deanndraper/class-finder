// Montgomery College Course Finder - Frontend JavaScript with API Integration

// Global variables
let currentSearchResults = [];
let currentSearchCriteria = {};

// API Configuration
const API_BASE_URL = window.location.origin + '/api';

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
    loadFormData();
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

async function loadFormData() {
    // Load available subjects, terms, and campuses from API
    try {
        const [subjects, terms, campuses] = await Promise.all([
            fetch(`${API_BASE_URL}/subjects`).then(r => r.json()),
            fetch(`${API_BASE_URL}/terms`).then(r => r.json()),
            fetch(`${API_BASE_URL}/campuses`).then(r => r.json())
        ]);
        
        // Populate subject dropdown
        const subjectSelect = document.getElementById('subject');
        subjectSelect.innerHTML = '<option value="">Select Subject</option>';
        subjects.forEach(subject => {
            const option = document.createElement('option');
            option.value = subject.code;
            option.textContent = `${subject.code} - ${subject.name}`;
            if (subject.code === 'COMM') option.selected = true;
            subjectSelect.appendChild(option);
        });
        
        // Populate term dropdown
        const termSelect = document.getElementById('term');
        termSelect.innerHTML = '<option value="">Select Term</option>';
        terms.forEach(term => {
            const option = document.createElement('option');
            option.value = term;
            option.textContent = term;
            if (term === 'Fall 2025') option.selected = true;
            termSelect.appendChild(option);
        });
        
        // Populate campus dropdown
        const campusSelect = document.getElementById('campus');
        campusSelect.innerHTML = '<option value="">All Campuses</option>';
        campuses.forEach(campus => {
            const option = document.createElement('option');
            option.value = campus.code;
            option.textContent = campus.name;
            campusSelect.appendChild(option);
        });
        
    } catch (error) {
        console.warn('Could not load form data from API, using defaults');
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
        await performAPISearch(searchCriteria);
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

async function performAPISearch(criteria) {
    // Show loading steps animation
    const loadingStepsPromise = simulateSearchSteps();
    
    try {
        // Make API request
        const response = await fetch(`${API_BASE_URL}/search`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(criteria)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Search failed');
        }
        
        const data = await response.json();
        
        // Wait for loading animation to complete
        await loadingStepsPromise;
        
        if (data.success) {
            currentSearchResults = data.results;
            showResults(data.results, criteria, data);
        } else {
            throw new Error(data.error || 'Search failed');
        }
        
    } catch (error) {
        // Wait for loading animation to complete before showing error
        await loadingStepsPromise;
        throw error;
    }
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
        
        if (stepElement) {
            // Mark current step as active
            stepElement.classList.add('active');
            
            await new Promise(resolve => setTimeout(resolve, step.delay));
            
            // Mark step as completed
            stepElement.classList.remove('active');
            stepElement.classList.add('completed');
        }
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
    
    // Disable search button
    searchBtn.disabled = true;
    searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Searching...';
}

function showResults(results, criteria, apiData) {
    hideAllSections();
    resultsSection.style.display = 'block';
    resultsSection.classList.add('fade-in');
    
    // Re-enable search button
    searchBtn.disabled = false;
    searchBtn.innerHTML = '<i class="fas fa-search"></i> Search Courses';
    
    // Generate results summary
    const availableResults = results.filter(r => r.hasAvailability);
    const waitlistedResults = results.filter(r => !r.hasAvailability);
    
    // Update summary with checkbox context
    const summaryHtml = generateSummaryCards(results, availableResults, waitlistedResults, apiData, criteria);
    document.getElementById('resultsSummary').innerHTML = summaryHtml;
    
    // Show different content based on availability checkbox
    if (criteria.availability) {
        // Show only available courses when checkbox is checked
        console.log(`🔘 Checkbox CHECKED - Showing only ${availableResults.length} available courses`);
        
        if (availableResults.length > 0) {
            document.getElementById('availableCourses').innerHTML = generateAvailableCoursesSection(availableResults);
            document.getElementById('allCourses').innerHTML = `
                <div class="info-box" style="background: #e8f4f8; padding: 1rem; border-radius: 8px; border-left: 4px solid #2c5aa0;">
                    <strong>ℹ️ Filtered View:</strong> Showing only ${availableResults.length} available courses (seats > waitlist). 
                    <strong>Uncheck "Available Only"</strong> to see all ${results.length} courses.
                </div>
            `;
        } else {
            document.getElementById('availableCourses').innerHTML = generateNoAvailableCoursesSection();
            document.getElementById('allCourses').innerHTML = `
                <div class="info-box" style="background: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <strong>⚠️ No Available Courses:</strong> All ${results.length} courses have waitlists. 
                    <strong>Uncheck "Available Only"</strong> to see all courses and consider joining waitlists.
                </div>
            `;
        }
    } else {
        // Show both sections when checkbox is unchecked
        console.log(`☐ Checkbox UNCHECKED - Showing all ${results.length} courses with ${availableResults.length} available`);
        
        if (availableResults.length > 0) {
            document.getElementById('availableCourses').innerHTML = generateAvailableCoursesSection(availableResults);
        } else {
            document.getElementById('availableCourses').innerHTML = generateNoAvailableCoursesSection();
        }
        
        // Show only waitlisted courses in "All Courses" section to avoid duplicates
        const waitlistedResults = results.filter(r => !r.hasAvailability);
        document.getElementById('allCourses').innerHTML = generateWaitlistedCoursesSection(waitlistedResults);
    }
}

function showError(message) {
    hideAllSections();
    errorSection.style.display = 'block';
    errorSection.classList.add('fade-in');
    document.getElementById('errorMessage').textContent = message;
    
    // Re-enable search button
    searchBtn.disabled = false;
    searchBtn.innerHTML = '<i class="fas fa-search"></i> Search Courses';
}

function hideAllSections() {
    [loadingSection, resultsSection, errorSection].forEach(section => {
        section.style.display = 'none';
        section.classList.remove('fade-in');
    });
}

function generateSummaryCards(allResults, availableResults, waitlistedResults, apiData, criteria) {
    const campuses = [...new Set(allResults.map(r => r.campus))];
    
    // Add checkbox status indicator
    const checkboxStatus = criteria?.availability ? 
        '<div style="background: #d4edda; padding: 0.5rem; border-radius: 4px; margin-top: 0.5rem; font-size: 0.8rem;"><strong>🔘 Filtered:</strong> Available only</div>' :
        '<div style="background: #f8f9fa; padding: 0.5rem; border-radius: 4px; margin-top: 0.5rem; font-size: 0.8rem;"><strong>☐ Showing:</strong> All courses</div>';
    
    return `
        <div class="summary-card">
            <div class="summary-number">${allResults.length}</div>
            <div class="summary-label">Total Sections</div>
            ${checkboxStatus}
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
    const containerId = 'availableCoursesTable';
    setTimeout(() => {
        initializeDataTable(containerId, availableResults, `Available Courses (${availableResults.length})`);
    }, 100);
    
    return `
        <div class="course-table-container">
            <h3><i class="fas fa-check-circle" style="color: #28a745;"></i> Available Courses (${availableResults.length})</h3>
            <div style="background: #d4edda; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #28a745;">
                <strong>🎉 Great news!</strong> These sections have more seats available than people on the waitlist.
            </div>
            <div id="${containerId}"></div>
        </div>
    `;
}

function generateNoAvailableCoursesSection() {
    return `
        <div class="course-table-container">
            <h3><i class="fas fa-exclamation-triangle" style="color: #ffc107;"></i> No Available Courses</h3>
            <div style="background: #fff3cd; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #ffc107;">
                <strong>⚠️ No sections found</strong> with seats available > waitlist count. Consider joining waitlists or checking back regularly.
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

function generateWaitlistedCoursesSection(waitlistedResults) {
    const containerId = 'waitlistedCoursesTable';
    setTimeout(() => {
        initializeDataTable(containerId, waitlistedResults, `Waitlisted Courses (${waitlistedResults.length})`);
    }, 200);
    
    return `
        <div class="course-table-container">
            <h3><i class="fas fa-clock" style="color: #dc3545;"></i> Waitlisted Courses (${waitlistedResults.length})</h3>
            <div style="background: #f8d7da; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid #dc3545;">
                <strong>⏳ Waitlist sections:</strong> These courses have more people waiting than seats available. Consider joining waitlists or checking back regularly.
            </div>
            <div id="${containerId}"></div>
        </div>
    `;
}

function initializeDataTable(containerId, courses, tableTitle = "Course Results") {
    // Clear the container
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (courses.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <h4>No courses found</h4>
                <p>Try adjusting your search criteria</p>
            </div>
        `;
        return;
    }
    
    // Create table element
    const tableId = `${containerId}-table`;
    container.innerHTML = `
        <div class="data-table-wrapper">
            <div class="table-header">
                <h4>${tableTitle}</h4>
            </div>
            <div id="${tableId}"></div>
        </div>
    `;
    
    // Define column configuration
    const columns = [
        {
            title: "CRN", 
            field: "crn", 
            width: 80,
            headerFilter: "input",
            headerFilterPlaceholder: "Filter CRN...",
        },
        {
            title: "Course", 
            field: "course", 
            width: 100,
            headerFilter: "input",
            headerFilterPlaceholder: "Filter course...",
            formatter: function(cell) {
                const course = cell.getValue();
                const courseTitle = cell.getRow().getData().courseTitle || '';
                return `<strong>${course}</strong><br><small>${courseTitle}</small>`;
            }
        },
        {
            title: "Section", 
            field: "section", 
            width: 80,
            headerFilter: "input"
        },
        {
            title: "Days", 
            field: "days", 
            width: 80,
            headerFilter: "input",
            headerFilterPlaceholder: "TR, MW..."
        },
        {
            title: "Time", 
            field: "time", 
            width: 150,
            headerFilter: "input"
        },
        {
            title: "Campus", 
            field: "campus", 
            width: 120,
            headerFilter: "select",
            headerFilterParams: {
                values: true, // Auto-populate from data
                clearable: true,
                placeholder: "All Campuses"
            },
            formatter: function(cell) {
                const campus = cell.getValue();
                const campusClass = getCampusClass(campus);
                return `<span class="campus-tag ${campusClass}">${campus}</span>`;
            }
        },
        {
            title: "Location", 
            field: "location", 
            width: 100,
            headerFilter: "input"
        },
        {
            title: "Instructor", 
            field: "instructor", 
            width: 150,
            headerFilter: "input",
            headerFilterPlaceholder: "Filter instructor..."
        },
        {
            title: "Seats", 
            field: "seatsAvailable", 
            width: 80,
            align: "center",
            sorter: "number",
            formatter: function(cell) {
                return `<strong>${cell.getValue()}</strong>`;
            }
        },
        {
            title: "Waitlist", 
            field: "waitlistCount", 
            width: 80,
            align: "center", 
            sorter: "number",
            formatter: function(cell) {
                return `<strong>${cell.getValue()}</strong>`;
            }
        }
    ];
    
    // Initialize Tabulator
    const table = new Tabulator(`#${tableId}`, {
        data: courses,
        columns: columns,
        layout: "fitColumns",
        responsiveLayout: "collapse",
        pagination: "local",
        paginationSize: 25,
        paginationSizeSelector: [10, 25, 50, 100],
        movableColumns: true,
        resizableRows: false,
        rowFormatter: function(row) {
            const data = row.getData();
            const campusClass = getCampusClass(data.campus);
            const availabilityClass = data.hasAvailability ? 'available' : 'waitlisted';
            row.getElement().classList.add(availabilityClass, campusClass);
        },
        initialSort: [
            {column: "course", dir: "asc"},
            {column: "section", dir: "asc"}
        ],
        tooltips: true,
        tooltipsHeader: true
    });
    
    return table;
}

function downloadTableCSV(tableId) {
    const tableElement = document.querySelector(`#${tableId}`);
    if (tableElement && tableElement.tabulator) {
        tableElement.tabulator.download("csv", "montgomery_college_courses.csv");
    }
}

function generateSimpleTable(courses) {
    if (courses.length === 0) {
        return '<p>No courses found.</p>';
    }
    
    const tableRows = courses.map(course => {
        const campusClass = getCampusClass(course.campus);
        const availabilityClass = course.hasAvailability ? 'available' : 'waitlisted';
        const statusClass = course.hasAvailability ? 'status-available' : 'status-waitlisted';
        
        return `
            <tr class="${availabilityClass} ${campusClass}">
                <td>${course.crn}</td>
                <td><strong>${course.course}</strong><br><small>${course.courseTitle || ''}</small></td>
                <td>${course.section}</td>
                <td>${course.days}</td>
                <td>${course.time}</td>
                <td>${course.campus}</td>
                <td>${course.location}</td>
                <td>${course.instructor}</td>
                <td><strong>${course.seatsAvailable}</strong></td>
                <td><strong>${course.waitlistCount}</strong></td>
            </tr>
        `;
    }).join('');
    
    return `
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <thead>
                <tr>
                    <th style="background: #2c5aa0; color: white; padding: 12px; text-align: left;">CRN</th>
                    <th style="background: #2c5aa0; color: white; padding: 12px; text-align: left;">Course</th>
                    <th style="background: #2c5aa0; color: white; padding: 12px; text-align: left;">Section</th>
                    <th style="background: #2c5aa0; color: white; padding: 12px; text-align: left;">Days</th>
                    <th style="background: #2c5aa0; color: white; padding: 12px; text-align: left;">Time</th>
                    <th style="background: #2c5aa0; color: white; padding: 12px; text-align: left;">Campus</th>
                    <th style="background: #2c5aa0; color: white; padding: 12px; text-align: left;">Location</th>
                    <th style="background: #2c5aa0; color: white; padding: 12px; text-align: left;">Instructor</th>
                    <th style="background: #2c5aa0; color: white; padding: 12px; text-align: left;">Seats</th>
                    <th style="background: #2c5aa0; color: white; padding: 12px; text-align: left;">Waitlist</th>
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
        performAPISearch(currentSearchCriteria);
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
    const headers = ['CRN', 'Course', 'Course Title', 'Section', 'Days', 'Time', 'Campus', 'Location', 'Instructor', 'Seats Available', 'Waitlist Count', 'Status'];
    const csvContent = [
        headers.join(','),
        ...currentSearchResults.map(course => [
            course.crn,
            course.course,
            `"${course.courseTitle || ''}"`,
            course.section,
            course.days,
            `"${course.time}"`,
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
    <meta charset="UTF-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f9f9f9; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #2c5aa0 0%, #1a365d 100%); color: white; padding: 20px; text-align: center; border-radius: 8px; margin-bottom: 20px; }
        .summary { background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th { background: #2c5aa0; color: white; padding: 12px; text-align: left; }
        td { padding: 10px; border-bottom: 1px solid #ddd; }
        .available { background-color: #d4edda; }
        .waitlisted { background-color: #f8d7da; }
        .status-available { color: #28a745; font-weight: bold; }
        .status-waitlisted { color: #dc3545; font-weight: bold; }
        .rockville { border-left: 4px solid #28a745; }
        .germantown { border-left: 4px solid #007bff; }
        .takoma { border-left: 4px solid #6f42c1; }
        .distance { border-left: 4px solid #ffc107; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎓 Montgomery College Course Report</h1>
            <p>Generated on ${new Date().toLocaleString()}</p>
        </div>
        
        <div class="summary">
            <h3>🔍 Search Criteria</h3>
            <ul>
                <li><strong>Term:</strong> ${currentSearchCriteria.term}</li>
                <li><strong>Subject:</strong> ${currentSearchCriteria.subject}</li>
                <li><strong>Course Number:</strong> ${currentSearchCriteria.courseNumber || 'All'}</li>
                <li><strong>Campus:</strong> ${currentSearchCriteria.campus || 'All'}</li>
                <li><strong>Available Only:</strong> ${currentSearchCriteria.availability ? 'Yes' : 'No'}</li>
            </ul>
            
            <h3>📊 Results Summary</h3>
            <ul>
                <li>Total sections: ${currentSearchResults.length}</li>
                <li>Available sections: ${availableResults.length}</li>
                <li>Waitlisted sections: ${currentSearchResults.length - availableResults.length}</li>
            </ul>
        </div>
        
        <h2>📋 Course Results</h2>
        ${generateSimpleTable(currentSearchResults)}
        
        <div style="margin-top: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 4px; font-size: 12px;">
            <p><strong>🤖 Generated by Montgomery College Course Finder</strong></p>
            <p>🏫 Campus Legend: Green=Rockville | Blue=Germantown | Purple=Takoma | Yellow=Distance Learning</p>
        </div>
    </div>
</body>
</html>
    `;
}

// Check API health on load
fetch(`${API_BASE_URL}/health`)
    .then(response => response.json())
    .then(data => {
        console.log('API Health:', data);
        if (!data.automation_available) {
            console.warn('Real automation not available, using sample data');
        }
    })
    .catch(error => {
        console.warn('API not available, using client-side sample data');
    });