// particlesGLB.js
import { THREE, GLTFLoader } from "./threeLoader.js";

document.addEventListener("DOMContentLoaded", function() {
  const container = document.getElementById("particles-glb-container");
  if (!container) {
    console.error("No container for particles found!");
    return;
  }

  // Create a Three.js scene for the particles
  const scene = new THREE.Scene();

  // Set up a camera to view the particles
  const camera = new THREE.PerspectiveCamera(60, container.clientWidth / container.clientHeight, 0.1, 1000);
  camera.position.z = 5;

  // Create a renderer with transparency enabled
  const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  container.appendChild(renderer.domElement);

  // Load the particles GLB model
  const loader = new GLTFLoader();
  let particlesModel;
  loader.load(
    "/static/assets/particles.glb",
    (gltf) => {
      particlesModel = gltf.scene;
      particlesModel.scale.set(0.5, 0.5, 0.5);
      scene.add(particlesModel);
    },
    undefined,
    (error) => {
      console.error("Error loading particles.glb:", error);
    }
  );

  // Set up animation to move particles toward a target
  const speedFactor = 0.5;
  const targetPosition = new THREE.Vector3(0, 0, 0);
  const clock = new THREE.Clock();
  function animate() {
    requestAnimationFrame(animate);
    const delta = clock.getDelta();
    if (particlesModel) {
      particlesModel.traverse((child) => {
        if (child.isMesh) {
          const direction = targetPosition.clone().sub(child.position).normalize();
          child.position.add(direction.multiplyScalar(speedFactor * delta));
        }
      });
    }
    renderer.render(scene, camera);
  }
  animate();

  // Expose a global function to fade out the particles
  window.fadeOutParticles = function() {
    if (!particlesModel) return;
    particlesModel.traverse((child) => {
      if (child.isMesh && child.material) {
        child.material.transparent = true;
        gsap.to(child.material, {
          opacity: 0,
          duration: 1,
          onComplete: function() {
            scene.remove(child);
          }
        });
      }
    });
  };
});
