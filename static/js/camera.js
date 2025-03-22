let player = document.getElementById('player');
let captureButton = document.getElementById('capture-button');
let canvas = document.getElementById('canvas');
let imageData = document.getElementById('image-data');
let retakeButton = document.getElementById('retake-button');
let analyzeForm = document.getElementById('analyze-form');
let cameraContainer = document.getElementById('camera-container');
let previewContainer = document.getElementById('preview-container');
let cameraError = document.getElementById('camera-error');

// Constraints for the video stream
const constraints = {
    video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: 'environment'  // Use the rear camera if available
    }
};

// Initialize the camera
function initCamera() {
    // Hide error message initially
    if (cameraError) {
        cameraError.style.display = 'none';
    }
    
    // Make sure all elements exist
    if (!player || !canvas) {
        console.error('Missing required elements');
        return;
    }
    
    // Check if getUserMedia is supported
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        if (cameraError) {
            cameraError.textContent = 'Camera access is not supported in this browser or environment. Try using Chrome or Firefox.';
            cameraError.style.display = 'block';
        }
        showFallbackUI();
        return;
    }
    
    // Get access to the camera
    navigator.mediaDevices.getUserMedia(constraints)
        .then((stream) => {
            player.srcObject = stream;
            player.play();
            showCameraUI();
        })
        .catch((err) => {
            console.error('Error accessing camera: ', err);
            if (cameraError) {
                cameraError.textContent = 'Error accessing camera: ' + (err.message || 'Camera permission denied or device not available');
                cameraError.style.display = 'block';
            }
            showFallbackUI();
        });
}

// Show fallback UI when camera is not available
function showFallbackUI() {
    if (cameraContainer) cameraContainer.style.display = 'none';
    if (previewContainer) previewContainer.style.display = 'block';
    
    // Create a message to inform user about alternative options
    const fallbackMsg = document.createElement('div');
    fallbackMsg.className = 'alert alert-info mt-3';
    fallbackMsg.innerHTML = '<strong>Camera not available.</strong> You can upload an image file instead:';
    
    // Create a file input for manual image upload
    const fileInput = document.createElement('input');
    fileInput.type = 'file';
    fileInput.accept = 'image/*';
    fileInput.className = 'form-control mt-3';
    fileInput.addEventListener('change', handleFileUpload);
    
    // Add elements to the preview container
    if (previewContainer) {
        previewContainer.appendChild(fallbackMsg);
        previewContainer.appendChild(fileInput);
    }
}

// Handle file upload when camera is not available
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file || !file.type.match('image.*')) {
        alert('Please select an image file.');
        return;
    }
    
    const reader = new FileReader();
    reader.onload = function(e) {
        // Draw the uploaded image on canvas
        const img = new Image();
        img.onload = function() {
            if (!canvas) return;
            
            const context = canvas.getContext('2d');
            canvas.width = img.width;
            canvas.height = img.height;
            context.drawImage(img, 0, 0);
            
            // Get data URL and store in hidden input
            if (imageData) {
                imageData.value = canvas.toDataURL('image/jpeg');
            }
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

// Show camera UI and hide preview
function showCameraUI() {
    if (cameraContainer) cameraContainer.style.display = 'block';
    if (previewContainer) previewContainer.style.display = 'none';
}

// Show preview UI and hide camera
function showPreviewUI() {
    if (cameraContainer) cameraContainer.style.display = 'none';
    if (previewContainer) previewContainer.style.display = 'block';
}

// Capture image from camera
function captureImage() {
    if (!canvas || !player) return;
    
    const context = canvas.getContext('2d');
    // Set canvas dimensions to match the video
    canvas.width = player.videoWidth;
    canvas.height = player.videoHeight;
    
    // Draw the video frame to the canvas
    context.drawImage(player, 0, 0, canvas.width, canvas.height);
    
    // Get the data URL from the canvas and store it in the hidden input
    if (imageData) {
        imageData.value = canvas.toDataURL('image/jpeg');
    }
    
    // Show the preview
    showPreviewUI();
}

// Retake the photo
function retakePhoto() {
    if (imageData) {
        imageData.value = '';
    }
    showCameraUI();
}

// Event listeners
if (captureButton) {
    captureButton.addEventListener('click', captureImage);
}

if (retakeButton) {
    retakeButton.addEventListener('click', retakePhoto);
}

// Check if we're on the analyze page and initialize the camera
document.addEventListener('DOMContentLoaded', function() {
    if (player) {
        initCamera();
    }
});
