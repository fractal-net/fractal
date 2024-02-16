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
            name: 'neurons-prover',
            script: 'python',
            interpreter: 'none',
            args: 'neurons/prover/app.py --subtensor.network finney --neuron.model_endpoint "http://127.0.0.1:<SERVER_PORT_HERE>" --logging.debug --logging.trace --netuid 29 --axon.port <YOUR_INTERNAL_PORT> --axon.external_port <YOUR_EXTERNAL_PORT> --wallet.name <YOUR_WALLET_NAME> --wallet.hotkey <YOUR_WALLET_HOTKEY>'
        },
        // {
        //     name: 'neurons-verifier',
        //         script: 'python',
        //         interpreter: 'none',
        //         args: 'neurons/verifier/app.py --subtensor.network finney --neuron.model_endpoint "http://127.0.0.1:<SERVER_PORT_HERE>" --logging.debug --logging.trace --database.password <YOUR_PASSWORD_HERE> --netuid 29 --axon.port <YOUR_INTERNAL_PORT> --axon.external_port <YOUR_EXTERNAL_PORT> --wallet.name <YOUR_WALLET_NAME> --wallet.hotkey <YOUR_WALLET_HOTKEY>''
        // }
    ]
};
