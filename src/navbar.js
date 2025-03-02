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

  // Navbar shrink on scroll
  window.addEventListener("scroll", function () {
    const navbar = document.querySelector(".navbar.full-navbar");
    if (window.scrollY > 50) {
      navbar.classList.add("shrink");
    } else {
      navbar.classList.remove("shrink");
    }
  });

  // Bubble-style navigation hover animations are handled via CSS,
  // but you can add additional JS animations here if desired.
});
