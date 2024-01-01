import { RedisClientType, RedisFunctions, RedisModules, RedisScripts, createClient } from 'redis';
import axios, { AxiosResponse } from 'axios';
import { IDynamiteResponse } from '../interfaces/IDynamiteResponse';
import { DynamiteResponse } from '../classes/DynamiteResponse';

const DYNAMITE_ENDPOINT = process.env.ENDPOINT_API;
const DYNAMITE_POST_BODY = process.env.DYNAMITE_POST_BODY;

const REDIS_KEY = process.env.CACHE_REDIS_KEY;
const REDIS_EXPIRY_SECONDS = parseInt(process.env.REDIS_EXPIRY_SECONDS, 10);

type RedisClient = RedisClientType<RedisModules, RedisFunctions, RedisScripts>;

export class DynamiteController {
    private static async getRedisClient(): Promise<RedisClient> {
        const redisPort = process.env.REDIS_PORT || 6379;
        const client = createClient({ url: `redis://redis:${redisPort}` });
        await client.connect();
        return client;
    }

    private static async checkCache(): Promise<DynamiteResponse> {
        console.log('Fetching jobs from cache');
        try {
            const client = await DynamiteController.getRedisClient();
            try {
                const cachedJson = await client.get(REDIS_KEY);

                if (cachedJson != null)
                    return new DynamiteResponse(JSON.parse(cachedJson));
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

    private static async setCache(value: IDynamiteResponse) {
        console.log('Updating cached jobs');
        try {
            const client = await DynamiteController.getRedisClient();
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

    public static async fetchDynamiteJobs(updateCache = true): Promise<DynamiteResponse> {
        console.log('Fetching jobs from Dynamite');
        const response: AxiosResponse<IDynamiteResponse> = await axios.post(DYNAMITE_ENDPOINT, DYNAMITE_POST_BODY, { headers: { "Content-Type": "application/x-www-form-urlencoded" } });
        const dynamiteJobs = new DynamiteResponse(response.data);

        console.log(`Got ${dynamiteJobs.jobCount} job(s)`);

        if (updateCache)
            await DynamiteController.setCache(response.data);

        return dynamiteJobs;
    }

    public static async getJobs(): Promise<DynamiteResponse> {
        console.log('Fetching jobs');
        let dynamiteJobs = await DynamiteController.checkCache();
        
        if (dynamiteJobs != null) {
            console.log(`Got ${dynamiteJobs.jobCount} cached job(s)`);
            return dynamiteJobs;
        }

        return await DynamiteController.fetchDynamiteJobs();
    }
}