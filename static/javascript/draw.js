

function handleMouseDown(event) {
            var x = event.clientX - canvas.getBoundingClientRect().left;
            var y = event.clientY - canvas.getBoundingClientRect().top;

            for (var i = bounding_boxes.length - 1; i >= 0; i--) {
              var bbox = bounding_boxes[i];

              if (
                x >= bbox.x &&
                x <= bbox.x + bbox.width &&
                y >= bbox.y &&
                y <= bbox.y + bbox.height
              ) {
                var handle = getResizeHandle(x, y, bbox);
                if (handle !== -1) {
                  isResizing = true;
                  selectedBox = bbox;
                  selectedHandle = handle;
                } else {
                  isDragging = true;
                  selectedBox = bbox;
                  offset.x = x - bbox.x;
                  offset.y = y - bbox.y;
                }
                return;
              }
            }
          }

          function handleMouseMove(event) {
            var x = event.clientX - canvas.getBoundingClientRect().left;
            var y = event.clientY - canvas.getBoundingClientRect().top;
            
            var resizeHandleCursor = getResizeHandleCursor(x, y);
            

            if (isDragging) {
              selectedBox.x = x - offset.x;
              selectedBox.y = y - offset.y;

              drawBoundingBoxes();
            }

            if (isResizing) {
              var newWidth = x - selectedBox.x;
              var newHeight = y - selectedBox.y;

              switch (selectedHandle) {
                case 0: // Top-left corner
                  selectedBox.x = x;
                  selectedBox.y = y;
                  selectedBox.width -= newWidth;
                  selectedBox.height -= newHeight;
                  break;
                case 1: // Top-right corner
                  selectedBox.y = y;
                  selectedBox.width = newWidth;
                  selectedBox.height -= newHeight;
                  break;
                case 2: // Bottom-left corner
                  selectedBox.x = x;
                  selectedBox.width -= newWidth;
                  selectedBox.height = newHeight;
                  break;
                case 3: // Bottom-right corner
                  selectedBox.width = newWidth;
                  selectedBox.height = newHeight;
                  break;
                case 4: // Top-center handle
                  selectedBox.y = y;
                  selectedBox.height -= newHeight;
                  break;
                case 5: // Bottom-center handle
                  selectedBox.height = newHeight;
                  break;
                case 6: // Middle-right handle
                  selectedBox.width = newWidth;
                  break;
                case 7: // Middle-left handle
                  selectedBox.x = x;
                  selectedBox.width -= newWidth;
                  break;
                

              }

              drawBoundingBoxes();
            }
            if (resizeHandleCursor) {
              canvas.style.cursor = resizeHandleCursor;
            } else if (isDragging) {
              canvas.style.cursor = 'move';
            } else {
              canvas.style.cursor = 'default';
            }
          }

          function handleMouseUp() {
            isDragging = false;
            isResizing = false;
            selectedBox = null;
            selectedHandle = null;
          }

          function getResizeHandle(x, y, bbox) {
            var resizeHandlesSize = 50;
          
            // Top-left corner
            if (
              x >= bbox.x - resizeHandlesSize / 2 && 
              x <= bbox.x + resizeHandlesSize / 2 &&
              y >= bbox.y - resizeHandlesSize / 2 && 
              y <= bbox.y + resizeHandlesSize / 2
            ) {
              return 0;
            }
            // Top-right corner
            else if (
              x >= bbox.x + bbox.width - resizeHandlesSize / 10 &&
              x <= bbox.x + bbox.width + resizeHandlesSize / 10 &&
              y >= bbox.y - resizeHandlesSize / 10 && 
              y <= bbox.y + resizeHandlesSize / 10
            ) {
              return 1;
            }
            // Bottom-left corner
            else if (
              x >= bbox.x - resizeHandlesSize / 2 && 
              x <= bbox.x + resizeHandlesSize / 2 &&
              y >= bbox.y + bbox.height - resizeHandlesSize / 2 && 
              y <= bbox.y + bbox.height + resizeHandlesSize / 2
            ) {
              return 2;
            }
            // Bottom-right corner
            else if (
              x >= bbox.x + bbox.width - resizeHandlesSize / 2 && 
              x <= bbox.x + bbox.width + resizeHandlesSize / 2 &&
              y >= bbox.y + bbox.height - resizeHandlesSize / 2 && 
              y <= bbox.y + bbox.height + resizeHandlesSize / 2
            ) {
              return 3;
            }
            // Top-center handle
            else if (
              x >= bbox.x + bbox.width / 2 - resizeHandlesSize / 2 && 
              x <= bbox.x + bbox.width / 2 + resizeHandlesSize / 2 &&
              y >= bbox.y - resizeHandlesSize / 2 && 
              y <= bbox.y + resizeHandlesSize / 2
            ) {
              return 4;
            }
            // Bottom-center handle
            else if (
              x >= bbox.x + bbox.width / 2 - resizeHandlesSize / 2 && 
              x <= bbox.x + bbox.width / 2 + resizeHandlesSize / 2 &&
              y >= bbox.y + bbox.height - resizeHandlesSize / 2 && 
              y <= bbox.y + bbox.height + resizeHandlesSize / 2
            ) {
              return 5;
            }
            // Middle-right handle
            else if (
              x >= bbox.x + bbox.width - resizeHandlesSize / 2 && 
              x <= bbox.x + bbox.width + resizeHandlesSize / 2 &&
              y >= bbox.y + bbox.height / 2 - resizeHandlesSize / 2 && 
              y <= bbox.y + bbox.height / 2 + resizeHandlesSize / 2
            ) {
              return 6;
            }
            // Middle-left handle
            else if (
              x >= bbox.x - resizeHandlesSize / 2 && 
              x <= bbox.x + resizeHandlesSize / 2 &&
              y >= bbox.y + bbox.height / 2 - resizeHandlesSize / 2 && 
              y <= bbox.y + bbox.height / 2 + resizeHandlesSize / 2
            ) {
              return 7;
            }
          
            return -1; // No resize handle found
          }
          
          
          function getResizeHandleCursor(x, y) {
            var resizeHandlesSize =5;
          
            for (var i = bounding_boxes.length - 1; i >= 0; i--) {
              var bbox = bounding_boxes[i];
          
              if (
                x > bbox.x - resizeHandlesSize / 2 && x < bbox.x + resizeHandlesSize / 2 &&
                y > bbox.y - resizeHandlesSize / 2 && y < bbox.y + resizeHandlesSize / 2
              ) {
                return 'nwse-resize'; // Top-left corner
              } else if (
                x > bbox.x + bbox.width / 2 - resizeHandlesSize / 2 && x < bbox.x + bbox.width / 2 + resizeHandlesSize / 2 &&
                y > bbox.y - resizeHandlesSize / 2 && y < bbox.y + resizeHandlesSize / 2
              ) {
                return 'ns-resize'; // Top-center handle
              } else if (
                x > bbox.x + bbox.width - resizeHandlesSize / 2 && x < bbox.x + bbox.width + resizeHandlesSize / 2 &&
                y > bbox.y - resizeHandlesSize / 2 && y < bbox.y + resizeHandlesSize / 2
              ) {
                return 'nesw-resize'; // Top-right corner
              } else if (
                x > bbox.x - resizeHandlesSize / 2 && x < bbox.x + resizeHandlesSize / 2 &&
                y > bbox.y + bbox.height / 2 - resizeHandlesSize / 2 && y < bbox.y + bbox.height / 2 + resizeHandlesSize / 2
              ) {
                return 'ew-resize'; // Middle-left handle
              } else if (
                x > bbox.x + bbox.width - resizeHandlesSize / 2 && x < bbox.x + bbox.width + resizeHandlesSize / 2 &&
                y > bbox.y + bbox.height / 2 - resizeHandlesSize / 2 && y < bbox.y + bbox.height / 2 + resizeHandlesSize / 2
              ) {
                return 'ew-resize'; // Middle-right handle
              } else if (
                x > bbox.x - resizeHandlesSize / 2 && x < bbox.x + resizeHandlesSize / 2 &&
                y > bbox.y + bbox.height - resizeHandlesSize / 2 && y < bbox.y + bbox.height + resizeHandlesSize / 2
              ) {
                return 'nesw-resize'; // Bottom-left corner
              } else if (
                x > bbox.x + bbox.width / 2 - resizeHandlesSize / 2 && x < bbox.x + bbox.width / 2 + resizeHandlesSize / 2 &&
                y > bbox.y + bbox.height - resizeHandlesSize / 2 && y < bbox.y + bbox.height + resizeHandlesSize / 2
              ) {
                return 'ns-resize'; // Bottom-center handle
              } else if (
                x > bbox.x + bbox.width - resizeHandlesSize / 2 && x < bbox.x + bbox.width + resizeHandlesSize / 2 &&
                y > bbox.y + bbox.height - resizeHandlesSize / 2 && y < bbox.y + bbox.height + resizeHandlesSize / 2
              ) {
                return 'nwse-resize'; // Bottom-right corner
              }
            }
          
            return null; // No resize handle found
          }
          
          function isDrawingActivated() {
            var drawButton = document.querySelector('.draw-button');
            return drawButton.classList.contains('active');
          }
          
          function toggleDrawing() {
            var drawButton = document.querySelector('.draw-button');
            drawButton.classList.toggle('active');
          
            if (drawButton.classList.contains('active')) {
              activateDrawing();
              drawButton.style.backgroundColor = 'green';
            } else {
              deactivateDrawing();
              drawButton.style.backgroundColor = ''; 
            }
          }
          
          function activateDrawing() {
            drawingEnabled = true;
            canvas.style.cursor = 'crosshair';
            canvas.addEventListener('mousedown', startDrawing);
            canvas.removeEventListener('mousedown', handleMouseDown);
          }
          
          function deactivateDrawing() {
            drawingEnabled = false;
            canvas.style.cursor = 'default';
            canvas.removeEventListener('mousedown', startDrawing);
            canvas.addEventListener('mousedown', handleMouseDown);
          }
