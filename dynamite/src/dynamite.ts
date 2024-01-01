import express from 'express';
import amqp from 'amqplib';
import { Fetch } from './routes/fetch';
import { Jobs } from './queues/jobs';

const REQUIRED_ENV_VARS = [
    { key: "API_PORT", type: "number" },
    { key: "ENDPOINT_API", type: "string" },
    { key: "DYNAMITE_POST_BODY", type: "string" },
    { key: "CACHE_REDIS_KEY", type: "string" },
    { key: "REDIS_EXPIRY_SECONDS", type: "number" },
    { key: "QUEUE_JOBS", type: "string" },
]

function ensureEnvironmentVariablesAreConfigured() {
    const errors = [];

    for (let index = 0; index < REQUIRED_ENV_VARS.length; index++) {
        const variable = REQUIRED_ENV_VARS[index];
        
        if (!Object.prototype.hasOwnProperty.call(process.env, variable.key)) {
            errors.push(`  - ${variable.key} is not configured`);
            continue;
        }

        const value = process.env[variable.key];

        switch (variable.type) {
            case "string":
                if (value == null || value.trim().length <= 0)
                    errors.push(`  - ${variable.key} is not configured`);
                break;

            case "number":
                if (value == null || value.trim().length <= 0) {
                    errors.push(`  - ${variable.key} is not configured`);
                    continue;
                }

                if (Number.isNaN(parseInt(value, 10)))
                    errors.push(`  - ${variable.key} is not set to a valid number: '${value}'`);
                break;
        
            default:
                errors.push(`  - Unknown type '${variable.type}' for variable: ${variable.key}`);
                break;
        }
    }

    if (errors.length > 0)
        throw new Error(`Unable to start as the following environment variables are not configured appropriately:\n${errors.join("\n")}`);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function createApi() {
    const api = express();
    api.use('/fetch', Fetch.getRoutes());
    api.listen(process.env.API_PORT);
}

async function getRabbitMqConnection() {
    let connection = null;

    while (connection == null) {
        try {
            connection = await amqp.connect('amqp://rabbitmq');
        } catch {
            console.error("Error connecting to RabbitMQ - waiting for service to start");
            await sleep(2000);
        }
    }

    return connection;
}

async function createQueueListener() {
    const connection = await getRabbitMqConnection();
    await Jobs.createQueueListener(connection);
}

async function init() {
    ensureEnvironmentVariablesAreConfigured();
    createApi();
    await createQueueListener();
}

init()
    .then(() => console.log("Dynamite running"))
    .catch((ex) => {
        console.error("Error starting Dynamite", ex);
        // Ensure the process quits fully so it will be restarted by docker
        process.exit(-1);
    })
    ;