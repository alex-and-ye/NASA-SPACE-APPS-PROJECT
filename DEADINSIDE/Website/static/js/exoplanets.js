
// Three.js Animation Setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('canvas-container').appendChild(renderer.domElement);

// Create lighting
const ambientLight = new THREE.AmbientLight(0x404040); // Soft white light
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 5, 5).normalize();
scene.add(directionalLight);

// Load background texture
const backgroundTextureLoader = new THREE.TextureLoader();
backgroundTextureLoader.load('https://i.ibb.co/chBqdxM/background2.jpg', (texture) => {
    scene.background = texture; // Set the loaded texture as the scene's background
});

// Create exoplanets with textures
function createExoplanet(radius, texturePath, position) {
    const geometry = new THREE.SphereGeometry(radius, 32, 32);
    const textureLoader = new THREE.TextureLoader();
    const texture = textureLoader.load(texturePath);
    const material = new THREE.MeshStandardMaterial({ map: texture });
    const planet = new THREE.Mesh(geometry, material);
    planet.position.set(position.x, position.y, position.z);
    scene.add(planet);
    return planet;
}

// Add exoplanets to the scene with textures
createExoplanet(1, 'https://i.ibb.co/Zcs8PY8/image-exoplanet.jpg', { x: -3.5, y: 0, z: 0 });
createExoplanet(1, 'https://i.ibb.co/YkfVcQL/image-uranus-1.jpg', { x: -1, y: 0, z: 0 });
createExoplanet(1, 'https://i.ibb.co/MBP2fJL/image-neptune.jpg', { x: 2, y: 0, z: 0 });
createExoplanet(1, 'https://i.ibb.co/XDsdKZ2/image-mars.jpg', { x: 4.5, y: 0, z: 0 });

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
    
    // Rotate the planets (optional)
    
    renderer.render(scene, camera);
}

animate();
