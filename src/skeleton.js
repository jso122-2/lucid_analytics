// Import dependencies.
import { THREE, GLTFLoader } from "./threeLoader.js";
import { OrbitControls } from "./OrbitControls.js";
import { gsap } from "https://cdn.skypack.dev/gsap";
import anime from "https://cdn.jsdelivr.net/npm/animejs@3.2.1/lib/anime.es.js";

// Use the injected MINIO_BASE_URL or fallback.
const minioBase =
  window.MINIO_BASE_URL || "http://127.0.0.1:9000/marketing.models/models/";
console.log("minioBase:", minioBase);

// Global variables.
let scene, renderer, controls;
let cameraSkeleton, cameraFlesh;
let skeletonHand, fleshHand;
let skeletonParticles, fleshParticles;
let articleContainer;
let isSequenceActive = false;
let currentArticleIndex = 0;
let currentModel = "skeleton"; // "skeleton" or "flesh"

const container = document.getElementById("webgl-container");
// Ensure container fills the viewport and is positioned relatively.
container.style.position = "relative";
container.style.width = "100%";
container.style.height = "100vh";

// Original scales.
const originalSkeletonScale = { x: 1.2, y: 1.2, z: 1.2 };
const originalFleshScale = { x: 2, y: 2, z: 2 };

// Explanatory text articles.
const explanatoryTexts = [
  "Data alone is like the bones of a skeleton—structured, essential, but incomplete. Just as bones provide the foundation for movement and strength, raw data offers the fundamental building blocks for insights and decisions. Yet, without analysis, interpretation, and context, data remains inert, waiting for life to be breathed into it.",
  "Enter transformation. When we apply sophisticated machine learning models to this skeletal structure, it’s as if we're layering muscle, skin, and flesh onto bare bones. Each algorithm, each statistical technique, adds detail and vitality, transforming raw information into meaningful, actionable insights—bringing our skeleton vividly to life.",
  "Hit the Transform button and watch as we shift from a stark frame of possibilities to a living, breathing body of knowledge, powered by intelligence, ready to engage and respond dynamically to the world around it."
];

// Helper: Set model materials to be transparent.
function setModelMaterialsTransparent(model) {
  model.traverse((child) => {
    if (child.isMesh && child.material) {
      child.material.transparent = true;
      child.material.opacity = 1;
    }
  });
}

// Helper: Crossfade a model's materials from startOpacity to endOpacity.
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
      duration: duration,
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

