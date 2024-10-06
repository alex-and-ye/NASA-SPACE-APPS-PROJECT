// Set up the scene, camera, and renderer
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Create lighting
const ambientLight = new THREE.AmbientLight(0x404040); // Soft white light
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 5, 5).normalize();
scene.add(directionalLight);

// Create exoplanets
function createExoplanet(radius, color, position) {
  const geometry = new THREE.SphereGeometry(radius, 32, 32);
  const material = new THREE.MeshStandardMaterial({ color: color }); // Use MeshStandardMaterial for better lighting effects
  const planet = new THREE.Mesh(geometry, material);
  planet.position.set(position.x, position.y, position.z);
  scene.add(planet);
  return planet;
}

// Add exoplanets to the scene
const exoplanet1 = createExoplanet(1, 0xff0000, { x: -1, y: 0, z: 0 });
const exoplanet2 = createExoplanet(0.8, 0x00ff00, { x: 2, y: 0, z: 0 });

// Create axes
function createAxes(length) {
    const axesHelper = new THREE.AxesHelper(length);
    scene.add(axesHelper);
}

// Call the function to create axes with a length of 5 units
createAxes(30);

// Position the camera
camera.position.z = 10;

// Handle window resizing
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    
    // Rotate the planets
    exoplanet1.rotation.y += 0.01;
    exoplanet2.rotation.y += 0.005;
    
    renderer.render(scene, camera);
}

animate();