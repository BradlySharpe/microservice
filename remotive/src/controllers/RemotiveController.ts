import { Request, Response, Router } from 'express';
import { RedisClientType, RedisFunctions, RedisModules, RedisScripts, createClient } from 'redis';
import axios, { AxiosResponse } from 'axios';
import { RemotiveResponse } from '../classes/RemotiveResponse';
import { IRemotiveResponse } from '../interfaces/IRemoteiveResponse';

const REMOTIVE_ENDPOINT = process.env.ENDPOINT_API;

const REDIS_KEY = process.env.CACHE_REDIS_KEY;
const REDIS_EXPIRY_SECONDS = parseInt(process.env.REDIS_EXPIRY_SECONDS, 10);

type RedisClient = RedisClientType<RedisModules, RedisFunctions, RedisScripts>;

export class RemotiveController {
    private static async getRedisClient(): Promise<RedisClient> {
        const redisPort = process.env.REDIS_PORT || 6379;
        const client = createClient({ url: `redis://redis:${redisPort}` });
        await client.connect();
        return client;
    }

    private static async checkCache(): Promise<RemotiveResponse> {
        console.log('Fetching jobs from cache');
        try {
            const client = await RemotiveController.getRedisClient();
            try {
                const cachedJson = await client.get(REDIS_KEY);

                if (cachedJson != null)
                    return new RemotiveResponse(JSON.parse(cachedJson));
            } catch (ex) {
                console.error("An error occurred retreiving the cached jobs", ex);
                if (client != null && client.isOpen)
                    await client.disconnect();
            }
        } catch (ex) {
            console.error("Unable to connect to redis", ex);
        }

        return null;
    }

    private static async setCache(value: IRemotiveResponse) {
        console.log('Updating cached jobs');
        try {
            const client = await RemotiveController.getRedisClient();
            try {
                await client.set(REDIS_KEY, JSON.stringify(value), { EX: REDIS_EXPIRY_SECONDS });
            } catch (ex) {
                console.error("An error occurred updating the cached jobs", ex);
                if (client != null && client.isOpen)
                    await client.disconnect();
            }
        } catch (ex) {
            console.error("Unable to connect to redis", ex);
        }

        return null;
    }

    public static async fetchRemotiveJobs(updateCache = true): Promise<RemotiveResponse> {
        console.log('Fetching jobs from Remotive');
        const response: AxiosResponse<IRemotiveResponse> = await axios.get(`${REMOTIVE_ENDPOINT}`);
        const remotiveJobs = new RemotiveResponse(response.data);

        console.log(`Got ${remotiveJobs.jobCount} job(s)`);

        if (updateCache)
            await RemotiveController.setCache(response.data);

        return remotiveJobs;
    }

    public static async getJobs(): Promise<RemotiveResponse> {
        console.log('Fetching jobs');
        let remotiveJobs = await RemotiveController.checkCache();
        
        if (remotiveJobs != null) {
            console.log(`Got ${remotiveJobs.jobCount} cached job(s)`);
            return remotiveJobs;
        }

        return await RemotiveController.fetchRemotiveJobs();
    }
}