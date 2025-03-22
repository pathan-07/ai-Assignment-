document.addEventListener('DOMContentLoaded', function() {
    // Initialize the progress bar if it exists
    const scoreElement = document.getElementById('score-value');
    const progressBar = document.getElementById('score-progress');
    
    if (scoreElement && progressBar) {
        const score = parseFloat(scoreElement.textContent);
        updateProgressBar(score);
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize keyword context popovers
    const keywordElements = document.querySelectorAll('.keyword-item');
    keywordElements.forEach(element => {
        element.addEventListener('click', function() {
            const keywordId = this.getAttribute('data-keyword-id');
            const contextContainer = document.getElementById(`context-${keywordId}`);
            
            if (contextContainer) {
                // Toggle the visibility of the context
                if (contextContainer.style.display === 'none') {
                    contextContainer.style.display = 'block';
                } else {
                    contextContainer.style.display = 'none';
                }
            }
        });
    });
});

function updateProgressBar(score) {
    const progressBar = document.getElementById('score-progress');
    if (!progressBar) return;
    
    // Update progress bar width
    progressBar.style.width = `${score}%`;
    
    // Update progress bar color based on score
    if (score < 40) {
        progressBar.classList.remove('bg-warning', 'bg-success');
        progressBar.classList.add('bg-danger');
    } else if (score < 70) {
        progressBar.classList.remove('bg-danger', 'bg-success');
        progressBar.classList.add('bg-warning');
    } else {
        progressBar.classList.remove('bg-danger', 'bg-warning');
        progressBar.classList.add('bg-success');
    }
}
