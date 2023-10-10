// Script for Tooltip
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

// Script for CopyIcon
const copyTextIcon = document.querySelector(".copy-text-icon");// Icon


copyTextIcon.addEventListener('click', () => {
  const textToCopy = document.getElementById('short-link').value;

  navigator.clipboard.writeText(textToCopy)
    .then(() => {
      // Text copied successfully!
      alert("Link copied to clipboard")
    })
    .catch((error) => {
      // Something went wrong while copying the text.
      alert("Error in copying link!")
    });
});