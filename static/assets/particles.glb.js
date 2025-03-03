document.addEventListener("DOMContentLoaded", function() {
  // Ensure the container for the GLB particles exists
  const container = document.getElementById("particles-glb-container");
  if (!container) {
    console.error("No container for particles found!");
    return;
  }

  // Create a Three.js scene for the particles
  const scene = new THREE.Scene();

  // Set up a camera to view the particles; adjust FOV and aspect as needed
  const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
  camera.position.z = 5;

  // Create a WebGL renderer with alpha (transparency)
  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  // Load the particles GLB model
  const loader = new THREE.GLTFLoader();
  let particlesModel;
  loader.load(
    "{{ url_for('static', filename='assets/particles.glb') }}",
    function(gltf) {
      particlesModel = gltf.scene;
      // Optionally scale the model
      particlesModel.scale.set(0.5, 0.5, 0.5);
      scene.add(particlesModel);
    },
    undefined,
    function(error) {
      console.error("Error loading particles.glb:", error);
    }
  );

  // Animation speed factor; adjust as needed
  const speedFactor = 0.5;
  // Assume the target (hand) is centered at (0,0,0) in our Three.js world.
  // You could compute this dynamically by getting the hand container's position.
  const targetPosition = new THREE.Vector3(0, 0, 0);

  // Animation loop: update particle positions to move toward the target
  function animate() {
    requestAnimationFrame(animate);
    const delta = clock.getDelta();

    if (particlesModel) {
      particlesModel.traverse(function(child) {
        if (child.isMesh) {
          // Compute a vector from the child position to the target
          const direction = targetPosition.clone().sub(child.position).normalize();
          // Move the particle toward the target at a rate proportional to speedFactor and delta time
          child.position.add(direction.multiplyScalar(speedFactor * delta));
        }
      });
    }

    renderer.render(scene, camera);
  }

  // Start the animation loop
  const clock = new THREE.Clock();
  animate();

  // Expose a global function to fade out and remove the particles.
  // Call this function when the final hand transformation is reached.
  window.fadeOutParticles = function() {
    if (!particlesModel) return;
    // Use GSAP to animate the opacity of the model.
    // We traverse all meshes and tween their material opacity.
    particlesModel.traverse(function(child) {
      if (child.isMesh && child.material) {
        // Ensure material is transparent
        child.material.transparent = true;
        gsap.to(child.material, {
          opacity: 0,
          duration: 1,
          onComplete: function() {
            // Optionally, remove the mesh from the scene after fading out
            scene.remove(child);
          }
        });
      }
    });
  };
});
