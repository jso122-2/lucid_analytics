// skeleton.jsx

// Import dependencies.
import { THREE, GLTFLoader } from "./threeLoader.js";
import { OrbitControls } from "./OrbitControls.js";
import { gsap } from "https://cdn.skypack.dev/gsap";
import anime from "https://cdn.jsdelivr.net/npm/animejs@3.2.1/lib/anime.es.js";

// Global variables.
let scene, renderer, controls;
let cameraSkeleton, cameraFlesh;
let skeletonHand, fleshHand;
let articleContainer;
let isSequenceActive = false;
let currentArticleIndex = 0;
let currentModel = "skeleton"; // "skeleton" or "flesh"

// Model paths from static directory
const MODEL_PATHS = {
  skeleton_model: "/static/utils/models/skeleton_hand.glb",
  flesh_model: "/static/utils/models/flesh_hand.glb"
};

// Explanatory texts.
const explanatoryTexts = [
  "Data alone is like the bones of a skeleton—structured, essential, but incomplete. Just as bones provide the foundation for movement and strength, raw data offers the fundamental building blocks for insights and decisions. Yet, without analysis, interpretation, and context, data remains inert, waiting for life to be breathed into it.",
  "Enter transformation. When we apply sophisticated machine learning models to this skeletal structure, it's as if we're layering muscle, skin, and flesh onto bare bones. Each algorithm, each statistical technique, adds detail and vitality, transforming raw information into meaningful, actionable insights—bringing our skeleton vividly to life.",
  "Hit the Transform button and watch as we shift from a stark frame of possibilities to a living, breathing body of knowledge, powered by intelligence, ready to engage and respond dynamically to the world around it."
];

// Get the WebGL container.
const container = document.getElementById("webgl-container");
container.style.position = "relative";
container.style.width = "100%";
container.style.height = "100vh";
// Make container transparent
container.style.backgroundColor = "transparent";

//
// Helper Functions
//
function setModelMaterialsTransparent(model) {
  model.traverse((child) => {
    if (child.isMesh && child.material) {
      child.material.transparent = true;
      child.material.opacity = 1;
    }
  });
}

function crossFadeModelOpacity(model, startOpacity, endOpacity, duration, onComplete) {
  let count = 0;
  const materials = [];
  model.traverse((child) => {
    if (child.isMesh && child.material) {
      child.material.opacity = startOpacity;
      materials.push(child.material);
    }
  });
  if (materials.length === 0) {
    onComplete && onComplete();
    return;
  }
  materials.forEach((mat) => {
    gsap.to(mat, {
      duration,
      opacity: endOpacity,
      ease: "power1.inOut",
      onComplete: () => {
        count++;
        if (count === materials.length && onComplete) {
          onComplete();
        }
      }
    });
  });
}

//
// Direct Hand Model Loading Logic
//
function loadHandAssets() {
  const loader = new GLTFLoader();

  // Load Skeleton Hand.
  loader.load(
    MODEL_PATHS.skeleton_model,
    (gltf) => {
      skeletonHand = gltf.scene;
      skeletonHand.position.set(-0.3, -1, 0);
      skeletonHand.rotation.set(-Math.PI / 2, 0, 0);
      skeletonHand.scale.set(1.2, 1.2, 1.2);
      setModelMaterialsTransparent(skeletonHand);
      skeletonHand.visible = true;
      scene.add(skeletonHand);
      console.log("✅ Skeleton hand loaded from static directory.");
    },
    (xhr) => {
      console.log(`Skeleton hand loading: ${(xhr.loaded / xhr.total) * 100}% loaded`);
    },
    (error) => console.error("❌ Error loading skeleton hand:", error)
  );

  // Load Flesh Hand.
  loader.load(
    MODEL_PATHS.flesh_model,
    (gltf) => {
      fleshHand = gltf.scene;
      fleshHand.position.set(0, -1, 0);
      fleshHand.scale.set(2, 2, 2);
      fleshHand.rotation.set(-1.0472, -0.8727, 0);
      setModelMaterialsTransparent(fleshHand);
      fleshHand.visible = false;
      scene.add(fleshHand);
      console.log("✅ Flesh hand loaded from static directory.");
    },
    (xhr) => {
      console.log(`Flesh hand loading: ${(xhr.loaded / xhr.total) * 100}% loaded`);
    },
    (error) => console.error("❌ Error loading flesh hand:", error)
  );
}

//
// Transform Sequence Logic
//
function showArticle(index, onComplete) {
  const text = explanatoryTexts[index];
  articleContainer.innerHTML = "";
  articleContainer.style.opacity = 1;
  const typingSpeed = 30; // characters per second
  const typingDuration = text.length / typingSpeed;
  let progressObj = { progress: 0 };
  gsap.to(progressObj, {
    duration: typingDuration,
    progress: text.length,
    ease: "none",
    onUpdate: () => {
      articleContainer.innerText = text.substring(0, Math.floor(progressObj.progress));
    },
    onComplete: onComplete
  });
}

