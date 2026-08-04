# 04_FRONTEND.md

## Frontend Architecture & Design

### Frontend Philosophy

- **Server-Side Rendering**: HTML generated on server, not SPA
- **Progressive Enhancement**: Works without JavaScript
- **Bootstrap**: Consistent, professional styling
- **HTMX**: Dynamic interactions without page reloads
- **Minimal JavaScript**: Vanilla JS for necessary interactions
- **Accessibility**: Keyboard navigation and screen reader support
- **Responsive**: Works on desktop, tablet, and mobile

### Technology Stack

| Technology | Purpose |
|-----------|---------|
| HTML5 | Semantic markup |
| Bootstrap 5 | CSS framework |
| HTMX | Dynamic interactions |
| Vanilla JavaScript | Client-side logic |
| Jinja2 | Server-side templating |

### Directory Structure

```
templates/
├── base.html                 # Base template
├── index.html                # Home page
├── meetings/
│   ├── list.html             # Meetings list
│   ├── detail.html           # Meeting detail
│   ├── create.html           # Create meeting
│   ├── edit.html             # Edit meeting
│   └── delete.html           # Delete confirmation
├── audio/
│   ├── upload.html           # Audio upload
│   └── player.html           # Audio player
├── transcription/
│   ├── view.html             # View transcription
│   └── speaker_segments.html # Speaker segments
├── analysis/
│   ├── summary.html          # Summary view
│   ├── action_items.html     # Action items
│   └── decisions.html        # Decisions
├── search/
│   ├── search.html           # Search page
│   └── results.html          # Search results
├── export/
│   └── export.html           # Export options
└── components/
    ├── navbar.html           # Navigation bar
    ├── footer.html           # Footer
    ├── alerts.html           # Alert messages
    ├── loading.html          # Loading spinner
    └── pagination.html       # Pagination

static/
├── css/
│   ├── main.css              # Custom styles
│   └── bootstrap.min.css     # Bootstrap (CDN)
├── js/
│   ├── main.js               # Main JavaScript
│   ├── htmx.min.js           # HTMX (CDN)
│   └── utils.js              # Utility functions
└── images/
    ├── logo.png
    └── icons/
```