// Initialize scene, models, UI, and the custom orbit controller.
function init() {
  if (!container) {
    console.error("WebGL container not found!");
    return;
  }
  scene = new THREE.Scene();
  const aspect = container.clientWidth / container.clientHeight;

  // Set up cameras.
  cameraSkeleton = new THREE.OrthographicCamera(
    (-10 * aspect) / 2,
    (10 * aspect) / 2,
    10 / 2,
    -10 / 2,
    0.1,
    1000
  );
  cameraSkeleton.position.set(0, 2, 5);
  cameraSkeleton.zoom = 0.19;
  cameraSkeleton.updateProjectionMatrix();
  cameraSkeleton.lookAt(0, -1, 0);

  cameraFlesh = new THREE.PerspectiveCamera(50, aspect, 0.1, 1000);
  cameraFlesh.position.set(0, 2, 5);
  cameraFlesh.lookAt(0, -0.8, 0);

  // Renderer.
  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.outputEncoding = THREE.sRGBEncoding;
  renderer.setClearColor(0x000000, 0);
  container.appendChild(renderer.domElement);

  // Create a custom orbit controller element in bottom-left.
  const orbitControllerDiv = document.createElement("div");
  orbitControllerDiv.id = "orbit-controller";
  orbitControllerDiv.style.position = "absolute";
  orbitControllerDiv.style.bottom = "10px";
  orbitControllerDiv.style.left = "10px";
  orbitControllerDiv.style.width = "150px";
  orbitControllerDiv.style.height = "150px";
  orbitControllerDiv.style.background = "rgba(0,0,0,0.5)";
  orbitControllerDiv.style.borderRadius = "50%";
  orbitControllerDiv.style.zIndex = "10001";
  orbitControllerDiv.style.cursor = "grab";
  container.appendChild(orbitControllerDiv);

  // Attach OrbitControls to the custom orbit controller.
  controls = new OrbitControls(cameraSkeleton, orbitControllerDiv);
  controls.enableZoom = false;
  controls.enablePan = false;
  controls.rotateSpeed = 0.3;
  controls.enableDamping = true;
  controls.dampingFactor = 0.1;
  controls.target.set(0, -1, 0);
  controls.update();

  // Lights.
  const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
  scene.add(ambientLight);
  const directionalLight = new THREE.DirectionalLight(0xffffff, 2);
  directionalLight.position.set(2, 2, 2);
  scene.add(directionalLight);
  const pointLight = new THREE.PointLight(0xffffff, 1.5);
  pointLight.position.set(5, 5, 5);
  scene.add(pointLight);

  // Load models.
  const loader = new GLTFLoader();
  loader.load(
    minioBase + "skeleton_hand.glb",
    (gltf) => {
      skeletonHand = gltf.scene;
      skeletonHand.position.set(0, -1, 0);
      skeletonHand.rotation.set(-Math.PI / 2, 0, 0);
      skeletonHand.scale.set(
        originalSkeletonScale.x,
        originalSkeletonScale.y,
        originalSkeletonScale.z
      );
      setModelMaterialsTransparent(skeletonHand);
      skeletonHand.visible = true;
      scene.add(skeletonHand);
      console.log("Skeleton hand loaded and visible.");
      skeletonHand.updateMatrixWorld(true);
      skeletonParticles = createHandParticles(skeletonHand, 0xffffff, 300);
      skeletonHand.add(skeletonParticles);
      skeletonParticles.material.opacity = 0;
    },
    undefined,
    (error) => console.error("Error loading skeleton hand:", error)
  );
  loader.load(
    minioBase + "flesh_hand.glb",
    (gltf) => {
      fleshHand = gltf.scene;
      fleshHand.position.set(0, -1, 0);
      fleshHand.scale.set(
        originalFleshScale.x,
        originalFleshScale.y,
        originalFleshScale.z
      );
      fleshHand.rotation.set(-1.0472, -0.8727, 0);
      setModelMaterialsTransparent(fleshHand);
      fleshHand.visible = false;
      scene.add(fleshHand);
      console.log("Flesh hand loaded (hidden).");
      fleshHand.updateMatrixWorld(true);
      fleshParticles = createHandParticles(fleshHand, 0xffffff, 300);
      fleshHand.add(fleshParticles);
      fleshParticles.material.opacity = 0;
    },
    undefined,
    (error) => console.error("Error loading flesh hand:", error)
  );

  // Create a permanent prompt (centered over the hand on initial load).
  createPermanentPrompt();

  // Create a global article container for text.
  articleContainer = document.createElement("div");
  articleContainer.id = "article-container";
  articleContainer.style.position = "absolute";
  articleContainer.style.top = "50%";
  articleContainer.style.left = "50%";
  articleContainer.style.transform = "translate(-50%, -50%)";
  articleContainer.style.width = "60%";
  articleContainer.style.color = "#fff";
  articleContainer.style.fontSize = "2rem";
  articleContainer.style.textAlign = "center";
  articleContainer.style.zIndex = "10000";
  articleContainer.style.pointerEvents = "none";
  articleContainer.style.opacity = 0;
  container.appendChild(articleContainer);

  // Set up the Transform button.
  const transformBtn = document.getElementById("transform-btn");
  if (transformBtn) {
    transformBtn.style.zIndex = "10002";
    transformBtn.addEventListener("click", onTransformClick);
  } else {
    console.error("Transform button not found!");
  }
  window.addEventListener("resize", onWindowResize, false);

  initUI();
  initCTAAnimation();

  animate();
}

// Create a particle system for a model.
function createHandParticles(model, color, count) {
  model.updateMatrixWorld(true);
  const bbox = new THREE.Box3().setFromObject(model);
  const size = bbox.getSize(new THREE.Vector3());
  const radius = Math.max(size.x, size.y, size.z) * 0.7;

  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const phi = Math.acos(2 * Math.random() - 1);
    const theta = 2 * Math.PI * Math.random();
    const r = radius * (0.5 + Math.random() * 0.5);
    positions[i * 3] = r * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
    positions[i * 3 + 2] = r * Math.cos(phi);
  }
  geometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));

  const material = new THREE.PointsMaterial({
    color: color,
    size: 0.1,
    transparent: true,
    opacity: 1
  });

  return new THREE.Points(geometry, material);
}

