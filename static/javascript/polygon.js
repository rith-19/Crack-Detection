function activateSmartPolygon() {
    console.log("Entering activateSmartPolygon function");
    var polyButton = document.querySelector('.polybt'); // Get the polygon button element

  if (!drawingPolygon) {
      drawingPolygon = true;
      canvas.style.cursor = 'crosshair';
      polygonPoints = []; // Reset polygon points array
      canvas.addEventListener('click', addPolygonPoint);
      console.log("Polygon drawing activated");
      // Indicate button activation
      polyButton.classList.add('active');
      polyButton.style.backgroundColor = 'green'; // Change background color to green
  } else {
      drawingPolygon = false;
      canvas.style.cursor = 'default';
      canvas.removeEventListener('click', addPolygonPoint);
      // Here you can process the polygonPoints array to draw the polygon
      drawPolygon();
      console.log("Polygon drawing deactivated");
      // Indicate button deactivation
      polyButton.classList.remove('active'); // Remove 'active' class from polygon button
      polyButton.style.backgroundColor = ''; // Reset background color
  }
}


function addPolygonPoint(event) {
  console.log("Entering addPolygonPoint function");
  var { x, y } = getCanvasCoordinates(event);
  polygonPoints.push({ x: x, y: y });
  // You can draw the polygon dynamically as the points are added if needed
  console.log("Point added to polygon at coordinates: (" + x + ", " + y + ")");

  // Check if drawing polygon is active
  if (drawingPolygon) {
      drawPolygon(); // Call drawPolygon if drawing polygon is active
  }
}

function drawPolygon() {
  console.log("Entering drawPolygon function");
  ctx.clearRect(0, 0, canvas.width, canvas.height); // Clear the canvas
  ctx.drawImage(image, 0, 0); // Redraw the image

  if (polygonPoints.length < 2) {
      console.log("Not enough points to draw polygon");
      return; // Polygon needs at least 2 points
  }

  // Draw pointers (dots) at each point
  ctx.fillStyle = 'teal'; // Set color for pointers
  var pointerRadius = 2;
  for (var i = 0; i < polygonPoints.length; i++) {
      ctx.beginPath();
      ctx.arc(polygonPoints[i].x, polygonPoints[i].y, 5, 0, Math.PI * 2);
      ctx.fill();
  }

  // Set border color to white
  ctx.strokeStyle = 'white';
  ctx.lineWidth = 2; // Set the line width

  // Begin the path
  ctx.beginPath();

  // Move to the first point
  ctx.moveTo(polygonPoints[0].x, polygonPoints[0].y);

  // Draw lines to each subsequent point
  for (var i = 1; i < polygonPoints.length; i++) {
      ctx.lineTo(polygonPoints[i].x, polygonPoints[i].y);
  }

  // Close the path
  ctx.closePath();

  // Stroke the path to draw the polygon
  ctx.stroke();

  // Fill the polygon with red color
  ctx.fillStyle = 'teal';
  ctx.globalAlpha = 0.6; // Set opacity to 50%
  ctx.fill();

  // Reset global alpha to default
  ctx.globalAlpha = 1.0;
  console.log(polygonPoints)
  console.log("Polygon drawn successfully");
}
