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

// Create exoplanets with textures
function createExoplanet(radius, texturePath, position) {
    const geometry = new THREE.SphereGeometry(radius, 32, 32);
    const textureLoader = new THREE.TextureLoader();
    const texture = textureLoader.load(texturePath);
    const material = new THREE.MeshStandardMaterial({ map: texture }); // Apply texture to material
    const planet = new THREE.Mesh(geometry, material);
    planet.position.set(position.x, position.y, position.z);
    scene.add(planet);
    return planet;
}

// Add exoplanets to the scene with textures
const exoplanet1 = createExoplanet(1, 'https://i.ibb.co/Zcs8PY8/image-exoplanet.jpg', { x: -1, y: 0, z: 0 });
const exoplanet2 = createExoplanet(1, 'https://i.ibb.co/Zcs8PY8/image-exoplanet.jpg',  { x: 2, y: 0, z: 0 });

// Create axes
function createAxes(length) {
    const axesHelper = new THREE.AxesHelper(length);
    scene.add(axesHelper);
}

// Call the function to create axes with a length of 30 units
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
   // exoplanet1.rotation.y += 0.01;
    //exoplanet2.rotation.y += 0.005;
    
    renderer.render(scene, camera);
}

animate();