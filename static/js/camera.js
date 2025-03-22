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
                cameraError.textContent = 'Error accessing camera: ' + err.message;
                cameraError.style.display = 'block';
            }
        });
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
