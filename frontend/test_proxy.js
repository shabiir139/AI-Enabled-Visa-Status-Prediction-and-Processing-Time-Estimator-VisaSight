const http = require('http');

const options = {
    hostname: '127.0.0.1',
    port: 8000,
    path: '/health',
    method: 'GET'
};

console.log('Testing connection to http://127.0.0.1:8000/health...');

const req = http.request(options, (res) => {
    console.log(`STATUS: ${res.statusCode}`);
    res.setEncoding('utf8');
    res.on('data', (chunk) => {
        console.log(`BODY: ${chunk}`);
    });
});

req.on('error', (e) => {
    console.error(`PROBLEM WITH REQUEST: ${e.message}`);
});

req.end();