### Base Template

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}AMIP - AI Meeting Intelligence Platform{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', path='css/main.css') }}">
    
    {% block extra_css %}{% endblock %}
</head>
<body>
    <!-- Navigation -->
    {% include 'components/navbar.html' %}
    
    <!-- Main Content -->
    <main class="container mt-4">
        {% if messages %}
            {% for message in messages %}
                <div class="alert alert-{{ message.category }} alert-dismissible fade show" role="alert">
                    {{ message.text }}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                </div>
            {% endfor %}
        {% endif %}
        
        {% block content %}{% endblock %}
    </main>
    
    <!-- Footer -->
    {% include 'components/footer.html' %}
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@1.9.10"></script>
    
    <!-- Custom JS -->
    <script src="{{ url_for('static', path='js/main.js') }}"></script>
    
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### Page Templates

#### Meetings List

```html
{% extends "base.html" %}

{% block title %}Meetings - AMIP{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-md-8">
        <h1>Meetings</h1>
    </div>
    <div class="col-md-4 text-end">
        <a href="{{ url_for('create_meeting') }}" class="btn btn-primary">
            <i class="bi bi-plus"></i> New Meeting
        </a>
    </div>
</div>

<!-- Search Form -->
<div class="card mb-4">
    <div class="card-body">
        <form method="get" class="d-flex gap-2">
            <input type="text" name="search" class="form-control" placeholder="Search meetings...">
            <button type="submit" class="btn btn-outline-primary">Search</button>
        </form>
    </div>
</div>

<!-- Meetings Table -->
<div class="table-responsive">
    <table class="table table-hover">
        <thead class="table-light">
            <tr>
                <th>Title</th>
                <th>Description</th>
                <th>Created</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody>
            {% for meeting in meetings %}
            <tr>
                <td>
                    <a href="{{ url_for('get_meeting', meeting_id=meeting.id) }}">
                        {{ meeting.title }}
                    </a>
                </td>
                <td>{{ meeting.description[:50] }}...</td>
                <td>{{ meeting.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                <td>
                    <a href="{{ url_for('edit_meeting', meeting_id=meeting.id) }}" class="btn btn-sm btn-outline-secondary">
                        Edit
                    </a>
                    <button class="btn btn-sm btn-outline-danger" 
                            hx-delete="{{ url_for('delete_meeting', meeting_id=meeting.id) }}"
                            hx-confirm="Are you sure?">
                        Delete
                    </button>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<!-- Pagination -->
{% if total > limit %}
<nav aria-label="Page navigation">
    <ul class="pagination">
        {% if skip > 0 %}
        <li class="page-item">
            <a class="page-link" href="?skip=0">First</a>
        </li>
        <li class="page-item">
            <a class="page-link" href="?skip={{ skip - limit }}">Previous</a>
        </li>
        {% endif %}
        
        {% if skip + limit < total %}
        <li class="page-item">
            <a class="page-link" href="?skip={{ skip + limit }}">Next</a>
        </li>
        <li class="page-item">
            <a class="page-link" href="?skip={{ (total // limit - 1) * limit }}">Last</a>
        </li>
        {% endif %}
    </ul>
</nav>
{% endif %}
{% endblock %}
```

#### Meeting Detail

```html
{% extends "base.html" %}

{% block title %}{{ meeting.title }} - AMIP{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-md-8">
        <h1>{{ meeting.title }}</h1>
        <p class="text-muted">Created: {{ meeting.created_at.strftime('%Y-%m-%d %H:%M') }}</p>
    </div>
    <div class="col-md-4 text-end">
        <a href="{{ url_for('edit_meeting', meeting_id=meeting.id) }}" class="btn btn-outline-secondary">Edit</a>
        <a href="{{ url_for('list_meetings') }}" class="btn btn-outline-secondary">Back</a>
    </div>
</div>

{% if meeting.description %}
<div class="card mb-4">
    <div class="card-body">
        <h5 class="card-title">Description</h5>
        <p>{{ meeting.description }}</p>
    </div>
</div>
{% endif %}

<!-- Tabs for different sections -->
<ul class="nav nav-tabs mb-4" role="tablist">
    <li class="nav-item" role="presentation">
        <button class="nav-link active" id="audio-tab" data-bs-toggle="tab" data-bs-target="#audio" type="button">
            Audio
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="transcription-tab" data-bs-toggle="tab" data-bs-target="#transcription" type="button">
            Transcription
        </button>
    </li>
    <li class="nav-item" role="presentation">
        <button class="nav-link" id="analysis-tab" data-bs-toggle="tab" data-bs-target="#analysis" type="button">
            Analysis
        </button>
    </li>
</ul>

<div class="tab-content">
    <!-- Audio Tab -->
    <div class="tab-pane fade show active" id="audio" role="tabpanel">
        {% if meeting.audios %}
            {% for audio in meeting.audios %}
            <div class="card mb-3">
                <div class="card-body">
                    <h5 class="card-title">{{ audio.filename }}</h5>
                    <p class="card-text">
                        Duration: {{ audio.duration }}s | Size: {{ audio.file_size | filesizeformat }}
                    </p>
                    <audio controls class="w-100">
                        <source src="{{ url_for('download_audio', audio_id=audio.id) }}" type="{{ audio.mime_type }}">
                        Your browser does not support the audio element.
                    </audio>
                </div>
            </div>
            {% endfor %}
        {% else %}
        <p class="text-muted">No audio files uploaded.</p>
        {% endif %}
        
        <a href="{{ url_for('upload_audio', meeting_id=meeting.id) }}" class="btn btn-primary">
            Upload Audio
        </a>
    </div>
    
    <!-- Transcription Tab -->
    <div class="tab-pane fade" id="transcription" role="tabpanel">
        {% if meeting.audios and meeting.audios[0].transcription %}
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">Transcription</h5>
                <p>{{ meeting.audios[0].transcription.text }}</p>
            </div>
        </div>
        {% else %}
        <p class="text-muted">No transcription available. Upload audio and start transcription.</p>
        {% endif %}
    </div>
    
    <!-- Analysis Tab -->
    <div class="tab-pane fade" id="analysis" role="tabpanel">
        {% if meeting.analysis %}
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">Summary</h5>
                <p>{{ meeting.analysis.summary }}</p>
            </div>
        </div>
        
        <div class="card mb-3">
            <div class="card-body">
                <h5 class="card-title">Action Items</h5>
                <ul>
                {% for item in meeting.analysis.action_items %}
                    <li>{{ item }}</li>
                {% endfor %}
                </ul>
            </div>
        </div>
        {% else %}
        <p class="text-muted">No analysis available. Complete transcription to generate analysis.</p>
        {% endif %}
    </div>
</div>
{% endblock %}
```

### HTMX Usage Examples

#### Delete with Confirmation

```html
<button class="btn btn-danger" 
        hx-delete="{{ url_for('delete_meeting', meeting_id=meeting.id) }}"
        hx-confirm="Are you sure you want to delete this meeting?"
        hx-target="body"
        hx-swap="outerHTML swap:1s">
    Delete
</button>
```

#### Dynamic Search

```html
<input type="text" 
       name="search"
       placeholder="Search meetings..."
       hx-get="{{ url_for('search_meetings') }}"
       hx-trigger="keyup changed delay:500ms"
       hx-target="#search-results">

<div id="search-results"></div>
```

#### File Upload with Progress

```html
<form hx-post="{{ url_for('upload_audio') }}"
      hx-encoding="multipart/form-data"
      hx-target="#upload-status">
    <input type="file" name="file" accept="audio/*" required>
    <button type="submit" class="btn btn-primary">Upload</button>
</form>

<div id="upload-status"></div>
```

### JavaScript Utilities

```javascript
// main.js

// Show toast notification
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.querySelector('main').prepend(alertDiv);
}

// Format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Format duration
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// HTMX event listeners
document.body.addEventListener('htmx:afterSwap', function(evt) {
    // Reinitialize Bootstrap components after HTMX swap
    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
        new bootstrap.Tooltip(el);
    });
});
```

### CSS Customization

```css
/* static/css/main.css */

:root {
    --primary-color: #0d6efd;
    --secondary-color: #6c757d;
    --success-color: #198754;
    --danger-color: #dc3545;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
    background-color: #f8f9fa;
}

main {
    min-height: calc(100vh - 200px);
}

.navbar {
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card {
    border: none;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.btn {
    border-radius: 0.25rem;
}

.table {
    background-color: white;
}

.table-hover tbody tr:hover {
    background-color: #f8f9fa;
}

/* Loading spinner */
.spinner {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid rgba(0, 0, 0, 0.1);
    border-radius: 50%;
    border-top-color: var(--primary-color);
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}
```

### Accessibility Guidelines

1. **Semantic HTML**: Use proper heading hierarchy, labels for inputs
2. **Color Contrast**: Ensure sufficient contrast for readability
3. **Keyboard Navigation**: All interactive elements accessible via keyboard
4. **ARIA Labels**: Add aria-labels where needed
5. **Alt Text**: Provide alt text for images
6. **Focus Management**: Visible focus indicators on interactive elements

### Responsive Design

```html
<!-- Mobile-first approach -->
<div class="container-fluid">
    <div class="row">
        <div class="col-12 col-md-8 col-lg-9">
            <!-- Main content -->
        </div>
        <div class="col-12 col-md-4 col-lg-3">
            <!-- Sidebar -->
        </div>
    </div>
</div>
```

### Performance Optimization

1. **Lazy Loading**: Load images and content on demand
2. **Caching**: Cache static assets with long expiration
3. **Minification**: Minify CSS and JavaScript
4. **Compression**: Enable gzip compression
5. **CDN**: Use CDN for Bootstrap and HTMX

---

**Document Version**: 1.0  
**Last Updated**: 2026-08-03  
**Status**: Active
