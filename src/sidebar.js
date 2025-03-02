document.addEventListener("DOMContentLoaded", function() {
    // Sidebar hover: expand on mouseenter, collapse on mouseleave.
    const sidebar = document.getElementById("sidebar");
    sidebar.addEventListener("mouseenter", function() {
      sidebar.classList.add("expanded");
    });
    sidebar.addEventListener("mouseleave", function() {
      sidebar.classList.remove("expanded");
    });
  
    // Compact dark mode toggle inside sidebar with smooth transition.
    const darkModeToggle = document.getElementById("sidebar-dark-mode-toggle");
    if (localStorage.getItem("theme") === "dark") {
      document.body.classList.add("dark-mode");
      darkModeToggle.innerHTML = "&#9728;"; // Sun icon
    } else {
      document.body.classList.remove("dark-mode");
      darkModeToggle.innerHTML = "&#9790;"; // Moon icon
    }
    darkModeToggle.addEventListener("click", function() {
      document.body.classList.toggle("dark-mode");
      if (document.body.classList.contains("dark-mode")) {
        localStorage.setItem("theme", "dark");
        darkModeToggle.innerHTML = "&#9728;"; // Sun icon
      } else {
        localStorage.setItem("theme", "light");
        darkModeToggle.innerHTML = "&#9790;"; // Moon icon
      }
    });
  });
  