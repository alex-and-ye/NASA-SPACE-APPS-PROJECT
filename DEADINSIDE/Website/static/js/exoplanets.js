// Set up the scene, camera, and renderer
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Create exoplanets
function createExoplanet(radius, color, position) {
  const geometry = new THREE.SphereGeometry(radius, 32, 32);
  const material = new THREE.MeshBasicMaterial({ color: color });
  const planet = new THREE.Mesh(geometry, material);
  planet.position.set(position.x, position.y, position.z);
  scene.add(planet);
  return planet;
}

// Add exoplanets to the scene
const exoplanet1 = createExoplanet(1, 0xff0000, { x: -2, y: 0, z: 0 });
const exoplanet2 = createExoplanet(1.5, 0x00ff00, { x: 2, y: 0, z: 0 });

// Position the camera
camera.position.z = 10;

// Animation loop
function animate() {
  requestAnimationFrame(animate);
  
  // Rotate the planets
  exoplanet1.rotation.y += 0.01;
  exoplanet2.rotation.y += 0.005;
  
  renderer.render(scene, camera);
}

animate();