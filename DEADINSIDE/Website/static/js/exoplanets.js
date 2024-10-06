// Three.js Animation Setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('canvas-container').appendChild(renderer.domElement);

// Create lighting
const ambientLight = new THREE.AmbientLight(0x404040);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
directionalLight.position.set(5, 5, 5).normalize();
scene.add(directionalLight);

// Load background texture
const backgroundTextureLoader = new THREE.TextureLoader();
backgroundTextureLoader.load('https://i.ibb.co/chBqdxM/background2.jpg', (texture) => {
    scene.background = texture;
});

// Planet textures
const planetTextures = [
    'https://i.ibb.co/Zcs8PY8/image-exoplanet.jpg',
    'https://i.ibb.co/YkfVcQL/image-uranus-1.jpg',
    'https://i.ibb.co/MBP2fJL/image-neptune.jpg',
    'https://i.ibb.co/XDsdKZ2/image-mars.jpg'
];

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

// Position the camera
camera.position.z = 15;

let currentPlanetSet = 0;
const planetsPerSet = 6;
let allPlanets = [];

const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function displayPlanets(planets) {
    // Clear existing planets
    scene.children.forEach(child => {
        if (child instanceof THREE.Mesh && child.geometry instanceof THREE.SphereGeometry) {
            scene.remove(child);
        }
    });

    // Add new planets
    planets.forEach((planet, index) => {
        const textureIndex = index % planetTextures.length;
        const planetMesh = createExoplanet(1.5, planetTextures[textureIndex], { x: (index - 2.5) * 4, y: 0, z: 0 });
        planetMesh.userData = planet;

        // Add click event listener to each planet
        planetMesh.callback = function() {
            showPlanetInfo(planet);
        };
    });
}

function navigatePlanets(direction) {
    currentPlanetSet += direction;
    if (currentPlanetSet < 0) currentPlanetSet = 0;
    if (currentPlanetSet * planetsPerSet >= allPlanets.length) currentPlanetSet--;

    const startIndex = currentPlanetSet * planetsPerSet;
    displayPlanets(allPlanets.slice(startIndex, startIndex + planetsPerSet));
}

function showPlanetInfo(planet) {
    const modal = document.getElementById('planet-info-modal');
    const modalName = document.getElementById('modal-planet-name');
    const modalInfo = document.getElementById('modal-planet-info');

    modalName.textContent = planet.pl_name;
    modalInfo.innerHTML = `
        Host Star: ${planet.hostname}<br>
        Distance: ${planet.sy_dist.toFixed(2)} parsecs<br>
        Planet Radius: ${planet.pl_rade.toFixed(2)} Earth Radii<br>
        SNR: ${planet.snr.toFixed(2)}<br>
        Semi-Major Axis: ${planet.pl_orbsmax.toFixed(3)} AU
    `;

    modal.style.display = 'block';
}

// Close modal when clicking on <span> (x)
document.querySelector('.close').onclick = function() {
    document.getElementById('planet-info-modal').style.display = 'none';
}

// Close modal when clicking outside of it
window.onclick = function(event) {
    const modal = document.getElementById('planet-info-modal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}

// Handle window resizing
window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

animate();
function updateCosmicStatistics(data) {
    document.getElementById('total-planets').textContent = data.total_planets;
    document.getElementById('avg-snr').textContent = data.avg_snr.toFixed(2);
    document.getElementById('median-snr').textContent = data.median_snr.toFixed(2);
    document.getElementById('std-snr').textContent = data.std_snr.toFixed(2);
    document.getElementById('max-snr').textContent = data.max_snr.toFixed(2);
    document.getElementById('min-snr').textContent = data.min_snr.toFixed(2);
}
// Fetch initial planet data
function fetchPlanets(params = '') {
    fetch('/get_planets/?' + params)
        .then(response => response.json())
        .then(data => {
            allPlanets = data.planets;
            navigatePlanets(0);
            updateCosmicStatistics(data);
        })
        .catch(error => console.error('Error:', error));
}



fetchPlanets();

// Update value displays for range inputs
function updateRangeValue(inputId) {
    const input = document.getElementById(inputId);
    const valueSpan = document.getElementById(inputId + '_value');
    valueSpan.textContent = input.value;
}

document.getElementById('telescope_diameter').addEventListener('input', () => updateRangeValue('telescope_diameter'));
document.getElementById('min_snr').addEventListener('input', () => updateRangeValue('min_snr'));
document.getElementById('max_distance').addEventListener('input', () => updateRangeValue('max_distance'));

// Initialize values
updateRangeValue('telescope_diameter');
updateRangeValue('min_snr');
updateRangeValue('max_distance');

// Prevent form submission and use AJAX instead
document.getElementById('filter-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const searchParams = new URLSearchParams(formData);

    fetchPlanets(searchParams.toString());
});


function onMouseClick(event) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = - (event.clientY / window.innerHeight) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);

    const intersects = raycaster.intersectObjects(scene.children);

    for (let i = 0; i < intersects.length; i++) {
        if (intersects[i].object.callback) {
            intersects[i].object.callback();
            break;
        }
    }
}

window.addEventListener('click', onMouseClick, false);