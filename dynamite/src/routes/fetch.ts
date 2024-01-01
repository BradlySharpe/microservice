import { Request, Response, Router } from 'express';
import { DynamiteController } from '../controllers/DynamiteController';

export class Fetch {

    public static getRoutes(): Router {
        const router = Router();

        router.get("/", Fetch.get);

        return router;
    }

    public static async get(req: Request, res: Response) {
        try {
            res
                .status(200)
                .json({
                    error: null,
                    data: await DynamiteController.getJobs()
                })
                ;
        } catch (ex) {
            console.error("Failed to fetch jobs", ex);
            res
                .status(500)
                .json({
                    error: "An unknown error occurred",
                    data: null
                })
                ;
        }
    }
}