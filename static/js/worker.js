// worker.js

// Listen for messages from the main thread
self.addEventListener('message', function(e) {
  // For example, receive parameters for particle computation
  const { numParticles, width, height } = e.data;
  const positions = computeParticlePositions(numParticles, width, height);
  // Send the computed positions back to the main thread
  self.postMessage(positions);
});

// Simulate heavy calculation for particle positions
function computeParticlePositions(numParticles, width, height) {
  const positions = [];
  for (let i = 0; i < numParticles; i++) {
    // Dummy calculation: generate random positions
    positions.push({ x: Math.random() * width, y: Math.random() * height });
  }
  return positions;
}
