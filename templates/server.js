const express = require('express');
const { exec } = require('child_process');

const app = express();

// Endpoint to execute the Python script
app.get('/runPythonScript', (req, res) => {
    exec('python run.py', (error, stdout, stderr) => {
        if (error) {
            res.status(500).send(`Error: ${error.message}`);
            return;
        }
        if (stderr) {
            res.status(500).send(`stderr: ${stderr}`);
            return;
        }
        res.send(`stdout: ${stdout}`);
    });
});

// Start the server
app.listen(3000, () => {
    console.log('Server is running on port 3000');
});