function onTransformClick() {
  console.log("Transform button pressed.");
  if (isSequenceActive) return;
  isSequenceActive = true;
  const promptDiv = document.getElementById("permanent-prompt");
  if (promptDiv) promptDiv.remove();

  if (currentArticleIndex === 0 && currentModel === "skeleton" && skeletonHand?.visible) {
    console.log("Dissolving skeleton hand...");
    gsap.to(skeletonHand.scale, {
      duration: 1,
      x: 0, y: 0, z: 0,
      ease: "power1.inOut"
    });
    crossFadeModelOpacity(skeletonHand, 1, 0, 1, () => {
      skeletonHand.visible = false;
      showArticle(currentArticleIndex, () => {
        currentArticleIndex++;
        isSequenceActive = false;
      });
    });
  } else if (currentArticleIndex < explanatoryTexts.length) {
    gsap.to(articleContainer, {
      duration: 0.5,
      opacity: 0,
      onComplete: () => {
        showArticle(currentArticleIndex, () => {
          currentArticleIndex++;
          isSequenceActive = false;
        });
      }
    });
  } else if (currentArticleIndex === explanatoryTexts.length) {
    gsap.to(articleContainer, {
      duration: 0.5,
      opacity: 0,
      onComplete: () => {
        articleContainer.innerHTML = "";
        const transformBtn = document.getElementById("transform-btn");
        if (transformBtn) transformBtn.remove();
        if (currentModel === "skeleton") {
          transitionToFleshHand(() => {
            currentModel = "flesh";
            currentArticleIndex = 0;
            isSequenceActive = false;
          });
        } else {
          transitionToSkeletonHand(() => {
            currentModel = "skeleton";
            currentArticleIndex = 0;
            isSequenceActive = false;
          });
        }
      }
    });
  }
}

function transitionToFleshHand(onComplete) {
  console.log("Transitioning to flesh hand...");
  gsap.to(articleContainer, {
    duration: 0.5,
    opacity: 0,
    onComplete: () => {
      articleContainer.innerHTML = "";
      if (fleshHand) {
        fleshHand.visible = true;
        controls.object = cameraFlesh;
        crossFadeModelOpacity(fleshHand, 0, 1, 1, onComplete);
      } else {
        console.warn("Flesh hand not loaded yet.");
        onComplete && onComplete();
      }
    }
  });
}

function transitionToSkeletonHand(onComplete) {
  console.log("Transitioning to skeleton hand...");
  gsap.to(articleContainer, {
    duration: 0.5,
    opacity: 0,
    onComplete: () => {
      articleContainer.innerHTML = "";
      if (skeletonHand) {
        skeletonHand.visible = true;
        controls.object = cameraSkeleton;
        crossFadeModelOpacity(skeletonHand, 0, 1, 1, onComplete);
      } else {
        console.warn("Skeleton hand not loaded yet.");
        onComplete && onComplete();
      }
    }
  });
}

