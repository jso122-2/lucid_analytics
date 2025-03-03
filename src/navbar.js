document.addEventListener("DOMContentLoaded", function () {
  // Smooth scroll for in-page anchor links using event delegation
  document.addEventListener("click", function (e) {
    if (e.target.matches("a[href^='#']")) {
      e.preventDefault();
      const targetID = e.target.getAttribute("href");
      const targetElem = document.querySelector(targetID);
      if (targetElem) {
        targetElem.scrollIntoView({ behavior: "smooth" });
      }
    }
  });

  // Navbar shrink on scroll - use .navbar instead of .navbar.full-navbar
  window.addEventListener("scroll", function () {
    const navbar = document.querySelector(".navbar");
    if (navbar) {
      if (window.scrollY > 50) {
        navbar.classList.add("shrink");
      } else {
        navbar.classList.remove("shrink");
      }
    }
  });

  // Center the navbar container using flexbox.
  const navbarContainer = document.querySelector(".navbar-container");
  if (navbarContainer) {
    navbarContainer.style.display = "flex";
    navbarContainer.style.justifyContent = "center";
  }

  // Remove the Utilities button, if present.
  // (Assumes the Utilities button has a recognizable class or id.)
  const utilitiesButton = document.querySelector("#sidebar .sidebar-item:nth-child(2)");
  if (utilitiesButton) {
    utilitiesButton.remove();
  }

  // Additional JS animations for navbar hover effects could be added here if desired.
});
