const sharp = require('sharp');
const path = require('path');

const svgPath = path.join(__dirname, '..', 'assets', 'icon.svg');
const pngPath = path.join(__dirname, '..', 'assets', 'icon.png');

sharp(svgPath)
  .resize(1024, 1024)
  .png()
  .toFile(pngPath)
  .then(() => console.log('Icon generated successfully'))
  .catch(err => console.error('Error generating icon:', err)); 