// Script for Tooltip
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})

window.addEventListener('load', () => {
  // Script for CopyIcon
  const copyTextIcon = document.querySelector(".copy-text-icon");// Icon

  if (copyTextIcon) {
    copyTextIcon.addEventListener('click', () => {
    const textToCopy = document.getElementById('short-link').value;

  navigator.clipboard.writeText(textToCopy)
    .then(() => {
      const notification = document.createElement("div");
      notification.classList.add("notification")
      notification.textContent="Link copied to clipboard!";
      document.body.appendChild(notification);

      setTimeout (function() {
        document.body.removeChild(notification);
      }, 3000)
    })
    .catch((error) => {
      // Something went wrong while copying the text.
      alert("Error in copying link!")
    });
  });
  }

});