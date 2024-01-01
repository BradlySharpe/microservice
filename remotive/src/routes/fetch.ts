import { Request, Response, Router } from 'express';
import { RemotiveController } from '../controllers/RemotiveController';

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
                    mapper: "remotive",
                    data: await RemotiveController.getJobs()
                })
                ;
        } catch (ex) {
            console.error("Failed to fetch jobs", ex);
            res
                .status(500)
                .json({
                    error: "An unknown error occurred",
                    mapper: "remotive",
                    data: null
                })
                ;
        }
    }
}