//
// Initialization and Animation
//
function init() {
  if (!container) {
    console.error("WebGL container not found!");
    return;
  }
  scene = new THREE.Scene();
  const aspect = container.clientWidth / container.clientHeight;

  document.getElementById("transform-btn").addEventListener("click", onTransformClick);

  // Set up the skeleton (Orthographic) camera.
  cameraSkeleton = new THREE.OrthographicCamera(
    (-10 * aspect) / 2,
    (10 * aspect) / 2,
    10 / 2,
    -10 / 2,
    0.1,
    1000
  );
  cameraSkeleton.position.set(-2.468, 1.2, 4.803);
  cameraSkeleton.zoom = 0.19;
  cameraSkeleton.updateProjectionMatrix();
  cameraSkeleton.lookAt(0, -1, 0);

  // Set up the flesh (Perspective) camera.
  cameraFlesh = new THREE.PerspectiveCamera(50, aspect, 0.1, 1000);
  cameraFlesh.position.set(6.044, 5.594, 3.16);
  cameraFlesh.lookAt(0, -1, 0);

  // Renderer with alpha for transparency.
  renderer = new THREE.WebGLRenderer({ 
    antialias: true, 
    alpha: true 
  });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.setClearColor(0x000000, 0); // Fully transparent background
  container.appendChild(renderer.domElement);

  // Set up OrbitControls for the skeleton camera with dark colors instead of white.
  const orbitControllerDiv = document.createElement("div");
  orbitControllerDiv.id = "orbit-controller";
  Object.assign(orbitControllerDiv.style, {
    position: "absolute",
    bottom: "10px",
    left: "10px",
    width: "150px",
    height: "150px",
    background: "#333333", // Dark gray instead of white
    border: "2px solid #555555", // Darker border
    borderRadius: "50%",
    zIndex: "10001",
    cursor: "grab"
  });
  container.appendChild(orbitControllerDiv);

  const orbitLabel = document.createElement("div");
  orbitLabel.id = "orbit-controller-label";
  orbitLabel.innerText = "Use me to rotate hands";
  Object.assign(orbitLabel.style, {
    position: "absolute",
    bottom: "170px",
    left: "10px",
    fontSize: "1rem",
    color: "#cccccc", // Light gray instead of white
    fontWeight: "bold",
    zIndex: "10002"
  });
  container.appendChild(orbitLabel);

  controls = new OrbitControls(cameraSkeleton, orbitControllerDiv);
  controls.enableZoom = false;
  controls.enablePan = false;
  controls.rotateSpeed = 0.3;
  controls.enableDamping = true;
  controls.dampingFactor = 0.1;
  controls.target.set(0, -1, 0);
  controls.update();

  // Lights.
  const ambientLight = new THREE.AmbientLight(0xcccccc, 1.5); // Slightly dimmer light
  scene.add(ambientLight);
  const directionalLight = new THREE.DirectionalLight(0xcccccc, 2); // Slightly dimmer light
  directionalLight.position.set(2, 2, 2);
  scene.add(directionalLight);
  const pointLight = new THREE.PointLight(0xcccccc, 1.5); // Slightly dimmer light
  pointLight.position.set(5, 5, 5);
  scene.add(pointLight);

  // Create an article container for typed text.
  articleContainer = document.createElement("div");
  articleContainer.id = "article-container";
  Object.assign(articleContainer.style, {
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    width: "60%",
    color: "#cccccc", // Light gray instead of white
    fontSize: "2rem",
    textAlign: "center",
    zIndex: "10000",
    pointerEvents: "none",
    opacity: 0,
    textShadow: "1px 1px 3px rgba(0, 0, 0, 0.7)" // Add shadow for better readability on transparent background
  });
  container.appendChild(articleContainer);

  // Load hand models directly.
  loadHandAssets();

  // Optionally load particles.js configuration.
  if (typeof particlesJS !== "undefined") {
    particlesJS.load("particles-js", "/static/utils/particlesjs-config.json", function() {
      console.log("particles.js configuration loaded");
    });
  } else {
    console.error("particlesJS is not defined. Make sure the library is loaded if needed.");
  }

  window.addEventListener("resize", onWindowResize, false);
  initUI();
  initCTAAnimation();
  animate();
}

function onWindowResize() {
  const aspect = container.clientWidth / container.clientHeight;
  cameraSkeleton.left = (-10 * aspect) / 2;
  cameraSkeleton.right = (10 * aspect) / 2;
  cameraSkeleton.top = 10 / 2;
  cameraSkeleton.bottom = -10 / 2;
  cameraSkeleton.updateProjectionMatrix();
  cameraFlesh.aspect = aspect;
  cameraFlesh.updateProjectionMatrix();
  renderer.setSize(container.clientWidth, container.clientHeight);
  controls.update();
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  let activeCamera = cameraSkeleton;
  if (fleshHand && fleshHand.visible) activeCamera = cameraFlesh;
  renderer.render(scene, activeCamera);
}

function initUI() {
  document.addEventListener("click", function(e) {
    if (e.target.matches('a[href^="#"]')) {
      e.preventDefault();
      const target = document.querySelector(e.target.getAttribute("href"));
      if (target) {
        target.scrollIntoView({ behavior: "smooth" });
      }
    }
  });
  window.addEventListener("scroll", function() {
    try {
      const navbar = document.getElementById("navbar");
      if (navbar) {
        if (window.scrollY > 50) {
          navbar.classList.add("shrink");
        } else {
          navbar.classList.remove("shrink");
        }
      }
    } catch (error) {
      console.error("Error in navbar scroll handler:", error);
    }
  });
  window.addEventListener("load", function() {
    try {
      gsap.from(".hero h1", { duration: 1, opacity: 0, y: -50 });
      gsap.from(".hero p", { duration: 1, opacity: 0, y: -50, delay: 0.5 });
    } catch (error) {
      console.error("Error in GSAP hero fade-in:", error);
    }
  });
}

function initCTAAnimation() {
  if (typeof anime !== "undefined") {
    anime({
      targets: ".cta-btn",
      scale: [1, 1.05],
      duration: 1000,
      easing: "easeInOutSine",
      direction: "alternate",
      loop: true
    });
    anime({
      targets: "#transform-btn",
      scale: [1, 1.1],
      duration: 1200,
      easing: "easeInOutSine",
      direction: "alternate",
      loop: true
    });
  } else {
    console.error("anime is not defined in initCTAAnimation");
  }
}

document.addEventListener("DOMContentLoaded", init);