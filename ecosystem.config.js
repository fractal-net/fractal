module.exports = {
    apps: [
        {
            name: 'redis-server',
            script: 'redis-server',
            args: "/etc/redis/redis.conf"
        },
        {
            name: 'server',
            script: 'python',
            interpreter: 'none',
            args: 'model/server.py',
        },
        {
            name: 'neurons-verifier',
            script: 'python',
            interpreter: 'none',
            args: 'neurons/verifier/app.py --subtensor.network test --neuron.model_endpoint "http://127.0.0.1:5004" --logging.debug --logging.trace --database.password YOUR_PASSWORD_HERE --disable_auto_update --netuid 79 --axon.port 5005 --axon.external_port 11333 --neuron.sample_size 3'
        }
    ]
};
