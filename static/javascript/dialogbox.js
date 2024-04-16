  function showCustomDialog(newBox) {
            var dialog = document.createElement('div');
            dialog.classList.add('custom-dialog');
        
            var dialogContent = document.createElement('div');
            dialogContent.classList.add('dialog-content');
        
            var label = document.createElement('label');
            label.setAttribute('for', 'box-label');
            label.textContent = 'Label:';
        
            var input = document.createElement('input');
            input.setAttribute('type', 'text');
            input.setAttribute('id', 'box-label');
            input.setAttribute('placeholder', 'Enter Label');
        
            var errorMessage = document.createElement('div');
            errorMessage.style.color = 'white';
            errorMessage.style.display = 'none';
            errorMessage.style.marginTop = '5px';
        
            dialogContent.appendChild(label);
            dialogContent.appendChild(input);
            dialogContent.appendChild(errorMessage);
        
            var closeButton = document.createElement('button');
            closeButton.textContent = 'Close';
            closeButton.style.backgroundColor = 'black';
            closeButton.style.color = 'white';
            closeButton.style.border = 'none';
            closeButton.style.borderRadius = '10px';
            closeButton.style.cursor = 'pointer';
            closeButton.style.padding = '5px 10px';
            closeButton.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.6)';
            closeButton.style.marginRight = '10px'; // Add margin for spacing
        
            closeButton.addEventListener('click', function () {
                removeCustomDialog();
            });
        
            dialogContent.appendChild(closeButton);
        
            var button = document.createElement('button');
            button.textContent = 'OK';
            button.style.backgroundColor = 'black';
            button.style.color = 'white';
            button.style.border = 'none';
            button.style.borderRadius = '10px';
            button.style.cursor = 'pointer';
            button.style.padding = '5px 10px';
            button.style.boxShadow = '0 2px 5px rgba(0, 0, 0, 0.6)';
        
            dialogContent.appendChild(button);
            dialog.appendChild(dialogContent);
        
            document.body.appendChild(dialog);
        
            button.addEventListener('click', function () {
                var labelValue = input.value.trim();
        
                if (labelValue !== "") {
                    newBox.label = labelValue;
                    drawBoundingBoxes();
                    removeCustomDialog();
                } else {
                    errorMessage.textContent = "Label field is required.";
                    errorMessage.style.display = 'block';
        
                    setTimeout(function () {
                        errorMessage.style.display = 'none';
                    }, 2000);
                }
            });
        }
        
          function removeCustomDialog() {
              var dialog = document.querySelector('.custom-dialog');
              if (dialog) {
                  dialog.parentNode.removeChild(dialog);
              }
          }