// Create a permanent prompt; center it over the hand on initial load.
function createPermanentPrompt() {
  let promptDiv = document.getElementById("permanent-prompt");
  if (!promptDiv) {
    promptDiv = document.createElement("div");
    promptDiv.id = "permanent-prompt";
    promptDiv.innerText = "Press Transform Button to Learn More";
    // Centered over the hand:
    promptDiv.style.position = "absolute";
    promptDiv.style.top = "50%";
    promptDiv.style.left = "50%";
    promptDiv.style.transform = "translate(-50%, -50%)";
    promptDiv.style.color = "#fff";
    promptDiv.style.fontSize = "1.8rem";
    promptDiv.style.backgroundColor = "rgba(0, 0, 0, 0.6)";
    promptDiv.style.padding = "10px 20px";
    promptDiv.style.borderRadius = "10px";
    promptDiv.style.opacity = 0.9;
    promptDiv.style.zIndex = "9999";
    promptDiv.style.pointerEvents = "none";
    container.appendChild(promptDiv);
  }
}

// When the Transform button is pressed, advance the sequence.
function onTransformClick() {
  console.log("Transform button pressed.");
  if (isSequenceActive) return;
  isSequenceActive = true;

  // Remove the permanent prompt.
  let promptDiv = document.getElementById("permanent-prompt");
  if (promptDiv) promptDiv.remove();

  if (currentArticleIndex === 0 && currentModel === "skeleton" && skeletonHand?.visible) {
    console.log("Dissolving skeleton hand into particles...");
    gsap.to(skeletonHand.scale, {
      duration: 1,
      x: 0, y: 0, z: 0,
      ease: "power1.inOut"
    });
    crossFadeModelOpacity(skeletonHand, 1, 0, 1, () => {
      skeletonHand.visible = false;
      if (skeletonParticles) {
        gsap.to(skeletonParticles.material, { duration: 1, opacity: 1 });
        gsap.to(skeletonParticles.scale, {
          duration: 1,
          x: 3, y: 3, z: 3,
          ease: "power1.out",
          onComplete: () => {
            showArticle(currentArticleIndex, () => {
              currentArticleIndex++;
              isSequenceActive = false;
            });
          }
        });
      } else {
        showArticle(currentArticleIndex, () => {
          currentArticleIndex++;
          isSequenceActive = false;
        });
      }
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

// Show an article with a typing effect.
function showArticle(index, onComplete) {
  const text = explanatoryTexts[index];
  articleContainer.innerHTML = "";
  articleContainer.style.opacity = 1;
  let progressObj = { progress: 0 };
  gsap.to(progressObj, {
    duration: 8,
    progress: text.length,
    ease: "none",
    onUpdate: () => {
      articleContainer.innerText = text.substring(0, Math.floor(progressObj.progress));
    },
    onComplete: onComplete
  });
}

// Transition to the flesh hand model.
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
        if (fleshParticles) {
          gsap.to(fleshParticles.material, { duration: 1, opacity: 1 });
        }
      } else {
        console.warn("Flesh hand not loaded yet.");
        onComplete && onComplete();
      }
    }
  });
}

// Transition to the skeleton hand model.
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
        if (skeletonParticles) {
          gsap.to(skeletonParticles.material, { duration: 1, opacity: 1 });
        }
      } else {
        console.warn("Skeleton hand not loaded yet.");
        onComplete && onComplete();
      }
    }
  });
}

// Update camera and renderer on window resize.
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
  document.addEventListener("click", function (e) {
    if (e.target.matches('a[href^="#"]')) {
      e.preventDefault();
      const target = document.querySelector(e.target.getAttribute("href"));
      if (target) {
        target.scrollIntoView({ behavior: "smooth" });
      }
    }
  });
  window.addEventListener("scroll", function () {
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
  window.addEventListener("load", function () {
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
      loop: true,
    });
    anime({
      targets: "#transform-btn",
      scale: [1, 1.1],
      duration: 1200,
      easing: "easeInOutSine",
      direction: "alternate",
      loop: true,
    });
  } else {
    console.error("anime is not defined in initCTAAnimation");
  }
}

document.addEventListener("DOMContentLoaded", init);
