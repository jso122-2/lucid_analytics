document.addEventListener("DOMContentLoaded", function () {
  // Define the HTML structure of the navbar.
  const navHTML = `
    <div class="navbar" id="navbar">
      <div class="navbar-container sexier-navbar">
        <div class="logo">Lucid Analytics</div>
        <ul class="nav-list">
          <li class="nav-item"><a href="/">Home</a></li>
          <li class="nav-item"><a href="/churn">Churn Analysis</a></li>
          <li class="nav-item"><a href="/nps">NPS Analysis</a></li>
          <li class="nav-item"><a href="/media">Media Analysis</a></li>
          <li class="nav-item"><a href="/about">About</a></li>
        </ul>
      </div>
    </div>
  `;

  // Insert the navbar HTML at the very top of <body>.
  // If you prefer it below something else, adjust accordingly.
  document.body.insertAdjacentHTML('afterbegin', navHTML);

  // Add the "shrink on scroll" logic (optional).
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
});
