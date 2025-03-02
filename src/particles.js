document.addEventListener("DOMContentLoaded", function() {
    particlesJS("particles-js", {
      "particles": {
        "number": {
          "value": 60,
          "density": {
            "enable": true,
            "value_area": 400  // Smaller area to concentrate particles
          }
        },
        "color": {
          "value": "#ffffff"
        },
        "shape": {
          "type": "circle",
          "stroke": {
            "width": 0,
            "color": "#000000"
          }
        },
        "opacity": {
          "value": 0.8,
          "random": false,
          "anim": {
            "enable": true,
            "speed": 2,      // Faster opacity changes for fade out effect
            "opacity_min": 0.1,
            "sync": false
          }
        },
        "size": {
          "value": 4,
          "random": false,   // Consistent size for all particles
          "anim": {
            "enable": true,
            "speed": 3,
            "size_min": 2,
            "sync": false
          }
        },
        "line_linked": {
          "enable": false  // No connecting lines for a cleaner swarm effect
        },
        "move": {
          "enable": true,
          "speed": 4,       // Increased speed for faster absorption
          "direction": "none",
          "random": false,  // Reduce randomness so movement is focused
          "straight": false,
          "out_mode": "out",
          "bounce": false,
          "attract": {
            "enable": true,
            "rotateX": 300,  // Lower values focus the attraction
            "rotateY": 300
          }
        }
      },
      "interactivity": {
        "detect_on": "canvas",
        "events": {
          "onhover": {
            "enable": false  // Disable hover interactivity for a controlled effect
          },
          "onclick": {
            "enable": false
          },
          "resize": true
        },
        "modes": {
          "grab": {
            "distance": 100,
            "line_linked": {
              "opacity": 0.5
            }
          },
          "push": {
            "particles_nb": 4
          }
        }
      },
      "retina_detect": true
    });
    
    // Expose a global function to fade out the particles when needed.
    window.fadeOutParticles = function() {
      // Use GSAP to fade out the particles canvas.
      // The particles.js library creates a <canvas> element inside the container.
      gsap.to("#particles-js canvas", { opacity: 0, duration: 1 });
    };
  });
  